# Weekly Product Review Pulse - Evaluations

This document outlines the evaluation strategy and testing criteria for each phase of the Weekly Product Review Pulse system.

## Phase 1: Foundation & Custom Tools
**Evaluations:**
- **Ingestion Normalization:** Write unit tests to ensure `AppStoreIngestor` and `PlayStoreIngestor` return identical schemas (e.g., `date`, `rating`, `review_text`, `version`).
- **Data Completeness:** Verify that the ingestors correctly fetch data across the full configurable window (e.g., exactly 8-12 weeks) and handle pagination if necessary.
- **Idempotency DB:** Unit test the SQLite CRUD operations. Ensure concurrent writes (if any) do not corrupt the single-file database.

## Phase 2: Reasoning & Clustering
**Evaluations:**
- **PII Scrubbing Validation:** Feed a synthetic dataset containing fake names, phone numbers, and emails. Verify the scrubber removes 100% of defined PII patterns.
- **Clustering Coherence:** Provide a mock dataset of 500 reviews with 5 distinct known themes. Evaluate if `umap-learn` and `hdbscan` correctly separate these into 5 distinct clusters without excessive noise.
- **Performance Benchmarks:** Measure the time and memory consumed to embed and cluster 10,000 reviews to ensure it runs within acceptable limits.

## Phase 3: MCP Servers Integration
**Evaluations:**
- **Docs MCP Tool Test:** Use the MCP Inspector to manually invoke `append_section`. Verify that the text is appended, headers are formatted correctly, and a valid deep link (anchor ID) is returned.
- **Gmail MCP Tool Test:** Use the MCP Inspector to manually invoke `send_email`. Verify the email is delivered to the test inbox, HTML formatting renders correctly, and the deep link correctly navigates to the Doc section.
- **Auth Token Lifecycle:** Manually revoke the OAuth token/credentials and verify the MCP servers surface a clear, actionable error message rather than silently failing.

## Phase 4: AI Agent Orchestration
**Evaluations:**
- **Quote Validation Accuracy:** Run a test where the LLM is prompted to intentionally hallucinate a quote. Assert that the validation step catches the hallucination and rejects it.
- **End-to-End Idempotency:** Run the agent orchestrator twice for "Groww, Week 42". Assert that the first run results in a Google Doc update and Email, and the second run exits safely with zero MCP tool calls.
- **Report Quality Assessment:** Perform a human-in-the-loop (HITL) review of the first 5 generated reports to score the themes, action ideas, and "who this helps" sections for relevance and clarity.

## Phase 5: Staging & Production
**Evaluations:**
- **Scheduler Reliability:** Monitor the CRON job/GitHub Action over a two-week period to ensure it fires exactly at Monday morning IST without manual intervention.
- **System Telemetry:** Track API costs (LLM tokens, embedding tokens) and end-to-end execution latency per product to establish a performance baseline.
