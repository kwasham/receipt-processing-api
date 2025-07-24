"""
Extraction service using OpenAI Agents SDK patterns.
"""
import asyncio
import base64
import logging
import os
from typing import Optional

from agents import Agent, Runner, set_default_openai_api
from src.core.config import settings
from src.models.receipt import ReceiptDetails
from src.prompts.extraction_prompt import EXTRACTION_PROMPT
from src.utils.image_processing import preprocess_image

# Configure OpenAI Agents to use Responses API (default behavior)
# Explicitly ensure we're using responses API instead of chat completions
set_default_openai_api("responses")

# Disable verbose logging to prevent image data spam
# enable_verbose_stdout_logging()  # Commented out to reduce log spam

# Disable sensitive data logging to prevent image data in logs
os.environ["OPENAI_AGENTS_DONT_LOG_MODEL_DATA"] = "1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for extracting receipt details from images using OpenAI Agents."""

    def __init__(self):
        # Configure the SDK to use Responses API explicitly
        # This should make it use /responses endpoint instead of /chat/completions
        set_default_openai_api("responses")
        pass  # No client needed - agents handle this internally

    def _image_to_base64(self, image_data: bytes) -> str:
        """Convert image bytes to base64 string."""
        return base64.b64encode(image_data).decode("utf-8")

    async def extract_receipt_details(
        self,
        file_data: bytes,
        filename: str,
        model: str = "gpt-o4-mini"  # Use vision-capable model
    ) -> ReceiptDetails:
        """Extract structured data from receipt image or PDF."""

        print("=== STARTING EXTRACTION ===", flush=True)
        logger.info("Starting extraction process")

        # Check if it's a PDF
        if filename.lower().endswith('.pdf'):
            print("Processing PDF...", flush=True)
            from src.api.dependencies import process_pdf_to_images
            images = await process_pdf_to_images(file_data)

            if images:
                file_data = images[0]
            else:
                raise ValueError("PDF has no pages")

        print("Preprocessing image...", flush=True)
        processed_image = preprocess_image(file_data)

        print("Encoding to base64...", flush=True)
        b64_image = self._image_to_base64(processed_image)

        print("Creating agent...", flush=True)
        agent = Agent(
            name="receipt_extraction_agent",
            instructions=EXTRACTION_PROMPT,
            model=model,
            output_type=ReceiptDetails  # Structured output
        )

        print("Running agent...", flush=True)

        # Use the correct message format from the SDK examples
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "detail": "auto",  # Auto detail for receipt text
                        "image_url": f"data:image/jpeg;base64,{b64_image}",
                    },
                ],
            },
            {
                "role": "user",
                "content": "Extract the receipt details from this image according to the ReceiptDetails schema.",
            },
        ]

        try:
            result = await Runner.run(agent, messages)

            print(f"=== EXTRACTION COMPLETE ===", flush=True)
            print(f"=== RESULT TYPE: {type(result.final_output)} ===", flush=True)

            # The SDK automatically parses to the output_type
            return result.final_output

        except Exception as e:
            print(f"=== EXTRACTION ERROR: {e} ===", flush=True)
            logger.error(f"Error during extraction: {str(e)}")

            # Return empty receipt as fallback
            from src.models.receipt import Location
            return ReceiptDetails(
                merchant=None,
                location=Location(city=None, state=None, zipcode=None),
                time=None,
                items=[],
                subtotal=None,
                tax=None,
                total=None,
                handwritten_notes=[]
            )