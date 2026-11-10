---
name: google_maps
track: bonus
kind: local_formatter
requires_env: []
inputs: [place]
outputs: [place, url, error, message]
side_effect: false
---
# google_maps

Builds a Google Maps search link for a specific place or address. Include the
city or verified street address when available to narrow the search. The tool
encodes the query locally. Google Maps resolves the search when the link opens.
