"""Business cost calculations from the notebook."""

def calculate_costs(fp_rate: float, fn_rate: float, per_receipt_cost: float) -> float:
    """
    Calculate total system cost based on error rates.
    
    From the notebook's business model:
    - Company processes 1 million receipts/year at baseline $0.20/receipt
    - Auditing a receipt costs $2
    - Missing an audit costs $30
    - 5% of receipts need auditing
    - Current system: 97% true positive rate, 2% false positive rate
    """
    audit_cost = 2
    missed_audit_cost = 30
    receipt_count = 1e6
    audit_fraction = 0.05

    needs_audit_count = receipt_count * audit_fraction
    no_needs_audit_count = receipt_count - needs_audit_count

    missed_audits = needs_audit_count * fn_rate
    total_audits = needs_audit_count * (1 - fn_rate) + no_needs_audit_count * fp_rate

    audit_cost_total = total_audits * audit_cost
    missed_audit_cost_total = missed_audits * missed_audit_cost
    processing_cost = receipt_count * per_receipt_cost

    return audit_cost_total + missed_audit_cost_total + processing_cost


def calculate_system_metrics(tp: int, fp: int, tn: int, fn: int) -> dict:
    """Calculate evaluation metrics from confusion matrix."""
    total = tp + fp + tn + fn
    if total == 0:
        return {
            "total": 0,
            "accuracy": 0,
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
            "fp_rate": 0,
            "fn_rate": 0
        }
    
    audit_positive = tp + fn
    audit_negative = fp + tn
    
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / audit_positive if audit_positive > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    fp_rate = fp / audit_negative if audit_negative > 0 else 0
    fn_rate = fn / audit_positive if audit_positive > 0 else 0
    
    return {
        "total": total,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "fp_rate": fp_rate,
        "fn_rate": fn_rate
    }
