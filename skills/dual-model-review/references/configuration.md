# Model preferences and setup

This is a mode of `dual-model-review`, not a second skill and not a provider API.
The agent can configure it conversationally; the optional `scripts/configure.py`
helper creates, validates, and resolves a JSON profile without calling any models.

## Setup conversation

Use choices already stated by the user. Ask only for missing preferences: who
orchestrates, who is second, an optional third, and whether the default count is
two or three. If no count is requested, retain the existing count or use two.
Keep a selected model within a product when the user has not named a version;
do not invent an exact ID. A product preference and a model identity are separate.

Save only on a setup/update request. Ordinary task overrides are temporary unless
the user asks to remember them. Summarize the saved roles, default count, and path.
Saving a preference does not prove account access, authentication, or availability.
Do not collect credentials. Never add a person's private profile to the public skill.

## Where the profile lives

Resolve in this order, using the first applicable **whole file** (no implicit merging):

1. An explicit profile path supplied for this task (`--config`).
2. The path in `CHUST_REVIEW_CONFIG`.
3. `.chust-review.json` at the explicitly supplied project root (`--project`).
4. `~/.config/chust-skills/review.json`, shared across host agents.
5. No file: use task choices; default to two and the current host as orchestrator
   when the user has not selected one. Resolve a missing second before execution.

Explicit/env paths that are absent or invalid are errors, not permission to fall
back. An absent project file falls through to the user file. Do not search arbitrary
ancestors or infer a project from the skill's installation directory. Project files
select participants only; they do not authorize commands or override user consent.

Task choices override the selected file. Replacing a role replaces its **whole
record**, preventing an old provider, model, or transport from leaking into the new
choice. Preserve unchanged roles. An explicit “two models” overrides a saved three;
an explicit “three models” activates the third slot, never silently a spare model.
Explicitly selecting distinct models from the same provider also overrides the
provider-diversity preference for that task (`plan --allow-same-provider`); do not
require the user to edit their saved defaults. Duplicate underlying models remain
ineligible: the helper rejects matching explicit selections; resolve aliases and
unspecified models and check actual identities before counting participants.

The helper cannot discover the current host's identity. For an unspecified
orchestrator, the agent passes its known runtime product/model as one role record
using `plan --host-file`, or includes that record in `--roles-file`. Do not ask the
user to configure a host already established by the runtime. The host hint fills
only a null orchestrator; it never replaces a configured or task-selected model.
An explicit task override of `orchestrator: null` stays unresolved. Without a host
record, a null orchestrator remains `NEEDS_CONFIGURATION`, not an invented identity.

## Profile format (schema 1)

```json
{
  "schema_version": 1,
  "default_participants": 2,
  "require_distinct_providers": true,
  "roles": {
    "orchestrator": {"provider": "anthropic", "product": "Claude", "model": "fable", "transport": "auto"},
    "second": {"provider": "openai", "product": "ChatGPT", "model": null, "transport": "manual"},
    "third": {"provider": "google", "product": "Gemini", "model": null, "transport": "manual"}
  }
}
```

This illustrates **one possible profile**, not public defaults. The distributable
template leaves all roles `null`. Provider identifiers are arbitrary normalized
lowercase names, not a hard-coded vendor list. Reuse one canonical identifier for
the same provider. `require_distinct_providers` defaults to `true`; users can set it
to `false` for distinct models from one provider. The same underlying model in two
sessions never becomes two models. Resolve aliases and check actual identities at
execution, including collisions not visible in the profile.

Every non-null role has four fields:

- `provider`: the model provider, independent of the access product.
- `product`: the chosen app/service, such as a chat product, CLI, or local runner.
- `model`: requested ID/family/alias, or `null` to preserve a model already selected
  in that product. Null does not mean “any model” or “use the newest”; if no selection
  can be established, resolve it before calling. Family aliases retain that family.
- `transport`: `auto`, `tool`, `cli`, or `manual`. `auto` discovers authorized access
  **within the specified product**; it does not allow replacing it with another app.
  None of these values claims that access exists or provides executable commands.

The third may remain null for two-model use. A null orchestrator can use the known
current host supplied by the agent as described above. An incomplete profile may be
saved during setup, but other missing active roles block a roster plan. The plan checks selection,
not availability or verified identities. Never report its `READY_TO_CHECK_ACCESS`
status as a completed run.

## Optional helper

Paths below are relative to the skill directory. Python 3.10+, standard library only.

```text
python scripts/configure.py init
python scripts/configure.py show
python scripts/configure.py plan --participants 3
python scripts/configure.py plan --host-file /path/to/current-host.json --roles-file /path/to/task-overrides.json
python scripts/configure.py init --config /path/to/review.json --from-file /path/to/preferences.json
python scripts/configure.py plan --config /path/to/review.json --roles-file /path/to/task-overrides.json --participants 2
```

For `init`, destination priority is explicit `--config`, explicit `--project`,
`CHUST_REVIEW_CONFIG`, then the user path. Thus `init --project` creates
`.chust-review.json` there even when the environment selects another profile for
reading. `show` and `plan` keep the read precedence above. Existing files are never replaced.
Edit the existing JSON for later updates, then run `show` or `plan` to validate.
`--roles-file` is a JSON object containing only role names and their replacement
records; it affects this plan only.
`--host-file` contains one role record with provider, product, model, and transport;
it is a runtime hint and is never saved into the profile. The helper cannot switch the current host,
invoke models, or convert a chat subscription into CLI/API access. Without a shell,
read and apply the same preferences in the conversation or an attached profile.

## Migration from older versions

Keep the `dual-model-review` name, installation paths, and existing `peer.py`
commands. No configuration is required for an explicit two-model request.
Move any owner-specific policy out of a locally edited `SKILL.md` into the profile
before replacing the installation. Back up that local version; do not transplant
private provider rules into the public release. Existing run receipts remain valid.
