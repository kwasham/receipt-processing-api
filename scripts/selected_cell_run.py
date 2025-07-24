import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.services.evaluation_pipeline import EvaluationPipeline
from openai import AsyncOpenAI
from src.core.config import settings


async def main():
    receipt_image_dir = Path("scripts/data/test")  
    ground_truth_dir = Path("scripts/data/ground_truth")
    pipeline = EvaluationPipeline()
    file_content = await pipeline.create_dataset_content(receipt_image_dir, ground_truth_dir)
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    # You may need to create full_eval first, or pass an existing eval_id
    # full_eval = await client.evals.create(
    #     name="updated-receipt-processing-eval",
    #     data_source_config={
    #         "type": "custom",
    #         "item_schema": None,  # Provide schema if needed
    #         "include_sample_schema": False,
    #     },
    #     testing_criteria=pipeline.get_graders(),
    # )
    # eval_run = await client.evals.runs.create(
    #     name="updated-receipt-processing-run",
    #     eval_id="eval_687f196505888191b986d9e3ea173264",
    #     data_source={
    #         "type": "jsonl",
    #         "source": {"type": "file_content", "content": file_content},
    #     },
    # )
    # print(eval_run.report_url)

    file_content = await pipeline.create_dataset_content(receipt_image_dir, ground_truth_dir,model="gpt-4.1-mini")

    eval_run = await client.evals.runs.create(
        name="receipt-processing-run-gpt-4-1-mini",
        eval_id="eval_687f196505888191b986d9e3ea173264",
        data_source={
            "type": "jsonl",
            "source": {"type": "file_content", "content": file_content},
        },
    )

    eval_run.report_url

if __name__ == "__main__":
    asyncio.run(main())
