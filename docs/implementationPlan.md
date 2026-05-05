# Weekly Product Review Pulse - Implementation Plan

This document breaks down the execution of the Weekly Product Review Pulse system into phased deliverables.

## Phase 1: Foundation & Custom Tools
**Goal:** Setup the core Python project, database schema, and data extraction tools for the AI Agent.
1. Initialize the Python project and manage dependencies (e.g., `poetry` or `pip`).
2. Create SQLite database schema for tracking idempotency (`runs` table with `product`, `week`, `status`, `doc_id`, `message_id`).
3. Build the `ingestion` tools:
   - Implement `AppStoreIngestor` to parse iTunes RSS feeds.
   - Implement `PlayStoreIngestor` using `google-play-scraper`.
4. Create a unified output schema for raw reviews.
**Exit Criteria:** The custom ingestion tools can be successfully called to return a normalized list of reviews from both stores for the configurable window (e.g., 8-12 weeks).

## Phase 2: Reasoning & Clustering
**Goal:** Provide the AI Agent with tools to cluster raw reviews and extract insights.
1. Implement PII scrubbing logic.
2. Integrate a local embedding model or an API (e.g., OpenAI `text-embedding-3-small`) to generate review vectors.
3. Apply `umap-learn` and `hdbscan` to cluster the embeddings.
**Exit Criteria:** The clustering logic successfully groups a mock list of reviews into semantic buckets, ready for LLM consumption.

## Phase 3: External MCP Server Configuration
**Goal:** Configure the AI Agent to connect to an external Model Context Protocol (MCP) server provided by the user.
1. Receive the connection details (e.g., SSE URL or stdio command path) for the external MCP server.
2. Implement an MCP Client in the Python project to connect to this server.
3. Verify the external server exposes the required `append_section` and `send_email` tools.
**Exit Criteria:** The Python project can successfully establish a connection to the external MCP server and list its available tools.

## Phase 4: AI Agent Orchestration
**Goal:** Build the LLM AI Agent to orchestrate the pipeline and use the tools provided by the external MCP server.
1. Implement the AI Agent orchestrator using a raw tool-calling loop powered by the Groq API (e.g., using a Llama 3 model) for ultra-fast reasoning.
2. Equip the Groq-powered Agent with the custom ingestion tools and connect it as an MCP Client to the external MCP server.
3. Craft the system prompt instructing the Agent on how to fetch data, cluster it, format the pulse report (themes, verbatim quotes, action ideas, "who this helps"), validate verbatim quotes against raw text, and deliver it via the MCP tools.
4. Integrate the SQLite idempotency checks into the execution flow.
5. Implement a CLI to trigger the Agent for specific products and ISO weeks.
**Exit Criteria:** End-to-end run features the AI Agent autonomously fetching data, reasoning, appending to the Google Doc, and sending an email. A repeated run for the same week does nothing.

## Phase 5: Staging & Production
**Goal:** Deploy the solution for scheduled execution.
1. Set up a Cron job or scheduled action (e.g., GitHub Actions) to run every Monday morning.
2. Add comprehensive logging and auditing.
3. Switch email from "draft-only" to "send" after final stakeholder approval.
**Exit Criteria:** The AI Agent runs autonomously in production without manual intervention.
