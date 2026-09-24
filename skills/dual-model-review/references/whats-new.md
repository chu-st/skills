# What's new

## 0.3.1

- Following a real Claude Fable review, `plan --host-file` can fill an unspecified
  orchestrator from known host facts without replacing selected roles.
- `init --project` creates the profile in that explicit project even when an
  environment profile selector is set. Read precedence is unchanged.
- Clarified relay-only hosts, runtime identity checks, and future-schema errors.
- Added regression checks for role preservation and profile creation destinations.
  The model reviewed the original four core files; patched behavior is covered by
  automated tests. No live three-model run is claimed.

## 0.3.0

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
