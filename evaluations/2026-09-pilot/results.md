# Pilot: what a second review actually changed

On 9 September 2026, both requested reviewers corrected two source-scope problems
in one selected research draft. Both also called an observational sentence a causal
claim without establishing that the draft made that claim. A different model did
not prevent this shared overreach. This pilot does **not** establish that either
review route is better.

## Execution and evidence

The [plan](plan.md) and [checklist](rubric.json) were fixed before six calls.
The declared same-model side reverses between the two cases. Original author
identities are attributed, not independently verified. Reviewers received identical
prompt text within each case, with source summaries and instructions included:
[support](support/prompt.txt), [education](education/prompt.txt),
[constructed synthesis control](synthesis-control.txt).

| Case | Reviewer requested | Relation to declared draft author | Execution | Seconds | Response |
|---|---|---|---|---:|---|
| Support | Codex `gpt-5.6-sol` | Same | PASS | 46.63 | [Read](outputs/support-codex.md) |
| Support | Claude `opus` | Different | PASS | 70.95 | [Read](outputs/support-claude.md) |
| Education | Codex `gpt-5.6-sol` | Different | PASS | 36.03 | [Read](outputs/education-codex.md) |
| Education | Claude `opus` | Same | PASS | 49.02 | [Read](outputs/education-claude.md) |
| Synthesis control | Codex `gpt-5.6-sol` | Not applicable | PASS | 25.59 | [Read](outputs/synthesis-control-codex.md) |
| Synthesis control | Claude `opus` | Not applicable | NOT RUN | 3.30 | Account session limit |

PASS means a response was delivered, not that its claims passed review. Claude
reported `claude-opus-5` in successful calls. Codex did not expose its resolved model
identity. The Claude control stopped on a provider session limit, with a reset
announced for 13:00 Europe/Moscow; no substitute or retry was used.

[Sanitized receipts](receipts.json) contain requested/reported identities, hashes,
timing and available provider usage counters. Responses are unedited, with line
endings normalized to LF to match the helper's text hashes. Raw process logs,
machine paths and session identifiers are not published. Codex logs contain only
agent-message items; Claude reports zero web search/fetch requests. Tools were
disabled for Claude and prohibited in the common task. There was no independent
source search in this pilot.

## Assessment against the supplied evidence

This is the host's non-blind assessment. The checklist covers selected claims,
not every possible defect; model self-assessments in the responses are not verdicts.

**Support.** Both reviewers retained the correct weighted means, 11.2 and 32.1,
and the absence of an identified causal effect. Those central conclusions already
existed in the [draft](support/draft.md), so they are not incremental discoveries.
Both noticed that the supplied survey data do not identify the question or the
respondents' AI exposure. This is a useful limitation of this particular brief.
Codex framed self-selection and the need for cluster assignment conditionally.

Claude added possible endogenous difficulty classification, but labelled an
untested scenario “confirmed.” It also treated the descriptive within-stratum
comparison as an unsupported causal conclusion, although the draft already warned
about nonrandom assignment. Clarifying the wording is useful; claiming a confirmed
causal error is stronger than the evidence supports. Its final “the survey adds
nothing” is too broad: the survey describes respondents, even if it cannot estimate
AI benefit. Claude's rejected argument about applying the aggregate mean was not
an objection supplied in the task. It should have been labelled a hypothetical
counterargument rather than reported as an actual rejected criticism.

**Education.** Both reviewers corrected the comparison from all 68 courses to
the relevant 12-course subset. Both preserved the qualified disclosure guidance
in their revised answers and withheld a claim about the actual interface inventory.
These address the two predefined material defects in the [excerpts](education/draft.md).

Both also classified “the difference between paid and free is huge” as a causal
claim. The excerpt states a difference, not explicitly that payment causes it.
Adding a causal caution is reasonable; counting an established causal error and
crediting its removal is unsupported. Claude additionally listed hypothetical
objections as “rejected” without identifying them as hypothetical. Its uncertainty
about precise dates and source-reading annotations reflects the limited source
summaries; it does not establish that the original dates were false.

**Constructed control.** Codex accepted the supported correction, preserved the
qualified guidance in the final text, rejected the false unweighted average of 24,
retained 11.2, and did not credit the reviewer with the draft's existing causal
limitation. Claude's behavior on this control is unknown because access failed.

## What changes, and what remains untested

The pilot supports keeping an explicit check that corrections survive synthesis,
and comparing the final answer with the saved draft before attributing improvement.
It also exposed two failure modes despite those instructions. After these calls,
the release adds two short sentences: critique the actual claim and do not invent
rejected objections. **That final wording was not retested with paid model calls.**
The frozen prompts above preserve the version actually exercised.

This was two selected cases and one constructed control, not a complete experiment
in two-model effectiveness. The review calls combine critique and revision; they
do not independently test a host integrating a real peer response in every case.
No human usefulness rating, blinded evaluation, population error estimate or
repeated-sampling uncertainty is available.

The tasks and practical limits matched; realized compute and dollar budgets did
not. Provider token counters have different definitions, caching and hidden prompt
overheads. Claude's reported dollar figure is not an independently verified bill;
Codex did not report a dollar figure. Latency is descriptive, not a quality score.

A next study should prospectively sample tasks, fix independent outcome criteria,
give both routes the same drafting and synthesis opportunities, and state a usable
budget measure. Randomize presentation to human raters and measure usefulness,
false corrections and reading/rework time. Choose the confirmatory sample size
from desired precision and pilot variability. Do not promote this convenience
sample into a claim of superiority.
