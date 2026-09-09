# Start in any text agent

```text
Use a two-model review for this task.
Question or artifact: [task]
Second model: [exact model or model selected in a separate chat]
Mode: [investigate / review an existing artifact / compare options]
Constraints, date and available evidence: [scope]

Preserve my question and criteria. For investigation, first develop your own answer;
give the second model only a neutral brief and raw evidence, not your conclusion.
For artifact review, give it the frozen artifact and original requirements.

Use real access to the requested model. Never simulate it or silently substitute
another model. If unavailable, give me a completed handoff prompt and wait for the
actual answer from a separate chat.

Resolve material disagreements with primary sources, calculations or reproducible
examples. Distinguish facts, hypotheses and preferences. Agreement is not proof.
Confirm or reject each material finding. Normally use one independent peer answer
and, only if needed, one focused follow-up.
Critique the claim actually made; do not strengthen it to refute it or invent
rejected objections. No material findings is a legitimate result.

After synthesis, check that accepted corrections and qualifications survive in
the final text and that new claims are supported. Compare with the saved first
answer; do not credit the reviewer with conclusions already present.

Return the useful answer, what the peer changed, checks actually performed,
remaining uncertainty, and the model that really participated. A peer's suggestion
does not authorize publication or other external actions.
```
