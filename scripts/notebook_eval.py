#!/usr/bin/env python3
"""
Notebook-style evaluation functions using create_dataset_content.
"""
import asyncio
from pathlib import Path
from typing import Dict, List
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.services.evaluation_pipeline import EvaluationPipeline
from src.utils.graders import get_all_graders


class NotebookEvaluator:
    """Evaluator class for notebook-style usage."""
    
    def __init__(self, image_dir: Path = None, ground_truth_dir: Path = None):
        self.pipeline = EvaluationPipeline()
        self.image_dir = image_dir or Path("scripts/data/test")
        self.ground_truth_dir = ground_truth_dir or Path("scripts/data/ground_truth")
        self.dataset = None
        self.results = {}
    
    async def prepare_dataset(self, model: str = "gpt-4o-mini"):
        """Prepare dataset using create_dataset_content."""
        print(f"🔄 Preparing dataset with {model}...")
        self.dataset = await self.pipeline.create_dataset_content(
            self.image_dir,
            self.ground_truth_dir,
            model
        )
        print(f"✅ Dataset prepared with {len(self.dataset)} records")
        return self.dataset
    
    async def run_evaluation(self, name: str = "Notebook Evaluation"):
        """Run evaluation using prepared dataset."""
        if not self.dataset:
            raise ValueError("Dataset not prepared. Call prepare_dataset() first.")
        
        print(f"🔍 Running evaluation: {name}")
        result = await self.pipeline.create_and_run_eval(name, self.dataset)
        self.results[name] = result
        
        if result["status"] == "success":
            print(f"✅ Evaluation completed successfully!")
            print(f"📊 View results at: {result['report_url']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    def show_metrics(self):
        """Display evaluation metrics."""
        if not self.results:
            print("No evaluation results available. Run evaluation first.")
            return
        
        print("\n📊 Evaluation Results Summary:")
        print("=" * 40)
        from src.services.cost_analysis import summarize_costs_from_eval
        for name, result in self.results.items():
            print(f"\n🔍 {name}")
            if result["status"] == "success":
                print(f"   ✅ Status: Success")
                print(f"   📋 Eval ID: {result['eval_id']}")
                print(f"   🏃 Run ID: {result['run_id']}")
                print(f"   🔗 Report URL: {result['report_url']}")
                # Summarize costs if metrics are present
                if "metrics" in result:
                    summary = summarize_costs_from_eval(result)
                    print(f"   💰 Total Cost: ${summary['total_cost']:.2f}")
                    print(f"   📈 System Metrics: {summary['system_metrics']}")
                    print(f"   FP Rate: {summary['fp_rate']:.3f}, FN Rate: {summary['fn_rate']:.3f}")
            else:
                print(f"   ❌ Status: Failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")


async def quick_eval(model: str = "gpt-4o-mini", name: str = "Quick Evaluation") -> NotebookEvaluator:
    """Quick evaluation function for notebook usage."""
    evaluator = NotebookEvaluator()
    await evaluator.prepare_dataset(model)
    await evaluator.run_evaluation(name)
    return evaluator


# Convenience functions for notebook usage
async def create_dataset_for_model(model: str = "gpt-4o-mini") -> List[Dict]:
    """Create dataset using create_dataset_content - convenience function."""
    pipeline = EvaluationPipeline()
    return await pipeline.create_dataset_content(
        Path("scripts/data/test"),
        Path("scripts/data/ground_truth"), 
        model
    )


async def run_quick_evaluation(name: str, model: str = "gpt-4o-mini") -> Dict:
    """Run a quick evaluation - convenience function."""
    pipeline = EvaluationPipeline()
    dataset = await pipeline.create_dataset_content(
        Path("scripts/data/test"),
        Path("scripts/data/ground_truth"),
        model
    )
    return await pipeline.create_and_run_eval(name, dataset)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Method 1: Quick evaluation
        evaluator = await quick_eval("gpt-4o-mini", "Test Run")
        evaluator.show_metrics()
        
        # Method 2: Step by step
        # evaluator = NotebookEvaluator()
        # await evaluator.prepare_dataset("gpt-4o-mini")
        # await evaluator.run_evaluation("Detailed Test")
        # evaluator.show_metrics()
    
    asyncio.run(main())
