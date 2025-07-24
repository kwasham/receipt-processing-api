# Receipt Processing Evaluation System

This project now includes a comprehensive evaluation system that incorporates all the evaluation logic from the notebook, including:

- **OpenAI Evals API Integration**: Full integration with OpenAI's evaluation platform for business analytics
- **Extraction Graders**: Evaluate accuracy of receipt field extraction
- **Item Extraction Graders**: Evaluate line item extraction quality
- **Audit Graders**: Evaluate audit decision accuracy
- **Reasoning Graders**: Evaluate quality of audit reasoning
- **Business Cost Analysis**: Calculate potential cost savings

## Key Features

### 1. OpenAI Evals API Integration

**Primary Feature**: The system is designed to use OpenAI's Evals API for comprehensive business analytics:

- **Professional Dashboard**: Access detailed evaluation results through OpenAI's web interface
- **Advanced Grading**: Leverages OpenAI's sophisticated grading algorithms
- **Scalable Analytics**: Handle large datasets with cloud-based processing
- **Business Reporting**: Generate professional reports for stakeholders
- **Graceful Fallback**: Enhanced local evaluation when API is unavailable

### 2. Improved Audit Prompts

- Basic and improved audit prompts with few-shot examples
- Enhanced travel-related expense detection
- Better math error detection with tolerance

### 3. Comprehensive Evaluation Pipeline

- **OpenAI Evals Integration**: Primary evaluation method using OpenAI's platform
- Automated dataset generation from images and ground truth
- Local evaluation with business impact metrics (fallback)
- Model comparison capabilities
- Cost analysis with realistic business assumptions

### 4. Multiple Usage Options

#### Command Line Interface

```bash
# Run evaluation
python -m src.cli evaluate --model gpt-4o-mini --eval-name "Test Run"

# Compare models
python -m src.cli compare-models -m gpt-4o-mini -m gpt-4o-mini

# Run existing dataset
python -m src.cli run-eval --dataset data/evaluation_dataset.jsonl
```

#### Python Script

```bash
# Run full evaluation
python scripts/run_eval.py --name "Full Evaluation"

# Compare models
python scripts/run_eval.py --compare-models
```

#### Interactive Notebook

```python
from scripts.notebook_eval import quick_eval, NotebookEvaluator

# Quick evaluation
evaluator = await quick_eval("gpt-4o-mini")

# Detailed evaluation
evaluator = NotebookEvaluator()
await evaluator.prepare_dataset()
await evaluator.run_evaluation()
evaluator.show_metrics()
```

### 4. OpenAI Evals API Integration

**For Business Analytics**: The system integrates with OpenAI's Evals API to provide professional-grade evaluation and reporting:

#### Features:

- **Cloud-based Processing**: Handle large evaluation datasets
- **Professional Dashboard**: Access results through OpenAI's web interface
- **Advanced Grading**: Sophisticated evaluation algorithms
- **Business Reports**: Generate stakeholder-ready analytics
- **Scalable Architecture**: Enterprise-grade evaluation infrastructure

#### Sample Integration Output:

```
=== OpenAI Evals Integration Results ===
Status: success
Eval ID: eval_receipt_processing_test
Run ID: run_eval_receipt_processing_test
Report URL: https://platform.openai.com/evals/eval_id/runs/run_id
OpenAI Dashboard: https://platform.openai.com/evals/eval_id

✅ OpenAI Evals API integration working
📊 Professional analytics available at report URL
💼 Business dashboard ready for stakeholder review
```

#### Test Integration:

```bash
# Test OpenAI Evals API integration
python scripts/test_openai_integration.py
```

### 5. Business Impact Analysis

The system automatically calculates:

- **Accuracy metrics**: Precision, recall, F1 score
- **Error rates**: False positive and false negative rates
- **Cost projections**: Annual costs for different systems
- **Potential savings**: Comparison with current manual processes

Example output:

```
=== Business Impact Analysis ===
Samples analyzed: 25
True Positives: 8, False Positives: 2
True Negatives: 13, False Negatives: 2
False Positive Rate: 13.33%
False Negative Rate: 20.00%

Estimated Annual Costs:
  Current System: $270,000
  AI System: $156,000
  Perfect System: $110,000
  Potential Savings: $114,000
```

## File Structure

```
src/
├── prompts/
│   └── audit_prompts.py          # Basic and improved audit prompts
├── services/
│   ├── audit.py                  # Enhanced audit service with examples
│   ├── evaluation.py             # All grader configurations
│   └── evaluation_pipeline.py    # Full evaluation pipeline
├── utils/
│   └── cost_calculator.py        # Business cost calculations
└── cli.py                        # Command line interface

scripts/
├── run_eval.py                   # Standalone evaluation script
└── notebook_eval.py              # Jupyter notebook helpers
```

## Evaluation Graders

### Extraction Graders

- Merchant name accuracy (text similarity)
- Location fields (exact match)
- Time accuracy
- Financial amounts (subtotal, tax, total)
- Handwritten notes (fuzzy matching)

### Item Extraction Graders

- Missed line items detection
- Extra line items detection
- Item extraction quality (0-10 scale)

### Audit Graders

- Individual criteria accuracy (travel-related, amount, math, handwritten X)
- Overall audit decision accuracy

### Reasoning Graders

- Audit reasoning quality evaluation
- Logical soundness assessment
- Comprehensiveness scoring

## Usage Examples

### 1. Run a comprehensive evaluation:

```bash
python scripts/run_eval.py --name "Comprehensive Test" --image-dir scripts/data/test --ground-truth-dir scripts/data/ground_truth
```

### 2. Compare different models:

```bash
python scripts/run_eval.py --compare-models
```

### 3. Use in a notebook:

```python
# In a Jupyter notebook
from scripts.notebook_eval import NotebookEvaluator
import asyncio

evaluator = NotebookEvaluator()
await evaluator.prepare_dataset()
await evaluator.run_evaluation("My Test")
evaluator.show_metrics()
```

### 4. Run via CLI:

```bash
python -m src.cli evaluate --model gpt-4o-mini --eval-name "CLI Test"
```

## Installation

Install additional dependencies:

```bash
pip install -r requirements.txt
```

Make sure you have:

- OpenAI API key set in your environment
- Test images in `scripts/data/test/`
- Ground truth files in `scripts/data/ground_truth/`

## Configuration

The system uses the existing configuration from `src/core/config.py`. Make sure your OpenAI API key is properly configured.

## Results

Results are automatically saved to `data/evaluation_results/` with timestamps and detailed metrics including cost analysis and performance measurements.
