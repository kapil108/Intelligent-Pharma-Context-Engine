import requests
from rapidfuzz import process, fuzz

class RxNormClient:
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"

    def normalize_name(self, name):
        """Use RxNorm API to normalize a drug name."""
        try:
            url = f"{self.BASE_URL}/approximateTerm.json?term={name}&maxEntries=1"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get("approximateGroup", {}).get("candidate", [])
            if candidates:
                # Return the best match RXCUI and Name
                best = candidates[0]
                return {
                    "name": best.get("name"),  # Fixed: was 'rxcuiName', actual field is 'name'
                    "rxcui": best.get("rxcui"),
                    "score": best.get("score")
                }
        except Exception as e:
            print(f"RxNorm lookup failed for {name}: {e}")
        
        return None

    def fuzzy_match_local(self, query, choices, limit=3):
        """Local fuzzy matching utility."""
        return process.extract(query, choices, scorer=fuzz.WRatio, limit=limit)

if __name__ == "__main__":
    # Quick Test
    client = RxNormClient()
    result = client.normalize_name("Lisinopri1")
    print(f"Result for 'Lisinopri1': {result}")
