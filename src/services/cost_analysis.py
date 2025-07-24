"""
Business cost analysis integration for evaluation results.
"""
from src.utils.cost_calculator import calculate_costs, calculate_system_metrics


def summarize_costs_from_eval(eval_result: dict, per_receipt_cost: float = 2.0):
    """
    Summarize business costs from an evaluation result dict.
    Expects eval_result to contain TP, FP, TN, FN counts (true/false positives/negatives).
    """
    # Example: eval_result["metrics"] = {"tp": 100, "fp": 5, "tn": 80, "fn": 10}
    metrics = eval_result.get("metrics", {})
    tp = metrics.get("tp", 0)
    fp = metrics.get("fp", 0)
    tn = metrics.get("tn", 0)
    fn = metrics.get("fn", 0)
    
    # Calculate error rates
    total = tp + fp + tn + fn
    fp_rate = fp / total if total else 0
    fn_rate = fn / total if total else 0
    
    # Calculate costs
    total_cost = calculate_costs(fp_rate, fn_rate, per_receipt_cost)
    system_metrics = calculate_system_metrics(tp, fp, tn, fn)
    
    return {
        "total_cost": total_cost,
        "system_metrics": system_metrics,
        "fp_rate": fp_rate,
        "fn_rate": fn_rate,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }
