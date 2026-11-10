---
name: ai_newsletter
track: bonus
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [topic, timeframe, max_items]
outputs: [topic, timeframe, markdown, item_count, items, error, message]
side_effect: false
---
# ai_newsletter

Uses the existing Tavily news search and Markdown digest formatter. Pass a
topic, timeframe, and maximum number of items. Each included item links to
its source. The digest uses search excerpts, so it can contain fewer items
than requested when usable results are limited.
