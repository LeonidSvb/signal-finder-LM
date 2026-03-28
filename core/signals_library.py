from core.models import Signal

SIGNALS_LIBRARY: list[Signal] = [
    Signal(
        name="Hiring Spike",
        description="Multiple roles opened within a short period (5-20+), indicating internal recruiting capacity is overloaded",
        category="late",
        searchable=False,
        sources=["LinkedIn Jobs", "Indeed"],
    ),
    Signal(
        name="Long-Open Roles",
        description="Roles open for 30+ days, signaling the company cannot close positions and has high readiness to pay for help",
        category="late",
        searchable=False,
        sources=["LinkedIn Jobs", "Indeed"],
    ),
    Signal(
        name="Leadership Change",
        description="New Head of Talent, VP Engineering, Head of Sales, COO or similar senior leader hired — new leaders want quick results and are open to new vendors",
        category="structural",
        searchable=True,
        sources=["LinkedIn", "news"],
    ),
    Signal(
        name="Funding Event",
        description="Company raised investment (Seed, Series A-C) — growth phase requires rapid team expansion",
        category="early",
        searchable=True,
        sources=["Crunchbase", "news"],
    ),
    Signal(
        name="Geographic Expansion",
        description="Company opening new offices or entering new markets — requires local hiring",
        category="early",
        searchable=True,
        sources=["news", "press releases"],
    ),
    Signal(
        name="Mergers and Acquisitions",
        description="Company merged with or acquired another — team restructuring creates new roles",
        category="structural",
        searchable=True,
        sources=["news"],
    ),
    Signal(
        name="New Product or Business Unit Launch",
        description="Company launching a new product line or division — new specialists required",
        category="early",
        searchable=True,
        sources=["company blog", "news"],
    ),
    Signal(
        name="Role-Specific Hiring Surge",
        description="10+ open roles in one function (e.g. sales, engineering) — signals strategic hiring push",
        category="late",
        searchable=False,
        sources=["job boards"],
    ),
    Signal(
        name="Career Page Expansion",
        description="Company updated careers page with new categories or significantly more listings — indicates systematic hiring",
        category="late",
        searchable=False,
        sources=["company website"],
    ),
    Signal(
        name="Public Hiring Announcements",
        description="CEO or HR posting 'we are hiring' publicly — indicates openness to outreach and active hiring mode",
        category="late",
        searchable=True,
        sources=["LinkedIn"],
    ),
    Signal(
        name="High Turnover",
        description="Frequent employee changes visible on LinkedIn — creates constant demand for new hires",
        category="structural",
        searchable=False,
        sources=["LinkedIn"],
    ),
    Signal(
        name="Compliance or Regulatory Pressure",
        description="New compliance requirements (especially in healthcare or finance) drive urgent hiring of specialized roles",
        category="structural",
        searchable=True,
        sources=["regulatory news"],
    ),
    Signal(
        name="New Large Contract",
        description="Company signed a major contract — needs to quickly scale team to deliver",
        category="early",
        searchable=True,
        sources=["news"],
    ),
    Signal(
        name="Tech Stack Change",
        description="Company adopting new technologies — requires specialists not available internally",
        category="structural",
        searchable=True,
        sources=["engineering blogs", "news"],
    ),
    Signal(
        name="Layoffs Rebuild Phase",
        description="Company that recently did layoffs is now rehiring key roles — high urgency, selective placement",
        category="structural",
        searchable=True,
        sources=["news"],
    ),
]


def get_all_signals() -> list[Signal]:
    return SIGNALS_LIBRARY


def get_searchable_signals() -> list[Signal]:
    return [s for s in SIGNALS_LIBRARY if s.searchable]


def get_signal_by_name(name: str) -> Signal | None:
    name_lower = name.lower().strip()
    for s in SIGNALS_LIBRARY:
        if s.name.lower() == name_lower:
            return s
    return None


def signals_as_context_string() -> str:
    lines = ["AVAILABLE SIGNALS LIBRARY (use only these names in your output):\n"]
    for s in SIGNALS_LIBRARY:
        searchable_label = "searchable via web" if s.searchable else "manual research only"
        lines.append(f'- "{s.name}" [{s.category}] [{searchable_label}]: {s.description}')
    return "\n".join(lines)
