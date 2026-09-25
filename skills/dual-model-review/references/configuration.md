# Model preferences and setup

This is a mode of `dual-model-review`, not a second skill and not a provider API.
The agent configures it conversationally; people need not edit JSON or learn CLI
flags. The optional `scripts/configure.py` helper creates, updates, validates, and
resolves a JSON profile without calling models.

## Setup conversation

Read existing preferences and reuse choices already stated. Ask only for missing
active roles; do not require a third for two-model use. If no count is requested,
retain the existing count or use two. If no cycle is requested, retain it or use
short. Three saved roles do not implicitly mean three active participants, and
three participants do not implicitly mean a full cycle.
Keep a selected model within a product when the user has not named a version;
do not invent an exact ID. A product preference and a model identity are separate.

Save only on a setup/update request. Ordinary task overrides are temporary unless
the user asks to remember them. “Next time” alone does not authorize a permanent
default change; clarify duration only if necessary to act, or keep a one-run
preference in the current conversation and state that scope.
Saving a preference does not prove account access, authentication, or availability.
Do not collect credentials. Never add a person's private profile to the public skill.

| User action | Behavior |
|---|---|
| “Show my models / покажи настройки” | Read and summarize; do not save or invoke models |
| “Configure / remember / by default / настрой / запомни” | Save the requested preferences; retain everything else |
| “Swap Claude and ChatGPT / поменяй местами” during setup | Move the existing whole role records; preserve the third, count and cycle |
| “Only this run, two and short / только сейчас” | Temporary choices; leave the profile unchanged |
| “Configure and check access” | Save, then separately perform authorized access checks; do not ask for access-check consent again |

If a product occurs in multiple roles or a replacement would create a duplicate
active model, resolve that ambiguity rather than inventing a swap or model. A
model selection such as “Pro” must be resolved to an available identifier within
the chosen product; the explicit flag selects it but does not verify the served ID.

After a change, validate the whole updated profile and show a compact summary in
the user's language. For example:

| Role | Selected product / model | Expected access / observation |
|---|---|---|
| Lead | User's selected app and model | Selected route; access not checked or last actual observation |
| Second | User's selected app and model | Automatic tool/CLI available, manual handoff, or unknown |
| Third (active / on request) | User's selection or not configured | Route and access status, separately |

Then state the default count and short/full cycle, and one useful phrase such as
“прогони в трёх моделях полным циклом”. Keep provider codes, JSON and paths secondary;
name the actual save location briefly after a save. Do not present CLI/manual/auto
as availability results. Expected route, observed access, and reported identity
are distinct. If identity is missing, keep the useful response and label identity
unverified; do not repeatedly ask to authorize a route already selected by the user.
Read-only discovery may inform a summary; paid model calls are not implicit in setup.
Use the user's authorized access route and obtain any required billing consent;
failure of a subscription route does not authorize a paid fallback.

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
  "default_cycle": "short",
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

`default_cycle` is optional in schema 1 and is `short` when absent. It accepts
`short` or `full`, independently of `default_participants`. Old profiles remain
valid and are not rewritten on read. A task's explicit cycle overrides this default.

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
python scripts/configure.py plan --participants 3 --cycle full
python scripts/configure.py update --config /path/to/review.json --from-file /path/to/complete-revised-profile.json
python scripts/configure.py plan --host-file /path/to/current-host.json --roles-file /path/to/task-overrides.json
python scripts/configure.py init --config /path/to/review.json --from-file /path/to/preferences.json
python scripts/configure.py plan --config /path/to/review.json --roles-file /path/to/task-overrides.json --participants 2
```

For `init` and `update`, destination priority is explicit `--config`, explicit `--project`,
`CHUST_REVIEW_CONFIG`, then the user path. Thus `init --project` creates
`.chust-review.json` there even when the environment selects another profile for
reading. `show` and `plan` keep the read precedence above. `init` never replaces an existing file.
For later updates, the agent reads the existing profile, changes only the user's
requested fields, and passes the complete revised object to `update --from-file`.
To update the profile selected for reading, pass its resolved path as `--config`.
An explicit `update --project` targets that project's existing file; if missing,
it fails without changing a user/environment profile. `update` validates both profiles,
saves a uniquely named backup beside it, and replaces it through a temporary file.
It refuses a missing destination; use `init` for creation. An unchanged profile is
left alone. Do not drop unmentioned preferences when building the replacement.
Without the helper, apply the same read/modify/validate/save discipline through
available file tools; JSON editing is the agent's task, not a required user step.
`--roles-file` is a JSON object containing only role names and their replacement
records; it affects this plan only.
`--host-file` contains one role record with provider, product, model, and transport;
it is a runtime hint and is never saved into the profile. The helper cannot switch the current host,
invoke models, or convert a chat subscription into CLI/API access. Without a shell,
read and apply the same preferences in the conversation or an attached profile.

## Migration from older versions

Keep the `dual-model-review` name, installation paths, and existing `peer.py`
commands. No configuration is required for an explicit two-model request.
Older helpers may reject the new optional `default_cycle` key; use the updated
helper for a profile that stores it. Backups are personal data too; keep them out
of repositories (including custom profile names).
Move any owner-specific policy out of a locally edited `SKILL.md` into the profile
before replacing the installation. Back up that local version; do not transplant
private provider rules into the public release. Existing run receipts remain valid.
