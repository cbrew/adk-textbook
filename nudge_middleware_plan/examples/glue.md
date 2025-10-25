# Framework-agnostic glue (pseudocode + minimal Python)

## Pseudocode wrapper for a tool call
def with_plan_gate(plan_text, act_fn, short_run=None):
    PLAN = plan_text  # emit to user; wait for 'OK' or 'SHORT'
    decision = get_user_decision()  # 'OK' | 'SHORT' | 'CANCEL'
    if decision == 'CANCEL':
        emit_receipt(step='cancelled', delta='User cancelled', next='None')
        return
    cfg = short_run if decision == 'SHORT' else None
    result = act_fn(config=cfg)
    update_grounding_box_from(result)
    emit_receipt(step='act', delta=describe_delta(result), next=next_action())

## Minimal Python Grounding store (illustrative)
from dataclasses import dataclass, field
from typing import List, Dict, Any
import json, datetime

@dataclass
class GroundingBox:
    goal: str
    stage: str
    progress: Dict[str,int]
    assumptions: List[str] = field(default_factory=list)
    open_items: List[str] = field(default_factory=list)
    next_action: Dict[str,str] = field(default_factory=lambda: {"owner":"unassigned","verb":"TBD","due":"TBD"})

class Store:
    def __init__(self):
        self.box = GroundingBox(goal="Unspecified", stage="Init", progress={"k":0,"n":1})
        self.receipts = []

    def update(self, **delta):
        changed = []
        for k,v in delta.items():
            if getattr(self.box, k) != v:
                setattr(self.box, k, v); changed.append(k)
        receipt = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "step":"update",
            "delta": f"Changed: {', '.join(changed) or 'none'}",
            "next": f"{self.box.next_action.get('owner','?')} → {self.box.next_action.get('verb','?')} by {self.box.next_action.get('due','TBD')}"
        }
        self.receipts.append(receipt)
        return receipt
