"""
Service for auditing receipts based on business rules using OpenAI Agents SDK.
"""
import logging
import os
from typing import Optional
from agents import Agent, Runner, set_default_openai_api
from src.models.audit import AuditDecision
from src.models.receipt import ReceiptDetails, Location, LineItem
from src.core.config import settings
from src.prompts.audit_prompts import AUDIT_PROMPT_IMPROVED

# Configure to use Responses API
set_default_openai_api("responses")

# Disable sensitive data logging to prevent receipt data in logs
os.environ["OPENAI_AGENTS_DONT_LOG_MODEL_DATA"] = "1"

logger = logging.getLogger(__name__)

# Define the examples exactly as in the notebook
def get_audit_examples():
    """Get few-shot examples for audit decisions."""
    nursery_receipt = ReceiptDetails(
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
    
    nursery_audit = AuditDecision(
        not_travel_related=True,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="1. The merchant is a plant nursery and the item purchased an insecticide, so this purchase is not travel-related (criterion 1 violated). 2. The total is $26.93, under $50, so criterion 2 is not violated. 3. The line items (1 * $24.99 + $1.94 tax) sum to $26.93, so criterion 3 is not violated. 4. There are no handwritten notes or 'X's, so criterion 4 is not violated. Since NOT_TRAVEL_RELATED is true, the receipt must be audited.",
        needs_audit=True,
    )
    
    flying_j_receipt = ReceiptDetails(
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
    
    flying_j_audit = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="1. The only item purchased is Unleaded gasoline, which is travel-related so NOT_TRAVEL_RELATED is false. 2. The total is $49.39, which is under $50, so AMOUNT_OVER_LIMIT is false. 3. The line items ($4.459 * 11.076 = $49.387884) sum to the total of $49.39, so MATH_ERROR is false. 4. There is no 'X' in the handwritten notes, so HANDWRITTEN_X is false. Since none of the criteria are violated, the receipt does not need auditing.",
        needs_audit=False,
    )
    
    engine_oil_receipt = ReceiptDetails(
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
    
    engine_oil_audit = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="1. The only item purchased is engine oil, which might be required for a vehicle while traveling, so NOT_TRAVEL_RELATED is false. 2. The total is $13.35, which is under $50, so AMOUNT_OVER_LIMIT is false. 3. The line items ($12.28 + $1.07 tax) sum to the total of $13.35, so MATH_ERROR is false. 4. There is no 'X' in the handwritten notes, so HANDWRITTEN_X is false. None of the criteria are violated so the receipt does not need to be audited.",
        needs_audit=False,
    )
    
    return [
        {"input": nursery_receipt, "output": nursery_audit},
        {"input": flying_j_receipt, "output": flying_j_audit},
        {"input": engine_oil_receipt, "output": engine_oil_audit},
    ]


class AuditService:
    """Service for evaluating receipts against audit criteria using OpenAI Agents SDK."""
    
    def __init__(self):
        """Initialize audit service."""
        # Configure to use Responses API
        set_default_openai_api("responses")
        # No client needed - agents handle this internally
        self.examples = self._prepare_examples()
    
    def _prepare_examples(self) -> str:
        """Prepare few-shot examples for the audit prompt."""
        examples = get_audit_examples()
        
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
        
        return examples_string
    
    async def audit_receipt(
        self,
        receipt_details: ReceiptDetails,
        model: str = "gpt-4o-mini"
    ) -> AuditDecision:
        """Audit a receipt based on business rules using OpenAI Agents SDK."""
        receipt_json = receipt_details.model_dump_json(indent=2)
        
        # Use the improved prompt with examples
        prompt = AUDIT_PROMPT_IMPROVED.format(examples=self.examples)
        
        try:
            # Create audit agent
            agent = Agent(
                name="receipt_audit_agent",
                instructions=prompt,
                model=model,
                output_type=AuditDecision
            )
            
            # Run the agent with receipt data
            input_message = f"Audit this receipt data:\n\n{receipt_json}"
            result = await Runner.run(agent, input_message)
            
            return result.final_output
            
        except Exception as e:
            logger.error(f"Error during audit: {str(e)}")
            return AuditDecision(
                not_travel_related=False,
                amount_over_limit=False,
                math_error=False,
                handwritten_x=False,
                reasoning=f"Audit error: {str(e)}",
                needs_audit=True
            )

