"""
Prompts for receipt auditing.
"""
from src.models.receipt import ReceiptDetails, Location, LineItem
from src.models.audit import AuditDecision


def get_audit_prompt() -> str:
    """Get the audit prompt with examples."""
    # Example receipts and audit decisions
    nursery_receipt_details = ReceiptDetails(
        merchant="WESTERN SIERRA NURSERY",
        location=Location(city="Oakhurst", state="CA", zipcode="93644"),
        time="2024-09-27T12:33:38",
        items=[
            LineItem(
                description="Plantskydd Repellent RTU 1 Liter",
                product_code=None,
                category="Garden/Pest Control",
                item_price="24.99",
                sale_price=None,
                quantity="1",
                total="24.99",
            )
        ],
        subtotal="24.99",
        tax="1.94",
        total="26.93",
        handwritten_notes=[],
    )

    nursery_audit_decision = AuditDecision(
        not_travel_related=True,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="""
        1. The merchant is a plant nursery and the item purchased an insecticide, so this
           purchase is not travel-related (criterion 1 violated).
        2. The total is $26.93, under $50, so criterion 2 is not violated.
        3. The line items (1 * $24.99 + $1.94 tax) sum to $26.93, so criterion 3 is not
           violated.
        4. There are no handwritten notes or 'X's, so criterion 4 is not violated.
        Since NOT_TRAVEL_RELATED is true, the receipt must be audited.
        """,
        needs_audit=True,
    )

    flying_j_details = ReceiptDetails(
        merchant="Flying J #616",
        location=Location(city="Frazier Park", state="CA", zipcode=None),
        time="2024-10-01T13:23:00",
        items=[
            LineItem(
                description="Unleaded",
                product_code=None,
                category="Fuel",
                item_price="4.459",
                sale_price=None,
                quantity="11.076",
                total="49.39",
            )
        ],
        subtotal="49.39",
        tax=None,
        total="49.39",
        handwritten_notes=["yos -> home sequoia", "236660"],
    )
    
    flying_j_audit_decision = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="""
        1. The only item purchased is Unleaded gasoline, which is travel-related so
           NOT_TRAVEL_RELATED is false.
        2. The total is $49.39, which is under $50, so AMOUNT_OVER_LIMIT is false.
        3. The line items ($4.459 * 11.076 = $49.387884) sum to the total of $49.39, so
           MATH_ERROR is false.
        4. There is no "X" in the handwritten notes, so HANDWRITTEN_X is false.
        Since none of the criteria are violated, the receipt does not need auditing.
        """,
        needs_audit=False,
    )

    engine_oil_details = ReceiptDetails(
        merchant="O'Reilly Auto Parts",
        location=Location(city="Sylmar", state="CA", zipcode="91342"),
        time="2024-04-26T8:43:11",
        items=[
            LineItem(
                description="VAL 5W-20",
                product_code=None,
                category="Auto",
                item_price="12.28",
                sale_price=None,
                quantity="1",
                total="12.28",
            )
        ],
        subtotal="12.28",
        tax="1.07",
        total="13.35",
        handwritten_notes=["vista -> yos"],
    )
    
    engine_oil_audit_decision = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="""
        1. The only item purchased is engine oil, which might be required for a vehicle
           while traveling, so NOT_TRAVEL_RELATED is false.
        2. The total is $13.35, which is under $50, so AMOUNT_OVER_LIMIT is false.
        3. The line items ($12.28 + $1.07 tax) sum to the total of $13.35, so
           MATH_ERROR is false.
        4. There is no "X" in the handwritten notes, so HANDWRITTEN_X is false.
        None of the criteria are violated so the receipt does not need to be audited.
        """,
        needs_audit=False,
    )

    examples = [
        {"input": nursery_receipt_details, "output": nursery_audit_decision},
        {"input": flying_j_details, "output": flying_j_audit_decision},
        {"input": engine_oil_details, "output": engine_oil_audit_decision},
    ]

    # Format the examples as JSON, with each example wrapped in XML tags.
    example_format = """
<example>
    <input>
        {input}
    </input>
    <output>
        {output}
    </output>
</example>
"""

    examples_string = ""
    for example in examples:
        example_input = example["input"].model_dump_json()
        correct_output = example["output"].model_dump_json()
        examples_string += example_format.format(input=example_input, output=correct_output)

    return f"""
Evaluate this receipt data to determine if it need to be audited based on the following
criteria:

1. NOT_TRAVEL_RELATED:
   - IMPORTANT: For this criterion, travel-related expenses include but are not limited
   to: gas, hotel, airfare, or car rental.
   - If the receipt IS for a travel-related expense, set this to FALSE.
   - If the receipt is NOT for a travel-related expense (like office supplies), set this
   to TRUE.
   - In other words, if the receipt shows FUEL/GAS, this would be FALSE because gas IS
   travel-related.
   - Travel-related expenses include anything that could be reasonably required for
   business-related travel activities. For instance, an employee using a personal
   vehicle might need to change their oil; if the receipt is for an oil change or the
   purchase of oil from an auto parts store, this would be acceptable and counts as a
   travel-related expense.

2. AMOUNT_OVER_LIMIT: The total amount exceeds $50

3. MATH_ERROR: The math for computing the total doesn't add up (line items don't sum to
   total)
   - Add up the price and quantity of each line item to get the subtotal
   - Add tax to the subtotal to get the total
   - If the total doesn't match the amount on the receipt, this is a math error
   - If the total is off by no more than $0.01, this is NOT a math error

4. HANDWRITTEN_X: There is an "X" in the handwritten notes

For each criterion, determine if it is violated (true) or not (false). Provide your
reasoning for each decision, and make a final determination on whether the receipt needs
auditing. A receipt needs auditing if ANY of the criteria are violated.

Note that violation of a criterion means that it is `true`. If any of the above four
values are `true`, then the receipt needs auditing (`needs_audit` should be `true`: it
functions as a boolean OR over all four criteria).

If the receipt contains non-travel expenses, then NOT_TRAVEL_RELATED should be `true`
and therefore NEEDS_AUDIT must also be set to `true`. IF THE RECEIPT LISTS ITEMS THAT
ARE NOT TRAVEL-RELATED, THEN IT MUST BE AUDITED. Here are some example inputs to
demonstrate how you should act:

<examples>
{examples_string}
</examples>

Return a structured response with your evaluation.
"""