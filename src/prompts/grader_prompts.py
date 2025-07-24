"""
Grader prompts for receipt processing evaluation.
"""

# Item extraction grader prompts
ITEM_EXTRACTION_BASE = """
Your task is to evaluate the correctness of a receipt extraction model.

The following items are the actual (correct) line items from a specific receipt.

{{ item.correct_receipt_details.items }}

The following items are the line items extracted by the model.

{{ item.predicted_receipt_details.items }}
"""

MISSED_ITEMS_GRADER = ITEM_EXTRACTION_BASE + """
Score 0 if the sample evaluation missed any items from the receipt; otherwise score 1.

The line items are permitted to have small differences or extraction mistakes, but each
item from the actual receipt must be present in some form in the model's output. Only
evaluate whether there are MISSED items; ignore other mistakes or extra items.
"""

EXTRA_ITEMS_GRADER = ITEM_EXTRACTION_BASE + """
Score 0 if the sample evaluation extracted any extra items from the receipt; otherwise
score 1.

The line items are permitted to have small differences or extraction mistakes, but each
item from the actual receipt must be present in some form in the model's output. Only
evaluate whether there are EXTRA items; ignore other mistakes or missed items.
"""

ITEM_MISTAKES_GRADER = ITEM_EXTRACTION_BASE + """
Score 0 to 10 based on the number and severity of mistakes in the line items.

A score of 10 means that the two lists are perfectly identical.

Remove 1 point for each minor mistake (typos, capitalization, category name
differences), and up to 3 points for significant mistakes (incorrect quantity, price, or
total, or categories that are not at all similar).
"""

# Audit reasoning grader prompt
AUDIT_REASONING_GRADER = """
Your task is to evaluate the quality of *reasoning* for audit decisions on receipts.
Here are the rules for audit decisions:

Expenses should be audited if they violate any of the following criteria:
1. Expenses must be travel-related
2. Expenses must not exceed $50
3. All math should be correct; the line items plus tax should equal the total
4. There must not be an "X" in the handwritten notes

If ANY of those criteria are violated, the expense should be audited.

Here is the input to the grader:
{{ item.predicted_receipt_details }}

Below is the output of an authoritative grader making a decision about whether or not to
audit an expense. This is a correct reference decision.

GROUND TRUTH:
{{ item.correct_audit_decision }}


Here is the output of the model we are evaluating:

MODEL GENERATED:
{{ item.predicted_audit_decision }}


Evaluate:
1. For each of the 4 criteria, did the model correctly score it as TRUE or FALSE?
2. Based on the model's *scoring* of the criteria (regardless if it scored it
   correctly), did the model reason appropriately about the criteria (i.e. did it
   understand and apply the prompt correctly)?
3. Is the model's reasoning logically sound, sufficient, and comprehensible?
4. Is the model's reasoning concise, without extraneous details?
5. Is the final decision to audit or not audit correct?

Grade the model with the following rubric:
- (1) point for each of the 4 criteria that the model scored correctly
- (3) points for each aspect of the model's reasoning that is meets the criteria
- (3) points for the model's final decision to audit or not audit

The total score is the sum of the points, and should be between 0 and 10 inclusive.
"""
