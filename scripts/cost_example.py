from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.cost_calculator import calculate_costs

# first_ai_system_cost = calculate_costs(
#     fp_rate=1 / 12, fn_rate=1 / 8, per_receipt_cost=0.04671
# )

# print(f"First version of our system, estimated cost: ${first_ai_system_cost:,.0f}")

system_cost_4_1_mini = calculate_costs(
    fp_rate=1 / 12, fn_rate=0, per_receipt_cost=0.003
)

print(f"Cost using gpt-4.1-mini: ${system_cost_4_1_mini:,.0f}")