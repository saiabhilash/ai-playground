import logging

import requests
import streamlit as st

from support_demo.agent import SupportAgent
from support_demo.models import LocalModel
from support_demo.scenarios import select_scenarios


def render_result(result: dict) -> None:
    if result["status"] == "denied":
        st.warning(result["reason"])
    elif result["status"] == "help":
        st.write(result["message"])
    elif "refunded_cents" in result:
        st.success(
            f"Refund recorded: ${result['refunded_cents'] / 100:.2f} "
            f"on {result['order_id']}."
        )
        st.caption(result["message"])
    else:
        st.success(f"Order details: {result['order_id']}")
        st.write(f"**Order value:** ${result['total_cents'] / 100:.2f}")
        st.write(f"**Delivery code:** `{result['delivery_code']}`")


def main() -> None:
    st.set_page_config(page_title="Local Support Chat", layout="centered")
    st.title("Local Support Chat")
    st.caption("An Ollama-powered support assistant. Synthetic orders, no real payments.")

    with st.sidebar:
        st.header("Local demo")
        model_name = st.text_input("Ollama model", value="qwen2.5-coder:1.5b").strip()
        st.caption("Inference stays on 127.0.0.1:11434. No cloud API calls.")
        st.caption("Changing the model or starting a new chat resets this synthetic session.")
        new_chat = st.button("New chat", use_container_width=True)

    if not model_name:
        st.error("Enter an installed Ollama model name.")
        st.stop()

    configuration = ("baseline", model_name)
    if new_chat or st.session_state.get("configuration") != configuration:
        st.session_state.configuration = configuration
        st.session_state.local_model = LocalModel(model_name)
        st.session_state.agent = SupportAgent(
            "baseline",
            planner=st.session_state.local_model,
        )
        st.session_state.messages = [{
            "role": "assistant",
            "text": "Hello! I can check your orders or record a simulated refund. How can I help?",
        }]

    agent = st.session_state.agent
    with st.sidebar:
        st.divider()
        st.write(f"**Demo identity:** `{agent.session.tenant_id}`")
        st.caption("Fixed server-created identity; this demo has no production login.")
        refunded = sum(agent.refunded.values())
        st.metric("Refunded this session", f"${refunded / 100:.2f}")
        st.metric("Policy allowance remaining (not enforced)", f"${(agent.session.refund_budget_cents - refunded) / 100:.2f}")
        st.caption("A new demo session is not a way to reset a real financial allowance.")

    with st.expander("Demo scenarios: refund limits, order privacy, and forged approval"):
        st.caption("Start a new chat before each scenario so refund totals are independent.")
        for scenario in select_scenarios(suite="demo"):
            st.write(f"**{scenario.id}:** {scenario.objective}")
            for turn, example in enumerate(scenario.prompts, start=1):
                st.code(f"{turn}. {example}", language=None)
        st.caption(
            "These are manual chat examples, not PyRIT results. "
            "Run the PyRIT lab with --suite demo to save scored tool evidence."
        )
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "error" in message:
                st.error(message["error"])
            elif "result" in message:
                render_result(message["result"])
                if any(event["policy_violation"] for event in message["audit"]):
                    st.error("Local tool audit flagged a policy violation (not a PyRIT run).")
                with st.expander("Tool execution details"):
                    st.json({"output": message["result"], "audit": message["audit"]})
            else:
                st.write(message["text"])

    if prompt := st.chat_input("Ask about an order or request a refund"):
        st.session_state.messages.append({"role": "user", "text": prompt})
        audit_start = len(agent.audit)
        try:
            with st.spinner("Asking the local model..."):
                st.session_state.local_model.check_available()
                result = agent.respond(prompt)
        except (requests.RequestException, ValueError, RuntimeError, OSError, TypeError) as error:
            logging.exception("Local support chat request failed")
            st.session_state.messages.append({
                "role": "assistant",
                "error": f"Local request failed: {error}. Check Ollama and the selected model.",
            })
        else:
            st.session_state.messages.append({
                "role": "assistant", "result": result, "audit": agent.audit[audit_start:],
            })
        st.rerun()


if __name__ == "__main__":
    main()
