---
description: CLI entry point and Hostinger VPS deployment
globs: main.py, Procfile, .streamlit/config.toml
alwaysApply: false
---

id: "TASK-009"
title: "CLI entry point + deploy to Hostinger VPS"
status: "done"
priority: "P1"
labels: ["cli", "deployment", "vps"]
dependencies: ["tasks/TASK-007-orchestrator.md", "tasks/TASK-008-streamlit-ui.md"]
created: "2026-03-28"

# 1) High-Level Objective

Complete main.py CLI (runs full pipeline, prints JSON), configure Streamlit for production, push to GitHub, and deploy to Hostinger VPS (72.61.143.225) as a systemd service.

# 2) Background / Context

VPS: 72.61.143.255, root access via SSH. GitHub repo: github.com/LeonidSvb/signal-finder-LM. Streamlit runs on port 8501, exposed via nginx reverse proxy on a subdomain. Deployment is manual (SSH + git pull + restart service) — no CI/CD in MVP.

# 3) Assumptions & Constraints

- ASSUMPTION: nginx already running on VPS (shared with n8n setup)
- Constraint: Streamlit port 8501, nginx proxies subdomain → localhost:8501
- Constraint: App runs as systemd service for auto-restart
- Constraint: No Docker in MVP

# 4) Dependencies

- TASK-007 (orchestrator complete)
- TASK-008 (UI complete)

# 5) Context Plan

**Beginning:**
- main.py _(read-only — stub from TASK-001)_
- config/settings.py _(read-only)_

**End state:**
- main.py (complete)
- .streamlit/config.toml
- requirements.txt (finalized)

# 6) Low-Level Steps

1. **Complete main.py**

   - File: `main.py`
   - Contents:
     ```python
     import argparse
     import json
     from core.orchestrator import generate_icp_only, run_full_analysis
     from utils.formatter import report_to_dict

     def main():
         parser = argparse.ArgumentParser(description="Signal Finder CLI")
         parser.add_argument("--url", required=True, help="Company website URL")
         parser.add_argument(
             "--icps",
             default="0,1",
             help="Comma-separated ICP indices to select (default: 0,1)"
         )
         args = parser.parse_args()
         indices = [int(i) for i in args.icps.split(",")]
         report = run_full_analysis(args.url, indices)
         print(json.dumps(report_to_dict(report), indent=2))

     if __name__ == "__main__":
         main()
     ```

2. **Create .streamlit/config.toml**

   - File: `.streamlit/config.toml`
   - Contents:
     ```toml
     [server]
     port = 8501
     headless = true
     address = "0.0.0.0"

     [theme]
     base = "light"
     primaryColor = "#2563EB"
     backgroundColor = "#FFFFFF"
     secondaryBackgroundColor = "#F8FAFC"
     textColor = "#0F172A"
     font = "sans serif"
     ```

3. **Create systemd service file (to run on VPS)**

   - File: `signal-finder.service` (reference file — not deployed automatically)
   - Contents:
     ```ini
     [Unit]
     Description=Signal Finder Streamlit App
     After=network.target

     [Service]
     User=root
     WorkingDirectory=/root/signal-finder-LM
     ExecStart=/usr/local/bin/streamlit run ui/streamlit_app.py
     Restart=always
     RestartSec=5

     [Install]
     WantedBy=multi-user.target
     ```

4. **Deployment steps (manual, run on VPS via SSH)**

   On VPS (72.61.143.225):
   ```bash
   cd /root
   git clone https://github.com/LeonidSvb/signal-finder-LM
   cd signal-finder-LM
   pip install -r requirements.txt
   cp signal-finder.service /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable signal-finder
   systemctl start signal-finder
   ```

   Nginx config (add to existing nginx setup):
   ```nginx
   server {
       listen 80;
       server_name signals.systemhustle.com;
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

# 7) Types & Interfaces

N/A

# 8) Acceptance Criteria

- `python main.py --url="https://systemhustle.com" --icps="0,1"` prints valid JSON report
- `streamlit run ui/streamlit_app.py` starts without errors with config.toml applied
- On VPS: `systemctl status signal-finder` shows active (running)
- Subdomain resolves and shows the Streamlit app

# 9) Testing Strategy

- Local: run CLI with systemhustle.com — verify JSON output is complete
- Local: run streamlit — verify UI loads at localhost:8501
- VPS: after deploy, open subdomain in browser — verify full flow works end-to-end

# 10) Notes

- VPS credentials: host=72.61.143.225, user=root (see project .env)
- GitHub repo: https://github.com/LeonidSvb/signal-finder-LM
- After first deploy: update via `git pull && systemctl restart signal-finder`
