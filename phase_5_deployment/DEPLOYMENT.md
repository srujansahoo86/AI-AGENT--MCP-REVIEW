# Deployment Guide - Weekly Product Review Pulse

This document outlines how to deploy the AI Agent for scheduled execution.

## 1. GitHub Actions Setup

The system is configured to run automatically every Monday morning via GitHub Actions.

### Required Secrets
Go to your GitHub Repository **Settings > Secrets and variables > Actions** and add the following:

- `GROQ_API_KEY`: Your Groq API key for the Llama model.
- `MCP_SERVER_URL`: The URL of your external MCP server (e.g., hosted on Render).
- `STAKEHOLDER_EMAIL`: Default recipient email for the weekly report.
- `DEFAULT_DOC_ID`: The target Google Doc ID where reports should be appended.

## 2. Local Monitoring & Auditing

### Viewing Logs
Logs are stored in the `logs/pulse.log` file at the root of the project. This file tracks:
- Start/Stop of each run.
- Tool call success/failures.
- Detailed error tracebacks.

### Running Audits
To see a summary of all past runs (idempotency checks):
```powershell
cd phase_5_deployment
python audit.py
```

## 3. Production Considerations
- **PII Scrubbing**: Ensure the `PIIScrubber` in Phase 2 is correctly configured for your regional data.
- **MCP Server Health**: If the external MCP server is down, the agent will log the failure and the run will be marked as `failed` in the database, allowing for a manual retry via CLI.
