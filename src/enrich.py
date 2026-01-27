class Enricher:
    def enrich(self, verified_record):
        if not verified_record.get('verified'):
            return {}

        raw = verified_record.get('raw_data', {})
        
        # Extract detailed safety population information
        contraindications = raw.get('contraindications', [])
        warnings = raw.get('warnings', [])
        precautions = raw.get('precautions', [])
        
        # Parse who should NOT use (contraindications)
        unsafe_for = []
        if contraindications:
            contraindications_text = contraindications[0] if isinstance(contraindications, list) else str(contraindications)
            # Common contraindication patterns
            if 'pregnan' in contraindications_text.lower():
                unsafe_for.append("Pregnant women")
            if 'nursing' in contraindications_text.lower() or 'breastfeed' in contraindications_text.lower():
                unsafe_for.append("Nursing mothers")
            if 'children' in contraindications_text.lower() or 'pediatric' in contraindications_text.lower():
                unsafe_for.append("Children (check age restrictions)")
            if 'allerg' in contraindications_text.lower():
                unsafe_for.append("Those with known allergies to this drug or similar drugs")
        
        # Extract pregnancy category
        pregnancy_category = raw.get('pregnancy', ["Not specified"])[0] if raw.get('pregnancy') else "Not specified"
        
        # Extract pediatric use info
        pediatric_use = raw.get('pediatric_use', ["Not specified"])[0] if raw.get('pediatric_use') else "Consult physician"
        
        # Extract geriatric use info  
        geriatric_use = raw.get('geriatric_use', ["Not specified"])[0] if raw.get('geriatric_use') else "Consult physician"
        
        return {
            "storage": raw.get('how_supplied', ["N/A"])[0],
            "side_effects": raw.get('adverse_reactions', ["N/A"])[0],
            "warnings": warnings[0] if warnings else "N/A",
            "contraindications": contraindications[0] if contraindications else "No specific contraindications listed",
            "unsafe_for": unsafe_for if unsafe_for else ["Consult your physician"],
            "pregnancy_category": pregnancy_category,
            "pediatric_use": pediatric_use,
            "geriatric_use": geriatric_use,
            "drug_class": raw.get('openfda', {}).get('pharm_class_epc', ["N/A"]),
            "ndc": raw.get('openfda', {}).get('product_ndc', ["N/A"]),
            "interactions": raw.get('drug_interactions', ["Consult physician"])[0] if raw.get('drug_interactions') else "Consult physician"
        }

