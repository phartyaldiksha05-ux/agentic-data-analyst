from agent.schemas import DatasetProfile
from agent.planner import RuleBasedPlanner

profile = DatasetProfile(
    dataset_name="sales.csv",
    rows=5000,
    duplicate_rows=5,
    columns=[
        {"name": "sales", "type": "numeric", "missing_count": 10, "unique_count": 4500},
        {"name": "region", "type": "categorical", "missing_count": 0, "unique_count": 5},
    ],
)
plan = RuleBasedPlanner().generate_plan(profile)
print(plan.model_dump_json(indent=2))
