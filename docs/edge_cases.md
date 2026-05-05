# Weekly Product Review Pulse - Edge Cases

This document outlines potential edge cases, failure modes, and mitigation strategies for each phase of the Weekly Product Review Pulse system.

## Phase 1: Foundation & Custom Tools
**Edge Cases:**
- **Zero Reviews:** A product might receive zero reviews in the configurable 8-12 week window.
  - *Mitigation:* The agent should gracefully exit and log a "No new data" status without calling the downstream reasoning or MCP tools.
- **Store Scraper Rate Limits/Blocks:** Google Play Store scraper might get temporarily IP banned.
  - *Mitigation:* Implement exponential backoff, user-agent rotation, or utilize proxy services if rate limits become restrictive.
- **RSS Feed Changes:** Apple might change the structure of the iTunes RSS feed.
  - *Mitigation:* Add strict Pydantic validation on the incoming feed. If it fails, alert the maintainers immediately.

## Phase 2: Reasoning & Clustering
**Edge Cases:**
- **Single Massive Cluster:** All reviews are highly generic (e.g., "Good app"), causing HDBSCAN to fail to find distinct clusters.
  - *Mitigation:* The system prompt should instruct the LLM to handle "generic feedback" gracefully without forcing artificial themes.
- **Context Window Overflow:** An unusually high volume of long reviews exceeds the embedding model limits or downstream LLM context window even after clustering.
  - *Mitigation:* Implement aggressive text summarization at the cluster level before passing it to the final LLM reasoning step, or truncate the number of reviews per cluster.

## Phase 3: MCP Servers Integration
**Edge Cases:**
- **Google Doc Deletion/Permission Loss:** The target Google Doc for a product is deleted or the service account loses edit access.
  - *Mitigation:* The Docs MCP server should catch the 403/404 error and pass it back to the Agent. The Agent should log a critical failure and notify the admin via a fallback mechanism.
- **Gmail Bounce/Spam:** Automated emails get marked as spam by internal corporate filters.
  - *Mitigation:* Ensure SPF/DKIM/DMARC records are correctly configured for the sending domain. Keep the HTML payload minimal and avoid spam-trigger words.

## Phase 4: AI Agent Orchestration
**Edge Cases:**
- **Infinite Validation Loop:** The LLM persistently hallucinates quotes, causing the `ValidateQuotes` step to reject the output repeatedly.
  - *Mitigation:* Set a hard limit on validation retries (e.g., 3 retries). If it fails, fallback to generating a summary *without* verbatim quotes and append a disclaimer.
- **Tool-Calling Loop:** The Agent gets confused and repeatedly calls `IngestData` instead of progressing to the next step.
  - *Mitigation:* Impose a maximum step limit on the LangGraph/Orchestrator execution. 
- **Content Safety Filter Trip:** A user review contains highly toxic content that trips the LLM provider's safety filter, causing the API to refuse the request.
  - *Mitigation:* Catch the API error and either omit the offending cluster or rely on the PII/profanity scrubber in Phase 2 to filter toxic content beforehand.

## Phase 5: Staging & Production
**Edge Cases:**
- **Database Lock Conflicts:** If someone triggers the CLI backfill exactly when the CRON job is running, SQLite might lock.
  - *Mitigation:* Implement standard SQLite retry timeouts. Ensure each run uses a specific transaction for the `(product, week)` pair.
- **Silent Failures:** The GitHub Action or CRON job fails to start due to infrastructure issues (not code issues).
  - *Mitigation:* Implement a secondary watchdog monitor or "dead man's switch" that expects a ping every Monday; if missed, it alerts the developer.
