import numpy as np

def fast_levenshtein(s1, s2):
    if len(s1) < len(s2):
        return fast_levenshtein(s2, s1)
    if not s2:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_cer(reference, hypothesis):
    """Character Error Rate: (S+D+I) / N"""
    if not reference:
        return 1.0 if hypothesis else 0.0
    dist = fast_levenshtein(reference, hypothesis)
    return dist / len(reference)

class Evaluator:
    def evaluate_pipeline(self, ground_truth, predictions):
        metrics = {}
        # Calculate Mean CER
        cers = []
        for gt, pred in zip(ground_truth, predictions):
            cers.append(calculate_cer(gt.get('drug_name'), pred.get('drug_name')))
        
        metrics['mean_cer'] = np.mean(cers)
        
        # Calculate Entity Match Rate
        correct = 0
        total = len(ground_truth)
        for gt, pred in zip(ground_truth, predictions):
            if gt.get('drug_name').lower() == pred.get('drug_name', '').lower():
                correct += 1
        
        metrics['entity_match_rate'] = correct / total if total > 0 else 0
        return metrics
