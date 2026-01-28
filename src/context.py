import pandas as pd
import json
import os
from thefuzz import process, fuzz

class PharmaBrain:
    def __init__(self, rxnorm_path, openfda_dir):
        # Load the "Source of Truth" (RxNorm)
        if os.path.exists(rxnorm_path):
            self.rxnorm_db = pd.read_csv(rxnorm_path)
            self.valid_drugs = self.rxnorm_db['drug_name'].dropna().unique().tolist()
        else:
            print(f"Warning: RxNorm DB not found at {rxnorm_path}. Using fallback list.")
            self.valid_drugs = ["Lisinopril", "Metformin", "Ibuprofen", "Atorvastatin", "Amoxicillin", "Sertraline"]
        
        self.openfda_dir = openfda_dir

    def fuzzy_match_drug(self, extracted_lines):
        """
        Scans all OCR lines to find a drug name.
        Returns: (Corrected Name, Confidence Score)
        """
        best_match = None
        highest_score = 0

        for line in extracted_lines:
            # Skip tiny words
            if len(line) < 4: continue
            
            # Fuzzy match against database
            match, score = process.extractOne(line, self.valid_drugs, scorer=fuzz.token_sort_ratio)
            
            if score > highest_score:
                highest_score = score
                best_match = match

        # Only accept if we are >80% sure it's a drug name
        if highest_score > 80:
            return best_match, highest_score
        return None, 0

    def get_enrichment(self, drug_name):
        """
        Mockup: Searches OpenFDA JSON for the drug name.
        (Real implementation requires parsing the massive JSON dump properly)
        """
        # In a real scenario, you'd query a local SQLite or ElasticSearch instance
        # For this prototype, we return a standard safety string based on the match.
        return {
            "source": "OpenFDA",
            "drug": drug_name,
            "warning": "Keep out of reach of children.",
            "storage": "Store at 20°C to 25°C (68°F to 77°F)."
        }
