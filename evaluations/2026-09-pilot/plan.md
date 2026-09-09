# Pilot plan — fixed before model calls

Question: can the revised instructions preserve corrections, reject false criticism and describe incremental contribution? Exploratory comparison: does a fresh reviewer requested from the same model as the draft author differ from a different-model reviewer?

Two purposively selected research cases: a previous Codex support-analysis answer and two exact excerpts from a previous Claude education-research draft. Their declared author identities are recorded in rubric.json. The Codex original receipt exposes the requested model only; the Claude original attribution is from its run plan. Do not claim independently verified original model identities.

For each case, request one fresh Codex `gpt-5.6-sol` response and one fresh Claude `opus` response. Thus the declared same-model side reverses between cases. Both receive identical prompt bytes, the same source summaries and revised instructions, no earlier review or rubric, a 650-word answer request and a 180-second time limit. No retries for low-quality results and no extra debate. Unavailable execution stays unavailable. No independent search; check logs for tool use.

These are matched task and practical limits, **not equal realized compute or dollar budgets**. Record elapsed seconds and available provider counters separately. Model defaults, hidden prompts, caching and tokenizer definitions differ. Do not aggregate token counters into a cross-provider score or call a low-latency result a quality win.

A separate constructed synthesis control runs once per model, max 500 words and 180 seconds. One reviewer note is valid; one is deliberately false. This tests rejection of false criticism and survival of a corrected qualification. It is not a hidden manipulation of any real user deliverable and is not pooled into effectiveness results.

Total planned: six CLI calls. Stop after these calls. Assess objective claims against supplied counts and source scope, preserve individual outputs, accept new verified findings outside the initial checklist, and record false criticism/regressions. The checklist is not exhaustive ground truth, and zero listed defects does not prove a defect-free answer. The host's assessment is not blind and no human usefulness ranking is available. Two selected cases, one pass each, cannot establish population accuracy, savings, comparative superiority or statistical significance. These results guide the next experiment's design.

The next study needs prospective tasks, independent outcome criteria, the same drafting and synthesis allowance in both arms, a justified budget measure, randomized presentation and human ratings of usefulness and reading/rework time. Determine confirmatory sample size from desired precision after the pilot; do not promote a convenience sample into proof.
