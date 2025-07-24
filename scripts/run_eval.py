#!/usr/bin/env python3
"""
Run evaluation using the notebook pattern with create_dataset_content.
"""
import asyncio
import click
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.services.evaluation_pipeline import EvaluationPipeline
from src.utils.graders import get_all_graders


@click.command()
@click.option('--name', required=True, help='Name for the evaluation run')
@click.option('--image-dir', type=Path, default=Path("scripts/data/test"), help='Directory containing test images')
@click.option('--ground-truth-dir', type=Path, default=Path("scripts/data/ground_truth"), help='Directory containing ground truth')
@click.option('--model', default="gpt-4o-mini", help='Model to use for evaluation')
@click.option('--compare-models', is_flag=True, help='Compare multiple models')
@click.option('--use-example-graders', is_flag=True, help='Use minimal example graders (like notebook initial_eval)')
def run_eval(name: str, image_dir: Path, ground_truth_dir: Path, model: str, compare_models: bool, use_example_graders: bool):
    """Run evaluation following the notebook pattern."""
    async def run():
        pipeline = EvaluationPipeline()
        
        # Choose graders - use example graders if requested (matches notebook)
        if use_example_graders:
            from src.utils.graders import get_example_graders
            graders = get_example_graders()
            print(f"🎯 Using example graders (3 graders, matches notebook initial_eval)")
        else:
            graders = None  # Will use all graders by default
            print(f"🎯 Using all comprehensive graders (18+ graders)")
        
        if compare_models:
            models = ["gpt-4o-mini", "gpt-4o"]
            for model_name in models:
                print(f"\n🔍 Running evaluation for {model_name}...")
                
                # Create dataset using create_dataset_content
                dataset = await pipeline.create_dataset_content(
                    image_dir, 
                    ground_truth_dir,
                    model_name
                )
                
                # Run evaluation
                result = await pipeline.create_and_run_eval(f"{name}-{model_name}", dataset, graders)
                
                if result["status"] == "success":
                    print(f"✅ {model_name} evaluation created successfully!")
                    print(f"📊 View results at: {result['report_url']}")
                else:
                    print(f"❌ {model_name} error: {result.get('error', 'Unknown error')}")
        else:
            print(f"🔍 Running evaluation for {model}...")
            
            # Create dataset using create_dataset_content
            dataset = await pipeline.create_dataset_content(
                image_dir, 
                ground_truth_dir,
                model
            )
            
            # Run evaluation
            result = await pipeline.create_and_run_eval(name, dataset, graders)
            
            if result["status"] == "success":
                print(f"✅ Evaluation created successfully!")
                print(f"📊 View results at: {result['report_url']}")
                print(f"📋 Eval ID: {result['eval_id']}")
                print(f"🏃 Run ID: {result['run_id']}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    asyncio.run(run())


if __name__ == "__main__":
    run_eval()
