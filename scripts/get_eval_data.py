import openai
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import settings


openai.api_key = settings.OPENAI_API_KEY
eval_id = "eval_687f196505888191b986d9e3ea173264"
run_id = "evalrun_687f19659c108191b80f13e3e4124421"

run = openai.evals.runs.retrieve(
    eval_id=eval_id,
    run_id=run_id,
)

# Save to file
import json

# Get all items from the content array
all_items = [content_item.item for content_item in run.data_source.source.content]

with open("scripts/results.json", "w") as f:
    json.dump(all_items, f, indent=2)


