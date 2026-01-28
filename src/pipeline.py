import os
import json
from .preprocess import Preprocessor
from .detect import Detector
from .ocr import OCRSystem
from .verify import Verifier
from .enrich import Enricher
from .parser import LabelParser

class PharmaPipeline:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.detector = Detector()
        self.ocr_system = OCRSystem()
        self.verifier = Verifier()
        self.enricher = Enricher()
        self.parser = LabelParser()

    def process_image(self, image_path):
        # 1. Preprocess
        img = self.preprocessor.process(image_path)
        
        # 2. Detect & OCR
        # BYPASS YOLO DETECTION - Read barcode directly from full image
        # regions = self.detector.detect_regions(img)
        text_results = self.ocr_system.read_text(img)
        barcodes = self.ocr_system.read_barcodes(img)
        
        print(f"[DEBUG] Direct barcode scan found: {len(barcodes)} barcodes")
        
        # Skipping region-based detection to test direct barcode reading
        # If no barcode found in full image, try cropping to regions
        # if not barcodes and regions:
        #     for region in regions:
        #         x1, y1, x2, y2 = region['coords']
        #         # Add some padding
        #         h, w, _ = img.shape
        #         pad = 10
        #         y1 = max(0, y1-pad)
        #         y2 = min(h, y2+pad)
        #         x1 = max(0, x1-pad)
        #         x2 = min(w, x2+pad)
        #         
        #         crop = img[y1:y2, x1:x2]
        #         if crop.size > 0:
        #             region_barcodes = self.ocr_system.read_barcodes(crop)
        #             if region_barcodes:
        #                 barcodes.extend(region_barcodes)
        #                 break # Found one, stop
        
        # Simple extraction logic (heuristic-based)
        # In production, this would use a layout model or NER
        full_text = " ".join([t[1] for t in text_results])
        
        # Naive extraction for demo:
        # We'll treat the highest confidence word as drug name for now
        # FILTERING: Exclude dates (2026, 2025), short numbers, and common invalid words
        import re
        
        def is_valid_name(text):
            text = text.strip().upper()
            if len(text) < 3: return False # Too short
            if text.isdigit(): return False # Pure numbers like 2026
            if re.match(r'^\d{4}$', text): return False # Year pattern
            if re.match(r'^(EXP|LOT|BATCH|MFG).*', text): return False # Metadata
            if re.match(r'^\d+(\.\d+)?(MG|G|ML|MCG|MM|%|MH)$', text, re.IGNORECASE): return False # Dosages
            if re.match(r'^\d+/\d+$', text): return False # Fractions like 1/4
            if re.match(r'.*\d+\.\d+/\d+.*', text): return False # Ratio patterns like "0.95/100"
            if ':' in text: return False # Colon-separated text (UI labels)
            
            # EXPANDED blocklist
            blocklist = [
                "NONE", "NULL", "UNKNOWN", "NA", 
                "OCR", "CONFIDENCE", "ANALYSIS", "DETECTED", 
                "TECHNICAL", "DETAILS", "CLINICAL", "CONTEXT", "RAW", "DATA",
                "UPLOAD", "IMAGE", "DRUG", "NAME", "BARCODE", "TYPE",
                "SAMPLE", "TEST", "DEMO", "EXAMPLE",  # Test labels
                "TIES", "TIE",  # Specific to issue
                "EXP", "DATE", "TIME", "SERIAL", "NO",
                "MATCH", "SCORE", "CUI", "RXNORM", "VERIFIED"  # UI elements
            ]
            for bad_word in blocklist:
                if bad_word in text:
                     return False
                     
            return True

        # Filter valid candidates AND prioritize LARGEST text (likely drug name)
        def get_text_size(bbox):
            """Calculate text size from bounding box"""
            if len(bbox) >= 2:
                width = abs(bbox[1][0] - bbox[0][0])
                height = abs(bbox[2][1] - bbox[0][1])
                return width * height
            return 0
        
        valid_candidates = []
        for bbox, text, conf in text_results:
            if is_valid_name(text):
                size = get_text_size(bbox)
                valid_candidates.append((text, conf, size))
        
        if valid_candidates:
            # Sort by SIZE first (drug names are usually large), then confidence
            sorted_text = sorted(valid_candidates, key=lambda x: (x[2], x[1]), reverse=True)
            extracted_name = sorted_text[0][0]
            confidence = sorted_text[0][1]
            print(f"[OCR] Selected: '{extracted_name}' (size: {sorted_text[0][2]:.0f}, conf: {confidence:.2f})")
        else:
            extracted_name = None
            confidence = 0.0
            print("[OCR] No valid drug name candidates found")
        
        # 3. Verify
        # Only verify if we have a candidate
        if extracted_name:
             verification = self.verifier.verify_drug(extracted_name)
        else:
             verification = {
                "verified": False,
                "match_score": 0.0,
                "rxcui": None,
                "norm_name": None
             }
        
        # 4. Enrich
        enrichment = self.enricher.enrich(verification)
        
        # 5. Advanced Parsing (Manufacturer, Dosage, etc.)
        raw_lines = [t[1] for t in text_results]
        parsed_data = self.parser.parse(raw_lines)

        # INTELLIGENT BACKFILL: If parser missed data, fill from verification result
        if verification['verified']:
             if not parsed_data['manufacturer'] and verification.get('manufacturer'):
                 parsed_data['manufacturer'] = verification['manufacturer']
             
             # If "drug_name" looks like a GS1 code (e.g. starts with (01)), try to parse it
             # and set proper drug name from verification if available
             if extracted_name and extracted_name.startswith("(01)"):
                 # It's a barcode pattern, not a drug name.
                 # If verification gave us a brand name, use that as the display name
                 if verification.get('brand_name'):
                     extracted_name = verification['brand_name']
                 elif verification.get('generic_name'):
                     extracted_name = verification['generic_name']

        # 6. Format Output
        output = {
            "image_id": os.path.basename(image_path),
            "fields": {
                "drug_name": {"value": extracted_name, "source": "ocr", "confidence": confidence},
                "barcode": {"value": barcodes[0]['data'] if barcodes else None, "source": "barcode"},
                "regions": [], # Bypassed YOLO detection, no regions
                "meta": parsed_data # Add dosage, manufacturer, etc.
            },
            "verification": {
                "matched_source": "openFDA" if verification['verified'] else None,
                "match_score": verification['match_score'],
                "rxcui": verification.get('rxcui')
            },
            "enrichment": enrichment
        }
        
        return output

if __name__ == "__main__":
    # Example usage
    # pipeline = PharmaPipeline()
    # result = pipeline.process_image("test.jpg")
    # print(json.dumps(result, indent=2))
    pass
