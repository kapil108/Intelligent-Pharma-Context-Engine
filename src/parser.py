import re

class LabelParser:
    def __init__(self):
        # Common manufacturers for lookup
        self.manufacturers = [
            "PFIZER", "MYLAN", "TEVA", "NOVARTIS", "SANOFI", "GSK", "MERCK", "GLAXOSMITHKLINE",
            "ASTRAZENECA", "JOHNSON & JOHNSON", "ROCHE", "ABBVIE", "AMGEN", "GILEAD", 
            "BRISTOL-MYERS SQUIBB", "ELI LILLY", "BAYER", "SUN PHARMA", "LUPIN", "CIPLA",
            "AUROBINDO", "DR. REDDY'S", "ZYDUS", "HIKMA", "PERRIGO", "APOTEX", "JANSSEN"
        ]
        
    def parse(self, text_lines):
        """
        Parses raw OCR lines to extract structured entities.
        Returns: {
            "dosage": "10mg", 
            "manufacturer": "Pfizer", 
            "composition": "Atorvastatin Calcium",
            "quantity": "100 Tablets"
        }
        """
        full_text = " ".join(text_lines).upper()
        
        entities = {
            "dosage": None,
            "manufacturer": None,
            "composition": None,
            "quantity": None
        }
        
        # 1. DOSAGE
        # Patterns: "10mg", "350 mg / 7 ml", "50mg/ml"
        # Group 1: Leading number
        # Group 3: Leading Unit
        # Group 4: Optional "/ 5ml" part
        dosage_pattern = r"(\d+(\.\d+)?\s*(MG|G|MCG|ML|%|IU|UNITS)(\s*\/\s*\d+(\.\d+)?\s*(ML|G|MG|ACTUATION))?)"
        dosage_match = re.search(dosage_pattern, full_text)
        if dosage_match:
            entities["dosage"] = dosage_match.group(0)
            
        # 2. MANUFACTURER
        # Check against known list
        for mfg in self.manufacturers:
            if mfg in full_text:
                entities["manufacturer"] = mfg
                break
        
        # Fallback: Look for "Mfd by", "Distributed by"
        if not entities["manufacturer"]:
            mfg_pattern = r"(MFD BY|MANUFACTURED BY|DISTRIBUTED BY)\s+([A-Z0-9\s\.]+)"
            mfg_match = re.search(mfg_pattern, full_text)
            if mfg_match:
                # Take first 3 words after the keyword
                raw_mfg = mfg_match.group(2).split()[:3]
                entities["manufacturer"] = " ".join(raw_mfg)

        # 3. QUANTITY
        # Patterns like: 100 Tablets, 30 Capsules, 200 mL
        qty_pattern = r"(\d+)\s*(TABLETS|CAPSULES|PILLS|GELS|CAPLETS|ML|FL OZ)"
        qty_match = re.search(qty_pattern, full_text)
        if qty_match:
            entities["quantity"] = qty_match.group(0)

        # 4. COMPOSITION (Heuristic)
        # Often the line *before* the dosage, or the longest word ending in -IDE, -INE, -ATE
        # For MVP, we will try to find chemical names if not found by basic lookup
        # This is tough without NER. We'll leave it as None or try a basic heuristic later.
        
        return entities

if __name__ == "__main__":
    parser = LabelParser()
    sample = ["Atorvastatin Calcium", "Tablets, USP", "10 mg", "Manufactured by: Pfizer"]
    print(parser.parse(sample))
