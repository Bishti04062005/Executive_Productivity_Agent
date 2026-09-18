
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models import Action
from processor import process_actions


actions = [
    Action(
        id="ACTION-001",
        description="Send updated vendor list to Raghav",
        owner="Arjun Malhotra",
        owner_type="executive",
        status="open",
        due_date="2026-09-22",
        waiting_on=None,
        people=["Raghav Sethi"],
        source_id="MEETING-001",
        evidence="I will send the updated vendor list.",
        uncertainty=None
    ),
    Action(
        id="ACTION-002",
        description="Confirm owner of Mumbai office renewal",
        owner=None,
        owner_type="unclear",
        status="open",
        due_date="2026-09-25",
        waiting_on=None,
        people=["Facilities"],
        source_id="MEETING-002",
        evidence="Not sure whose desk this is on.",
        uncertainty="Ownership unclear"
    )
]


result = process_actions(
    actions,
    as_of_date="2026-09-23"
)


print("Processing successful!")
print("Total actions:", len(result["all_actions"]))
print("My actions:", len(result["my_actions"]))
print("Waiting on others:", len(result["waiting_on_others"]))
print("Unclear ownership:", len(result["unclear_ownership"]))
print("Overdue:", len(result["overdue"]))
print("Due today:", len(result["due_today"]))
print("Upcoming:", len(result["upcoming"]))