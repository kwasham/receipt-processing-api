#!/usr/bin/env python3
"""
Generate evaluation dataset from receipt images and ground truth data.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.services.evaluation_pipeline import EvaluationPipeline


async def generate_dataset_from_images(
    image_dir: Path,
    ground_truth_dir: Path,
    output_file: Path,
    model: str = "gpt-4o-mini"
) -> None:
    """Generate dataset by processing images and comparing with ground truth."""
    # Ensure paths are relative to the parent directory (one level higher)
    base_dir = Path(__file__).parent.parent
    image_dir = base_dir / image_dir if not image_dir.is_absolute() else image_dir
    ground_truth_dir = base_dir / ground_truth_dir if not ground_truth_dir.is_absolute() else ground_truth_dir
    output_file = base_dir / output_file if not output_file.is_absolute() else output_file

    # Use the evaluation pipeline's create_dataset_content function
    pipeline = EvaluationPipeline()
    dataset = await pipeline.create_dataset_content(
        image_dir,
        ground_truth_dir, 
        model
    )
    
    # Save dataset
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        for record in dataset:
            f.write(json.dumps(record) + '\n')
    
    print(f"Generated dataset with {len(dataset)} records: {output_file}")


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate evaluation dataset")
    parser.add_argument(
        "--image-dir", 
        type=Path, 
        default=Path("data/test"),
        help="Directory containing receipt images"
    )
    parser.add_argument(
        "--ground-truth-dir",
        type=Path,
        default=Path("data/ground_truth"),
        help="Directory containing ground truth data"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/evaluation_dataset.jsonl"),
        help="Output file for dataset"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model to use for predictions"
    )
    
    args = parser.parse_args()
    
    await generate_dataset_from_images(
        args.image_dir,
        args.ground_truth_dir,
        args.output,
        args.model
    )


if __name__ == "__main__":
    asyncio.run(main())