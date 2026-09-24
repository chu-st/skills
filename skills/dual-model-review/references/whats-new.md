# What's new in 0.3.0

- The existing `dual-model-review` skill now supports two or three participants.
- Configure **orchestrator**, **second**, and optional **third** in setup mode.
  Providers, products, and model choices are user preferences, not package policy.
- Store preferences outside the installation; updates preserve them. Task choices
  override saved preferences. Two remains the fallback count.
- The optional `scripts/configure.py` creates, validates, and resolves profiles.
  It makes no model calls; `peer.py` remains a one-peer transport.
- The third receives a neutral first brief, or is explicitly labelled as an
  informed review when added to an existing debate. Evidence outranks votes.
- Preserve roles, selected products, completed responses, and honest incomplete
  status when access or identity verification is missing.
- Gemini and other providers can use available tools, configured generic CLI
  adapters, or manual handoff. No native Gemini adapter is bundled.
- Existing skill invocations, two-model requests, and peer receipts remain valid.

See [configuration.md](configuration.md) for setup and migration.
