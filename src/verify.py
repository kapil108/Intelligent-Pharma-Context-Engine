import sqlite3
import json
from .rxnorm_client import RxNormClient
from rapidfuzz import process, fuzz

import os

class Verifier:
    def __init__(self, db_path=None):
        if db_path is None:
             base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
             db_path = os.path.join(base_dir, 'data', 'openfda_labels', 'fda_labels.db')
        self.db_path = db_path
        self.rxnorm = RxNormClient()

    def verify_drug(self, extracted_name):
        print(f"[DEBUG] Verifying drug name: '{extracted_name}' (Type: {type(extracted_name)})")
        if not extracted_name or str(extracted_name).upper() == "UNKNOWN" or len(str(extracted_name).strip()) < 3:
            print("[DEBUG] Name rejected as invalid/empty.")
            return {
                "verified": False,
                "match_score": 0.0,
                "norm_name": extracted_name
            }

        # 1. Normalize via RxNorm API (Primary verification source)
        norm_result = self.rxnorm.normalize_name(extracted_name)
        
        # If RxNorm found a match, use it directly for verification
        if norm_result and norm_result.get('rxcui'):
            rxnorm_score = int(float(norm_result.get('score', 0)))
            print(f"[DEBUG] RxNorm found: {norm_result['name']} (RXCUI: {norm_result['rxcui']}, Score: {rxnorm_score})")
            
            # RxNorm score > 50 means good match (their scale is different)
            if rxnorm_score >= 50:
                print(f"[DEBUG] ✅ VERIFIED via RxNorm API! Score: {rxnorm_score}")
                return {
                    "verified": True,
                    "match_score": min(rxnorm_score, 100),  # Normalize to 100
                    "brand_name": extracted_name,
                    "generic_name": norm_result['name'],
                    "manufacturer": None,
                    "raw_data": {},  # No detailed data from RxNorm alone
                    "rxcui": norm_result['rxcui']
                }
        
        lookup_name = norm_result['name'] if norm_result else extracted_name
        
        # 2. Try local FDA DB for additional data
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT brand_name, generic_name, manufacturer_name, raw_json FROM labels WHERE brand_name LIKE ? OR generic_name LIKE ?", 
                           (f"%{lookup_name}%", f"%{lookup_name}%"))
            
            matches = cursor.fetchall()
            conn.close()
            
            if matches:
                choices = [m[0] for m in matches] + [m[1] for m in matches]
                best_choice = process.extractOne(lookup_name, choices, scorer=fuzz.WRatio)
                
                if best_choice and best_choice[1] >= 80:
                    selected_row = matches[0]
                    for m in matches:
                        if best_choice[0] == m[0] or best_choice[0] == m[1]:
                            selected_row = m
                            break
                    
                    print(f"[DEBUG] ✅ VERIFIED via local FDA DB! Score: {best_choice[1]}")
                    return {
                        "verified": True,
                        "match_score": best_choice[1],
                        "brand_name": selected_row[0],
                        "generic_name": selected_row[1],
                        "manufacturer": selected_row[2],
                        "raw_data": json.loads(selected_row[3]) if selected_row[3] else {},
                        "rxcui": norm_result['rxcui'] if norm_result else None
                    }
        except Exception as e:
            print(f"[DEBUG] Local DB lookup failed: {e}")
        
        # 3. Final fallback - if RxNorm found something but score was low
        if norm_result:
            return {
                "verified": False,
                "match_score": int(float(norm_result.get('score', 0))),
                "norm_name": norm_result['name'],
                "rxcui": norm_result['rxcui']
            }
        
        return {
            "verified": False,
            "match_score": 0.0,
            "norm_name": lookup_name
        }

