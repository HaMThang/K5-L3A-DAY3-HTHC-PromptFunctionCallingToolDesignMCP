---
name: cite_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [claims]
outputs: [status, citations, unsupported, error, message]
side_effect: false
---
# cite_sources

Matches evidence quotes to the collected source text from `lookup`, `fetch`,
`papers`, or `paper_text`. Each claim supplies `claim`, `url`, and `quote`.
The chat runner supplies the source items from the current request.

The URL must match a collected item and the quote must occur in its summary,
with whitespace normalized. A match establishes that the text appears in the
collected result. Read the surrounding context to assess whether it supports
the claim.
