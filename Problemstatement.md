# Weekly Product Review Pulse - Problem Statement

**Objective**
We are building an **AI Agent** that acts as an automated weekly “pulse” to turn public App Store and Google Play reviews for selected fintech products into a one-page insight report. The AI Agent will use the **Model Context Protocol (MCP)** to autonomously access tools for Google Workspace. Specifically, the agent will use MCP tools to append the generated report to a Google Doc and send stakeholder emails via Gmail. Writes to Google Docs and Gmail must go through dedicated MCP servers—not ad hoc API calls inside the agent.

**Supported products (initial):** INDMoney, Groww, PowerUp Money, Wealth Monitor, Kuvera.

---

**What the AI Agent does**
1. **Ingest**: Ingest public reviews from the last 8–12 weeks (configurable window) from both Apple App Store (e.g., iTunes customer-reviews RSS) and Google Play (scraper-based), per product.
2. **Reasoning & Tool Use**: The AI Agent orchestrates the workflow. It uses embeddings and density-based clustering (e.g., UMAP + HDBSCAN) to cluster feedback, and then uses its LLM capabilities to name themes, pull verbatim quotes, and propose action ideas—with validation so quotes must appear in real review text.
3. **Report Generation**: The Agent renders a concise one-page narrative: top themes, quotes, action ideas, and a short “who this helps” section.
4. **Deliver via MCP**: The AI Agent uses the Model Context Protocol to invoke tools exposed by Google Workspace MCP servers:
   - **Google Docs MCP Tool**: The Agent calls an MCP tool to append each week’s report as a new dated section to a single running Google Doc per product (e.g., Weekly Review Pulse — Groww). The Doc is the system of record and preserves history.
   - **Gmail MCP Tool**: The Agent calls an MCP tool to send a short stakeholder email that includes a deep link to the new section in that Doc (heading link), not a duplicate full report in email alone.

---

**Key Requirements**
- **AI Agent Orchestration**: The core system is an LLM-driven AI Agent equipped with data ingestion and MCP delivery tools.
- **MCP-based Delivery**: Append to the shared Google Doc and send Gmail only via the respective MCP servers' tools. The Agent is an MCP host/client; it does not embed Google credentials.
- **Weekly Cadence**: Scheduled job Monday morning IST, with a CLI for backfill of any ISO week.
- **Idempotent Runs**: Re-running the same product + ISO week must not create duplicate Doc sections or duplicate sends. 
- **Auditable & Safe**: Each run records delivery identifiers and scrubs PII before generating the pulse.

**Success Criteria (high level)**
End-to-end run features an AI Agent that successfully produces a grounded one-page pulse and uses MCP tools to update the Google Doc and send an email idempotently per product + week. Architecture and implementation plan traceability: every requirement maps to modules, MCP usage, and phased exit criteria.
