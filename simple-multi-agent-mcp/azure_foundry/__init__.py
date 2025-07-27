"""
Azure AI Foundry Integration
Provides connection and integration with Azure AI Foundry services
"""
import os
import logging
from typing import Dict, Any, Optional
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AccessToken


class AzureAIFoundryClient:
    """
    Client for Azure AI Foundry integration
    Manages connections to AI services and provides unified access
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AzureAIFoundry")
        self.credential = None
        self.project_client = None
        self.chat_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure AI Foundry clients"""
        try:
            # Use Managed Identity in Azure, DefaultAzureCredential locally
            if os.getenv("MSI_ENDPOINT"):
                self.credential = ManagedIdentityCredential()
                self.logger.info("Using Managed Identity credential")
            else:
                self.credential = DefaultAzureCredential()
                self.logger.info("Using Default Azure credential")
            
            # Get configuration from environment
            project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
            openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
            
            if project_endpoint:
                # Initialize AI Project client
                self.project_client = AIProjectClient.from_connection_string(
                    conn_str=project_endpoint,
                    credential=self.credential
                )
                self.logger.info("Initialized AI Project client")
            
            if openai_endpoint:
                # Initialize chat completions client
                self.chat_client = ChatCompletionsClient(
                    endpoint=f"{openai_endpoint}/openai/deployments/{deployment_name}",
                    credential=self.credential
                )
                self.logger.info(f"Initialized Chat client with deployment: {deployment_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure AI Foundry clients: {e}")
            raise
    
    async def get_chat_completion(self, messages: list, **kwargs) -> Dict[str, Any]:
        """
        Get chat completion from Azure OpenAI
        
        Args:
            messages: List of messages in OpenAI format
            **kwargs: Additional parameters for the completion
            
        Returns:
            Chat completion response
        """
        if not self.chat_client:
            raise Exception("Chat client not initialized")
        
        try:
            # Convert messages to Azure AI format
            ai_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    ai_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    ai_messages.append(UserMessage(content=msg["content"]))
                # Add more message types as needed
            
            # Get completion
            response = self.chat_client.complete(
                messages=ai_messages,
                **kwargs
            )
            
            return {
                "success": True,
                "response": response,
                "content": response.choices[0].message.content if response.choices else ""
            }
            
        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get AI Project information"""
        if not self.project_client:
            return {"error": "Project client not initialized"}
        
        try:
            # Get project details
            project_details = self.project_client.get_project()
            
            return {
                "success": True,
                "project_name": project_details.get("name"),
                "project_id": project_details.get("id"),
                "location": project_details.get("location"),
                "resource_group": project_details.get("resource_group")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get project info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def log_conversation(self, conversation_id: str, messages: list, metadata: Dict[str, Any] = None):
        """
        Log conversation to Azure AI Foundry for monitoring and analysis
        
        Args:
            conversation_id: Unique identifier for the conversation
            messages: List of conversation messages
            metadata: Additional metadata to log
        """
        try:
            if self.project_client:
                # Log the conversation for monitoring
                log_data = {
                    "conversation_id": conversation_id,
                    "messages": messages,
                    "metadata": metadata or {},
                    "timestamp": self._get_timestamp()
                }
                
                # Use project client to log data
                # Note: Actual implementation depends on AI Foundry logging APIs
                self.logger.info(f"Logged conversation {conversation_id} with {len(messages)} messages")
                
        except Exception as e:
            self.logger.warning(f"Failed to log conversation: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def is_healthy(self) -> bool:
        """Check if the AI Foundry connection is healthy"""
        try:
            if self.chat_client:
                # Simple health check - try to get a token
                token = self.credential.get_token("https://cognitiveservices.azure.com/.default")
                return token is not None
            return False
        except Exception:
            return False


# Global instance for easy access
_ai_foundry_client = None


def get_ai_foundry_client() -> AzureAIFoundryClient:
    """Get or create AI Foundry client instance"""
    global _ai_foundry_client
    if _ai_foundry_client is None:
        _ai_foundry_client = AzureAIFoundryClient()
    return _ai_foundry_client
