# Telemetry & Observability Events

Emit line-delimited JSON (NDJSON):

- `turn_receipt` (schema: turn_receipt.schema.json)
- `consent_log` (schema: consent_log.schema.json)
- `grounding_box_snapshot` (entire GroundingBox object occasionally)
- `error_classified` { "class": <enum>, "primary_fix": "...", "fallback": "..." }
- `source_provenance` { "count": N, "jurisdictions": [...], "recency_days": X }

**PII caution:** Do not log full documents; log stable identifiers.
