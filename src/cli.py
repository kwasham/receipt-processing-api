@cli.command()
@click.option('--eval-id', required=True, help='OpenAI eval ID')
@click.option('--run-id', required=True, help='OpenAI eval run ID')
@click.option('--api-key', default=None, help='OpenAI API key (optional, overrides config)')
@click.option('--per-receipt-cost', default=2.0, type=float, help='Cost per receipt (default: $2.00)')
def summarize_costs(eval_id: str, run_id: str, api_key: str, per_receipt_cost: float):
    """Summarize business costs from an OpenAI eval run."""
    import openai
    import json
    from src.services.cost_analysis import summarize_costs_from_eval
    from src.core.config import settings

    openai.api_key = api_key or settings.OPENAI_API_KEY
    run = openai.evals.runs.retrieve(eval_id=eval_id, run_id=run_id)

    # Try to get metrics from run (user may need to adjust this for their schema)
    metrics = getattr(run, 'metrics', None)
    if metrics is None:
        print("❌ No metrics found in eval run. Cannot summarize costs.")
        return

    result = {"metrics": metrics}
    summary = summarize_costs_from_eval(result, per_receipt_cost=per_receipt_cost)

    print("\n💰 Business Cost Summary:")
    print(f"   Total Cost: ${summary['total_cost']:.2f}")
    print(f"   System Metrics: {summary['system_metrics']}")
    print(f"   FP Rate: {summary['fp_rate']:.3f}, FN Rate: {summary['fn_rate']:.3f}")
    print(f"   TP: {summary['tp']}, FP: {summary['fp']}, TN: {summary['tn']}, FN: {summary['fn']}")
"""Simplified CLI for receipt processing evaluation."""
import asyncio
import click
from pathlib import Path
from src.services.evaluation_pipeline import EvaluationPipeline


@click.group()
def cli():
    """Receipt processing evaluation CLI."""
    pass


@cli.command()
@click.option('--image-dir', type=Path, default=Path("scripts/data/test"), help='Directory containing test images')
@click.option('--ground-truth-dir', type=Path, default=Path("scripts/data/ground_truth"), help='Directory containing ground truth')
@click.option('--model', default="gpt-4o-mini", help='Model to use for evaluation')
@click.option('--name', required=True, help='Name for the evaluation run')
@click.option('--use-example-graders', is_flag=True, help='Use minimal example graders (like notebook initial_eval)')
def evaluate(image_dir: Path, ground_truth_dir: Path, model: str, name: str, use_example_graders: bool):
    """Run evaluation following the notebook pattern."""
    async def run():
        pipeline = EvaluationPipeline()
        
        # Create dataset
        dataset = await pipeline.create_dataset_content(
            image_dir, 
            ground_truth_dir,
            model
        )
        
        if len(dataset) == 0:
            print("❌ Dataset is empty. Check that ground truth files exist for your images.")
            return
        
        # Choose graders - use example graders if requested (matches notebook)
        if use_example_graders:
            from src.utils.graders import get_example_graders
            graders = get_example_graders()
            print(f"🎯 Using example graders (3 graders, matches notebook initial_eval)")
        else:
            graders = None  # Will use all graders by default
            print(f"🎯 Using all comprehensive graders (18+ graders)")
        
        # Run evaluation
        result = await pipeline.create_and_run_eval(name, dataset, graders)
        
        if result["status"] == "success":
            print(f"✅ Evaluation created successfully!")
            print(f"📊 View results at: {result['report_url']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    asyncio.run(run())


if __name__ == "__main__":
    cli()
