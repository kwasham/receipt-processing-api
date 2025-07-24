# OpenAI Agents SDK Context for Receipt Extraction

Based on the official OpenAI Agents Python repository: https://github.com/openai/openai-agents-python

## Key Findings from the Official Repository

### 1. Correct Agent Pattern from the SDK

```python
from agents import Agent, Runner

# Basic agent creation
agent = Agent(
    name="receipt_extraction_agent",
    instructions="You are a helpful assistant that extracts receipt details",
    output_type=ReceiptDetails  # Structured output
)

# Running the agent
result = await Runner.run(agent, input_data)
print(result.final_output)
```

### 2. Image Processing Pattern (from local_image.py example)

```python
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

# Use in agent
result = await Runner.run(
    agent,
    [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "detail": "auto",  # or "high" for better quality
                    "image_url": f"data:image/jpeg;base64,{b64_image}",
                },
            ],
        },
        {
            "role": "user",
            "content": "Extract receipt details from this image",
        },
    ],
)
```

### 3. Structured Output Types (from non_strict_output_type.py)

```python
from agents import Agent, AgentOutputSchema

# Option 1: Direct dataclass/Pydantic model
agent = Agent(
    name="receipt_extractor",
    instructions="Extract receipt details",
    output_type=ReceiptDetails  # Your Pydantic model
)

# Option 2: Non-strict schema (if needed)
agent = Agent(
    name="receipt_extractor",
    instructions="Extract receipt details",
    output_type=AgentOutputSchema(ReceiptDetails, strict_json_schema=False)
)
```

### 4. The Agent Loop (from README)

When you call `Runner.run()`:

1. Call the LLM with model/settings and message history
2. LLM returns response (may include tool calls)
3. If response has final output matching `output_type`, return it
4. If no `output_type`, first response without tool calls is final output
5. Process tool calls and repeat

## Refactored Receipt Extraction Service

```python
"""
Extraction service using OpenAI Agents SDK patterns.
"""
import asyncio
import base64
import logging
from typing import Optional

from agents import Agent, Runner
from src.core.config import settings
from src.models.receipt import ReceiptDetails
from src.prompts.extraction_prompt import EXTRACTION_PROMPT
from src.utils.image_processing import preprocess_image

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for extracting receipt details from images using OpenAI Agents."""

    def __init__(self):
        pass  # No client needed - agents handle this internally

    def _image_to_base64(self, image_data: bytes) -> str:
        """Convert image bytes to base64 string."""
        return base64.b64encode(image_data).decode("utf-8")

    async def extract_receipt_details(
        self,
        file_data: bytes,
        filename: str,
        model: str = "gpt-4o"  # Use vision-capable model
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
                        "detail": "high",  # High detail for receipt text
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
```

## Key Changes from Your Current Implementation

1. **Import**: `from agents import Agent, Runner` (correct SDK)
2. **No OpenAI client needed**: Agents SDK handles this internally
3. **Correct image format**: Use `"type": "input_image"` with base64 data URL
4. **Message structure**: Use list of message objects with proper content format
5. **Structured output**: Set `output_type=ReceiptDetails` on agent
6. **Result access**: Use `result.final_output` directly

## Important Notes

- The SDK automatically handles structured output parsing
- Use `"detail": "high"` for receipt images (better OCR)
- No need for manual JSON parsing - the SDK does this
- The agent loop handles retries and validation automatically
- Set `OPENAI_API_KEY` environment variable for authentication
