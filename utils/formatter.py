from core.models import Report


def report_to_dict(report: Report) -> dict:
    return {
        "icp_list": [
            {
                "role": icp.role,
                "company_type": icp.company_type,
                "industry": icp.industry,
                "geography": icp.geography,
            }
            for icp in report.icp_list
        ],
        "icp_signals": [
            {
                "icp": {
                    "role": ics.icp.role,
                    "company_type": ics.icp.company_type,
                    "industry": ics.icp.industry,
                },
                "signals": [
                    {"name": s.name, "description": s.description, "category": s.category, "searchable": s.searchable, "sources": s.sources}
                    for s in ics.signals
                ],
                "hidden_signals": [
                    {"name": s.name, "description": s.description, "category": s.category, "searchable": s.searchable, "sources": s.sources}
                    for s in ics.hidden_signals
                ],
            }
            for ics in report.icp_signals
        ],
        "companies": [
            {
                "name": c.name,
                "signal": c.signal,
                "explanation": c.explanation,
                "source_url": c.source_url,
                "icp_ref": c.icp_ref,
            }
            for c in report.companies
        ],
        "insight": report.insight,
        "action_plan": {
            "who_to_target": report.action_plan.who_to_target,
            "where_to_find": report.action_plan.where_to_find,
            "outreach_angles": report.action_plan.outreach_angles,
        },
        "cta_url": report.cta_url,
    }
