"""Evaluation pipeline following the notebook pattern."""
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

from openai import AsyncOpenAI
from src.models.receipt import ReceiptDetails
from src.models.audit import AuditDecision, EvaluationRecord
from src.services.extraction import ExtractionService
from src.services.audit import AuditService
from src.core.config import settings


class EvaluationPipeline:
    """Pipeline for running evaluations following the notebook pattern."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.extraction_service = ExtractionService()
        self.audit_service = AuditService()
    
    async def create_evaluation_record(
        self,
        image_path: Path,
        ground_truth_dir: Path,
        model: str = "gpt-4o-mini"
    ) -> EvaluationRecord:
        """Create a complete evaluation record for a receipt."""
        # Load ground truth
        extraction_path = ground_truth_dir / "extraction" / f"{image_path.stem}.json"
        correct_details = ReceiptDetails.model_validate_json(extraction_path.read_text())
        
        audit_path = ground_truth_dir / "audit_results" / f"{image_path.stem}.json"
        correct_audit = AuditDecision.model_validate_json(audit_path.read_text())
        
        # Generate predictions
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        predicted_details = await self.extraction_service.extract_receipt_details(
            image_data, image_path.name, model=model
        )
        predicted_audit = await self.audit_service.audit_receipt(
            predicted_details, model=model
        )
        
        return EvaluationRecord(
            receipt_image_path=str(image_path.name),
            correct_receipt_details=correct_details,
            predicted_receipt_details=predicted_details,
            correct_audit_decision=correct_audit,
            predicted_audit_decision=predicted_audit,
        )
    
    async def create_dataset_content(
        self,
        receipt_image_dir: Path,
        ground_truth_dir: Path,
        model: str = "gpt-4o-mini"
    ) -> List[Dict]:
        """Create dataset content following notebook format."""
        tasks = [
            self.create_evaluation_record(image_path, ground_truth_dir, model)
            for image_path in receipt_image_dir.glob("*.jpg")
        ]
        records = await asyncio.gather(*tasks)
        
        # Format for OpenAI Evals
        return [{"item": record.model_dump()} for record in records]
    
    def get_graders(self) -> List[Dict]:
        """Get all graders as defined in the notebook."""
        # Use the comprehensive graders from graders.py
        from src.utils.graders import get_all_graders
        return get_all_graders()
    
    async def create_and_run_eval(
        self,
        name: str,
        dataset: List[Dict],
        graders: Optional[List[Dict]] = None
    ) -> Dict:
        """Create and run evaluation on OpenAI platform."""
        if graders is None:
            graders = self.get_graders()
        
        try:
            # Create eval (with caching behavior like notebook)
            eval_cfg = await self._create_eval_cached(name, graders)
            
            # Run eval
            eval_run = await self.client.evals.runs.create(
                name=f"{name}-run",
                eval_id=eval_cfg.id,
                data_source={
                    "type": "jsonl",
                    "source": {"type": "file_content", "content": dataset},
                },
            )
            
            print(f"Evaluation run created: {eval_run.id}")
            print(f"View results at: {eval_run.report_url}")
            
            return {
                "eval_id": eval_cfg.id,
                "run_id": eval_run.id,
                "report_url": eval_run.report_url,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_eval_cached(self, name: str, graders: List[Dict]):
        """Create eval with caching like the notebook."""
        # Simple in-memory cache to avoid creating duplicate evals
        cache_key = f"{name}_{hash(str(graders))}"
        if not hasattr(self, '_eval_cache'):
            self._eval_cache = {}
        
        if cache_key in self._eval_cache:
            print(f"Using cached eval: {self._eval_cache[cache_key].id}")
            return self._eval_cache[cache_key]
        
        eval_cfg = await self.client.evals.create(
            name=name,
            data_source_config={
                "type": "custom",
                "item_schema": EvaluationRecord.model_json_schema(),
                "include_sample_schema": False,  # Don't generate new completions.
            },
            testing_criteria=graders,
        )
        print(f"Created new eval: {eval_cfg.id}")
        
        self._eval_cache[cache_key] = eval_cfg
        return eval_cfg
