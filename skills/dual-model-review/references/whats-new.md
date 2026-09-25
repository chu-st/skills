# What's new

## 0.4.0

- Select two/three participants independently of short/full cycles; old profiles
  keep the short default without a rewrite.
- Full investigation includes mutual critiques, author revisions, material
  disagreement resolution, one common draft and independent closing checks.
  Existing artifacts instead use reviews, a designated author's revision and checks.
- Resolve disputes with discriminating evidence or the user's actual criteria;
  a bounded cooperative round may propose checks or better options. Preserve
  supported dissent; the third never decides by vote. See [disagreements.md](disagreements.md).
- Interpret ordinary requests for a multi-model run, research or work; preserve
  the deliverable and do not mistake product comparison for collaboration.
- Conversational setup supports viewing, swapping and saving roles, temporary
  choices and explicit access checks. Show access observations separately from
  expected routes and model identity. Users need not edit JSON.
- The optional helper adds backed-up `update --from-file`, `default_cycle` and
  temporary `plan --cycle`. An explicit project update never falls back to the
  user/environment profile. Model flags select a model but do not attest its identity.

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
