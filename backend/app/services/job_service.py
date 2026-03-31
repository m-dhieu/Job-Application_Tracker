import requests
import logging

logger = logging.getLogger(__name__)

def fetch_jobs(limit: int, offset: int):
    """
    Calls the external Himalayas jobs API to fetch job listings with error handling and timeout.
    """
    url = f"https://himalayas.app/jobs/api/?limit={limit}&offset={offset}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("jobs", [])
    except requests.exceptions.RequestException as e:
        # Raise a RuntimeError with details for the caller to catch and log
        logger.error(f"Himalayas job API request failed: {e}")
        raise RuntimeError(f"Himalayas job API request failed: {e}")
