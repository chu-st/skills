# Start in any text agent

```text
Use a [two/three]-model review for this task.
Question or artifact: [task]
Orchestrator: [current agent or selected product/model]
Second model: [exact model or model selected in a separate chat]
Third model: [only for three participants; otherwise not called]
Mode: [investigate / review an existing artifact / compare options]
Constraints, date and available evidence: [scope]

Preserve my question and criteria. For investigation, first develop your own answer;
give each peer the same neutral brief and raw evidence, not anyone else's conclusions.
For artifact review, give each the same frozen artifact and original requirements.
Preserve all first responses before exchanging them. The third must not see the
second's first answer in advance.

Use real access to the requested model. Never simulate it or silently substitute
another model. If unavailable, give me a completed handoff prompt and wait for the
actual answer from a separate chat. Preserve roles and selected products. If another
model orchestrates, hand off to it; do not count this host as a fourth participant.
Missing third access leaves the requested three-model run incomplete; preserve
the useful partial work without silently downgrading to two.

Resolve material disagreements with primary sources, calculations or reproducible
examples. Distinguish facts, hypotheses and preferences. Agreement is not proof.
Confirm or reject each material finding. Normally use one first answer per peer
and, only if needed, one focused follow-up in total. Do not decide by majority vote.
Critique the claim actually made; do not strengthen it to refute it or invent
rejected objections. No material findings is a legitimate result.

After synthesis, check that accepted corrections and qualifications survive in
the final text and that new claims are supported. Compare with the saved first
answer; do not credit the reviewer with conclusions already present.

Return the useful answer, what each peer changed, checks actually performed,
remaining uncertainty, and models that really participated. Report unverified
identities separately from received responses. A peer's suggestion
does not authorize publication or other external actions.
```
