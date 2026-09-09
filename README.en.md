# CHU.ST Skills

[![Dual-model review · chu.st](assets/brand/skills-cover.png)](https://chu.st/?utm_source=github&utm_medium=referral&utm_campaign=skills&utm_content=cover_en)

An open, evidence-oriented second opinion for research, decisions, plans, documents,
and code. Built at [chu.st — Чувство управления](https://chu.st/).

**Choose the second model in your prompt.** The protocol is agent-neutral. Automatic
execution needs access to the selected model; otherwise exchange a neutral brief
and an actual answer between two chats.

- Claude Code → Codex, with an explicit model ID.
- Codex → Claude, with an explicit model ID or alias such as `opus`.
- Other agents through available connectors or an explicit CLI argument adapter.
- Any text chat through the [standalone prompt](prompts/start-en.md).

The [skill](skills/dual-model-review/SKILL.md) and references are in English so
agents can reuse them; answer users in their own language. The README, onboarding,
and research example are primarily in Russian.

[Install](docs/install.md) · [Transport details](skills/dual-model-review/references/transports.md)
· [Research example](examples/research/README.md) · [Validation](docs/validation.md)

[Pilot: same-model and different-model review](evaluations/2026-09-pilot/results.md)

Two models agreeing is not evidence of correctness. Validate material findings
against primary evidence or reproducible checks. Record limitations and distinguish
successful delivery from a quality verdict. No universal accuracy or cost claim.

Python 3.10+ is only needed for optional CLI and installation helpers. Provider
authentication and usage charges remain yours. No telemetry or data sent to chu.st.

Maintained by Timur Semenov / CHU.ST. Contact: timsem@chu.st. [MIT license](LICENSE).
