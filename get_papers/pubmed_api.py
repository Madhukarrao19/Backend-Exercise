import requests
from typing import Dict, Any

def fetch_papers(query: str, debug: bool = False) -> Dict[str, Any]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 10  # Fetch 10 papers for testing
    }
    try:
        print("Making API request...") if debug else None
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        print("API request successful.") if debug else None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from PubMed API: {e}")
        return None