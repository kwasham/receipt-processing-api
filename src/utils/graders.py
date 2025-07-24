"""
Graders for receipt processing evaluation following the notebook pattern.
"""
from src.prompts.grader_prompts import (
    MISSED_ITEMS_GRADER,
    EXTRA_ITEMS_GRADER,
    ITEM_MISTAKES_GRADER,
    AUDIT_REASONING_GRADER
)


def get_extraction_graders():
    """Get graders for extraction accuracy."""
    simple_graders = [
        {
            "name": "Merchant Name Accuracy",
            "type": "text_similarity",
            "input": "{{ item.predicted_receipt_details.merchant }}",
            "reference": "{{ item.correct_receipt_details.merchant }}",
            "pass_threshold": 0.8,
            "evaluation_metric": "bleu",
        },
        {
            "name": "Location City Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.location.city }}",
            "reference": "{{ item.correct_receipt_details.location.city }}",
        },
        {
            "name": "Location State Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.location.state }}",
            "reference": "{{ item.correct_receipt_details.location.state }}",
        },
        {
            "name": "Location Zipcode Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.location.zipcode }}",
            "reference": "{{ item.correct_receipt_details.location.zipcode }}",
        },
        {
            "name": "Time Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.time }}",
            "reference": "{{ item.correct_receipt_details.time }}",
        },
        {
            "name": "Subtotal Amount Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.subtotal }}",
            "reference": "{{ item.correct_receipt_details.subtotal }}",
        },
        {
            "name": "Tax Amount Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.tax }}",
            "reference": "{{ item.correct_receipt_details.tax }}",
        },
        {
            "name": "Total Amount Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.total }}",
            "reference": "{{ item.correct_receipt_details.total }}",
        },
        {
            "name": "Handwritten Notes Accuracy",
            "type": "text_similarity",
            "input": "{{ item.predicted_receipt_details.handwritten_notes }}",
            "reference": "{{ item.correct_receipt_details.handwritten_notes }}",
            "pass_threshold": 0.8,
            "evaluation_metric": "fuzzy_match",
        },
    ]
    
    return simple_graders


def get_item_graders():
    """Get graders for line item extraction."""
    return [
        {
            "name": "Missed Line Items",
            "type": "score_model",
            "model": "gpt-4o-mini",
            "input": [
                {
                    "role": "system",
                    "content": MISSED_ITEMS_GRADER
                }
            ],
            "range": [0, 1],
            "pass_threshold": 1,
        },
        {
            "name": "Extra Line Items",
            "type": "score_model",
            "model": "gpt-4o-mini",
            "input": [
                {
                    "role": "system",
                    "content": EXTRA_ITEMS_GRADER
                }
            ],
            "range": [0, 1],
            "pass_threshold": 1,
        },
        {
            "name": "Item Mistakes",
            "type": "score_model",
            "model": "gpt-4o-mini",
            "input": [
                {
                    "role": "system",
                    "content": ITEM_MISTAKES_GRADER
                }
            ],
            "range": [0, 10],
            "pass_threshold": 8,
        },
    ]


def get_audit_graders():
    """Get graders for audit decision accuracy."""
    simple_audit_graders = [
        {
            "name": "Not Travel Related Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_audit_decision.not_travel_related }}",
            "reference": "{{ item.correct_audit_decision.not_travel_related }}",
        },
        {
            "name": "Amount Over Limit Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_audit_decision.amount_over_limit }}",
            "reference": "{{ item.correct_audit_decision.amount_over_limit }}",
        },
        {
            "name": "Math Error Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_audit_decision.math_error }}",
            "reference": "{{ item.correct_audit_decision.math_error }}",
        },
        {
            "name": "Handwritten X Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_audit_decision.handwritten_x }}",
            "reference": "{{ item.correct_audit_decision.handwritten_x }}",
        },
        {
            "name": "Needs Audit Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_audit_decision.needs_audit }}",
            "reference": "{{ item.correct_audit_decision.needs_audit }}",
        },
    ]
    
    model_judgement_graders = [
        {
            "name": "Audit Reasoning Quality",
            "type": "score_model",
            "model": "gpt-4o-mini",
            "input": [{"role": "system", "content": AUDIT_REASONING_GRADER}],
            "range": [0, 10],
            "pass_threshold": 8,
        },
    ]
    
    return simple_audit_graders + model_judgement_graders


def get_all_graders():
    """Get all graders for full evaluation."""
    return get_extraction_graders() + get_item_graders() + get_audit_graders()


def get_example_graders():
    """Get the basic example graders used in the notebook's initial_eval."""
    return [
        {
            "name": "Total Amount Accuracy",
            "type": "string_check",
            "operation": "eq",
            "input": "{{ item.predicted_receipt_details.total }}",
            "reference": "{{ item.correct_receipt_details.total }}",
        },
        {
            "name": "Merchant Name Accuracy",
            "type": "text_similarity",
            "input": "{{ item.predicted_receipt_details.merchant }}",
            "reference": "{{ item.correct_receipt_details.merchant }}",
            "pass_threshold": 0.8,
            "evaluation_metric": "bleu",
        },
        {
            "name": "Missed Line Items",
            "type": "score_model",
            "model": "gpt-4o-mini",
            "input": [
                {
                    "role": "system",
                    "content": MISSED_ITEMS_GRADER
                }
            ],
            "range": [0, 1],
            "pass_threshold": 1,
        },
    ]


# For backward compatibility and easy imports
SIMPLE_EXTRACTION_GRADERS = get_extraction_graders()
ITEM_EXTRACTION_GRADERS = get_item_graders()
SIMPLE_AUDIT_GRADERS = get_audit_graders()
ALL_GRADERS = get_all_graders()
