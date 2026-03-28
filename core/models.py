from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ICP:
    role: str
    company_type: str
    industry: str
    geography: Optional[str] = None


@dataclass
class Signal:
    name: str
    description: str
    category: str
    searchable: bool
    sources: list[str]


@dataclass
class ICPSignals:
    icp: ICP
    signals: list[Signal]
    hidden_signals: list[Signal]


@dataclass
class Company:
    name: str
    signal: str
    explanation: str
    source_url: str = ""
    icp_ref: str = ""


@dataclass
class ActionPlan:
    who_to_target: list[str]
    where_to_find: list[str]
    outreach_angles: list[str]


@dataclass
class Report:
    icp_list: list[ICP]
    icp_signals: list[ICPSignals]
    companies: list[Company]
    insight: str
    action_plan: ActionPlan
    cta_url: str
