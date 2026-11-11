"""Synthetic support agent demo. No production services or customer data."""

import os

# Local scans never load model providers or datasets from the environment.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
