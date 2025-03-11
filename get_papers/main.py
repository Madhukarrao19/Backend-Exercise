import sys
import os
import argparse
from typing import List, Dict, Any
import requests
import json

# Add the project root folder to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_papers.pubmed_api import fetch_papers
from get_papers.utils import save_to_csv

debug = False

def process_papers(papers_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process the fetched papers and filter for non-academic authors and company affiliations"""
    processed_papers = []
    if papers_json and 'esearchresult' in papers_json and 'idlist' in papers_json['esearchresult']:
        ids = papers_json['esearchresult']['idlist']
        if ids:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "rettype": "medline",
                "retmode": "text"
            }
            response = requests.get(base_url, params=params)
            records = response.text.split("\n\n")
            for record in records:
                paper = parse_medline_record(record)
                if paper:
                    processed_papers.append(paper)
    return processed_papers

def parse_medline_record(record: str) -> Dict[str, Any]:
    lines = record.split("\n")
    paper = {"Non-Academic Authors": set(), "Company Affiliations": set(), "Corresponding Author Email": ""}

    for line in lines:
        if line.startswith("PMID-"):
            paper["PubmedID"] = line.split("-")[1].strip()
        elif line.startswith("TI  -"):
            paper["Title"] = line.split("-")[1].strip()
        elif line.startswith("DP  -"):
            paper["Publication Date"] = line.split("-")[1].strip()
        elif line.startswith("AU  -"):
            author = line.split("-")[1].strip()
            if is_non_academic_author(author):
                paper["Non-Academic Authors"].add(author)
        elif line.startswith("AD  -"):
            affiliation = line.split("-")[1].strip()
            if is_pharma_biotech_affiliation(affiliation):
                paper["Company Affiliations"].add(affiliation)
        elif line.startswith("EM  -"):
            paper["Corresponding Author Email"] = line.split("-")[1].strip()

    if paper["Non-Academic Authors"] and paper["Company Affiliations"]:
        paper["Non-Academic Authors"] = list(paper["Non-Academic Authors"])
        paper["Company Affiliations"] = list(paper["Company Affiliations"])
        return paper
    return None

def is_non_academic_author(author: str) -> bool:
    # Heuristic: Assume non-academic if no university or similar institution in the name
    return not any(word in author.lower() for word in ["university", "college", "institute", "dept"])

def is_pharma_biotech_affiliation(affiliation: str) -> bool:
    # Heuristic: Assume pharma/biotech if certain keywords are present
    keywords = ["pharma", "biotech", "laboratories", "inc", "corp"]
    return any(keyword in affiliation.lower() for keyword in keywords)

def main(query: str, output_file: str = None) -> None:
    global debug
    print("Fetching papers...") if debug else None
    papers_json = fetch_papers(query, debug)
    print("Papers fetched:", json.dumps(papers_json, indent=2)) if debug else None

    if not papers_json:
        print("No papers found or an error occurred while fetching papers.")
        return

    processed_papers = process_papers(papers_json)
    print("Processed papers:", json.dumps(processed_papers, indent=2)) if debug else None

    if not processed_papers:
        print("No papers with non-academic authors and company affiliations found.")
        return

    if output_file:
        print("Saving results to CSV...") if debug else None
        save_to_csv(processed_papers, output_file, debug)
        print(f"Results saved to {output_file}") if debug else None
    else:
        print("Results:", json.dumps(processed_papers, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", help="Search query for PubMed.")
    parser.add_argument("-f", "--file", help="Output CSV file name.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output.")
    args = parser.parse_args()
    debug = args.debug
    main(args.query, args.file)