# Access to the second model

The method is independent of the host agent. A prompt can request any second model;
actual automatic execution requires an available connector, CLI, or API adapter
for that model. Do not promise automatic access to every model from every app.

## Route selection

1. Use an already available tool that can invoke the exact requested model with a
   fresh context and the supplied brief. A generic subagent of the same model is
   not a substitute for the requested second model.
2. If the host has a shell and the desired CLI is installed and authenticated, use
   `scripts/peer.py` inside this skill. Python 3.10+ is required only for the helper.
3. An explicitly configured external CLI can use the `command` adapter.
4. Without such access, prepare a copyable handoff using the templates. The user
   pastes it into a fresh chat with the selected model and brings the actual answer
   back. Until that answer arrives the second opinion is pending, not completed.

## Claude → Codex

In Claude Code, read the skill and run the following using the user's selected
Codex model ID, a frozen brief file, and a new output directory:

```text
python <skill-directory>/scripts/peer.py --provider codex --model <model-id> --prompt brief.md --output review/codex-01
```

## Codex → Claude

```text
python <skill-directory>/scripts/peer.py --provider claude --model opus --prompt brief.md --output review/claude-01
```

`opus` is a user-selectable alias, not a hard-coded requirement. Replace it with
the requested alias or model ID. Read the reported model in the receipt when
available; aliases can resolve differently over time.

## Installation and troubleshooting

Authenticate through each provider's own CLI. Include needed
source text explicitly, since the peer is not expected to discover project files.

Executable discovery uses an explicit `--executable` path first, then
`CHUST_CLAUDE_BIN` / `CHUST_CODEX_BIN`, then PATH. Use a native executable; Windows `.cmd` and `.bat`
wrappers are refused to avoid interpreting data as shell syntax.
On Windows, inspect `Get-Command claude -All` / `Get-Command codex -All` or the
provider's official installation instructions to locate its native executable;
pass its absolute path with `--executable`.

Use `--timeout 300` to change the default five-minute call budget. Full stdout
and stderr are saved while the process runs. Stdin is closed after the brief;
stdout is never truncated in the launch pipeline. Empty responses, CLI failures,
timeouts and invalid provider envelopes are NOT RUN. Existing output folders are
not overwritten. A successful receipt only verifies delivery of a response.
Read the printed model identity assessment as well as `execution_status`:

- `MATCH`: the requested and reported identifiers are identical.
- `FAMILY_MATCH`: a Claude alias matches the family named in the reported ID. The
  family is read out of that ID, so a newly released family needs no code change.
  This does not verify the current alias resolution or an exact version.
- `UNVERIFIED`: identity was absent, ambiguous, or an alias could not be resolved.
- `MISMATCH`: the reported model conflicts with the requested ID or Claude family.
  The helper exits with code 2 and `NOT RUN`, preserving the received answer for inspection.

An unverified identity may accompany successful delivery; it is not a verified
model pairing. Use a concrete model ID when exact matching is required. A bare
command adapter cannot establish identity from answer text. Usage mentioning
several models is not resolved by picking the one with the most output tokens.
An identifier the helper cannot recognize as a model ID, such as `default` or a
team alias, stays `UNVERIFIED` even when both sides report the same word: an echoed
placeholder is not evidence of which model answered.
Receipts retain available provider token counters and reported cost. Missing usage
is unknown. Counter definitions, caching and dollar costs differ by provider;
do not equate them with comparable compute or an actual bill.
Reported counters, including zero, are retained for failed calls too: failure can
still incur usage. `usage.result_status` records the provider envelope's status
when available; interpret it together with the receipt's execution status.

Codex uses `exec --ephemeral --ignore-user-config --sandbox read-only` with a
new call directory. This avoids loading user-configured connectors but is not a
proof of file confidentiality: respect the host sandbox and pass only authorized
input. Claude uses safe mode with tools disabled. These flags require CLI versions
that support them; inspect `--help` if an older CLI rejects a flag. Never fix an
access failure by disabling security or silently switching models.

The helper also reads each provider's machine-readable envelope: Claude's result
object and Codex's turn events. A provider may change that format. The call then
ends as NOT RUN with the raw logs preserved, never as a silently degraded answer;
update the package rather than parsing around the change.

## Other CLI models

Create a local JSON file containing an argument array, not a shell command:

```json
["/path/to/other-agent", "--model", "{model}", "--print"]
```

Then use `--provider command --model <id> --command-file adapter.json`. The adapter
must accept the brief on stdin and write only the answer on stdout. Use
absolute paths for script and resource arguments: the child process runs in the
new output directory, not beside the adapter file or in the caller's directory.
The adapter's executable is resolved before that directory change. Configure
the provider's noninteractive, tool-access and permission flags explicitly; this
generic adapter cannot enforce another tool's policy. `{model}` substitution is
required so the requested model is not silently ignored. Verify provider identity
through its own diagnostics; generic stdout does not prove which model answered.

Official CLI references: [Claude Code](https://code.claude.com/docs/en/cli-reference)
and [Codex](https://learn.chatgpt.com/docs/non-interactive-mode).
