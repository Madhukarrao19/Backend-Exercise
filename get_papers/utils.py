import pandas as pd
from typing import List, Dict, Any

def save_to_csv(data: List[Dict[str, Any]], filename: str = "output.csv", debug: bool = False) -> None:
    if not data:
        print("No data to save.") if debug else None
        return

    try:
        print("Creating DataFrame...") if debug else None
        df = pd.DataFrame(data, columns=[
            "PubmedID", "Title", "Publication Date", "Non-Academic Authors", "Company Affiliations", "Corresponding Author Email"
        ])
        print("Saving DataFrame to CSV...") if debug else None
        df.to_csv(filename, index=False)
        print(f"CSV saved to {filename}") if debug else None
    except Exception as e:
        print(f"Error saving CSV: {e}")