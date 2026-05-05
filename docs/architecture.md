# Weekly Product Review Pulse - AI Agent Architecture

This document defines the high-level architecture, component boundaries, and integration points for the Weekly Product Review Pulse system. The core of this system is an **AI Agent** that orchestrates the workflow and utilizes the Model Context Protocol (MCP) to access Google Workspace tools.

## 1. System Overview

The system is an LLM-driven AI Agent designed to ingest, reason over, summarize, and deliver public app store reviews for selected fintech products. It strictly adheres to the Model Context Protocol (MCP) for output delivery. The AI Agent acts as an MCP Client and connects to an external MCP server (link to be provided) to autonomously format and deliver its insights. 

**Supported Products:** INDMoney, Groww, PowerUp Money, Wealth Monitor, Kuvera.

## 2. Core Architecture

The architecture relies on an **Agentic Orchestration Pattern** (e.g., using LangGraph, CrewAI, or an LLM Tool-Calling loop). The AI Agent is equipped with a specific set of tools and a system prompt.

### 2.1 AI Agent Orchestrator
The central intelligence of the system.
- **Workflow:** The Agent is triggered via a scheduled job (e.g., Monday morning IST) or via a CLI for backfilling any specific ISO week. It receives the task: "Generate the weekly pulse for product X and deliver it via Google Docs and Gmail."
- **Execution Loop:** The Agent autonomously calls tools in sequence: `IngestData` -> `ClusterData` -> `GenerateReport` -> `ValidateQuotes` -> `AppendToGoogleDoc` -> `SendGmail`.
- **Reasoning & Validation:** The LLM generates a concise one-page narrative consisting of top themes, verbatim quotes, action ideas, and a short "who this helps" section based on the clustered feedback. A distinct validation step ensures that any quotes pulled by the LLM exactly match the real, raw review text to prevent hallucinations.

### 2.2 Ingestion Tools (Custom Agent Tools)
Tools provided to the Agent to fetch raw data.
- **Apple App Store Tool:** Parses iTunes customer-reviews RSS feeds over a configurable time window (e.g., last 8–12 weeks).
- **Google Play Store Tool:** Scrapes review endpoints using a dedicated scraping library over the same configurable time window.
- **Clustering Tool:** To avoid blowing up the context window, the Agent can invoke a clustering tool (using `umap-learn` and `hdbscan`) that groups semantically similar reviews into concise buckets, which the LLM then reads.

### 2.3 Delivery Tools (External MCP Server)
The AI Agent acts as an **MCP Client**. It connects to an external, pre-existing MCP server to perform side effects.
- **Google Docs MCP Tool:** The external server exposes an `append_section` tool. The Agent passes its generated Markdown report. The server handles authentication and appending, returning a `heading_anchor_id` or deep link to the Agent.
- **Gmail MCP Tool:** The external server exposes a `send_email` tool. The Agent passes an HTML teaser and the deep link. The server handles authentication and sending the email.

## 3. Idempotency & State Management

To ensure re-running the agent for a specific product and ISO week does not produce duplicate emails or Doc sections, an idempotency wrapper surrounds the Agent's execution.

**Execution Flow State Checks:**
1. System triggers Agent for `(Product X, ISO Week Y)`.
2. Checks local SQLite DB: `SELECT status FROM runs WHERE product='X' AND week='Y'`.
3. If `status == 'completed'`, the system exits safely.
4. If `status == 'pending'` or `missing`, the Agent is instantiated and prompted.
5. Upon successful completion of the MCP tools, the system saves the `heading_anchor_id` and `message_id`.
6. Marks run as `completed`.

## 4. Security & Credentials Boundaries

- **Core AI Agent:** Only stores API keys for the Orchestrator LLM (e.g., `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`), and any connection details required for the external MCP server. The Agent has no direct access to Google Credentials.
- **External MCP Server:** Handles all Google OAuth tokens and service account secrets.
- **Data Safety:** The Ingestion Tools scrub Personally Identifiable Information (PII) before the data enters the LLM context window.

## 5. Technology Stack Recommendations

- **AI Agent Orchestrator:** `Python` with `LangChain`, `LangGraph`, or `LlamaIndex` to manage the tool-calling loop.
- **Clustering & Embeddings:** `umap-learn`, `hdbscan`, and lightweight local embeddings or OpenAI embeddings.
- **Database:** `SQLite` (Lightweight, single-file, sufficient for run metadata).
- **MCP Client:** Python MCP SDK (e.g., `mcp`) to connect the Agent to the external MCP server.
