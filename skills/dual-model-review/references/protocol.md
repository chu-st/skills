# The exchange

The user may ask for an investigation, review of existing work, or comparison.
These modes share an evidence standard but do not pretend to have the same
independence. A peer reviewing an existing draft necessarily sees that draft.

## Investigation

1. The host writes a neutral brief and its own initial answer separately.
2. The peer receives the brief and raw evidence, not the host's answer.
3. Preserve both answers before exchanging them. Label them A and B when useful;
   retain actual model identities in the execution record. Do not claim anonymity
   if the writing or tool interface reveals the author.
4. The host checks B against evidence. If material disagreements remain, ask B to
   challenge A using the same finding contract. A new focused request is preferred
   to a sprawling debate. Stop at the declared budget, normally two peer calls.
5. Resolve individual claims, then produce one answer. Agreement on a factual
   claim is strongest when supported by different independent evidence trails.

## Review

Send the frozen artifact, original request, constraints, and acceptance criteria.
Request meaningful defects and counterexamples, not cosmetic edits or a mandatory
number of criticisms. The host reproduces or checks findings before applying them.
A peer's proposed command is not authorization to run it. For code or release work,
use the project's existing acceptance checks on the final version.

## Finding contract

Record consequential findings as:

- **Claim/location:** exact claim and a stable section/quote or file reference.
- **Kind:** factual error, unsupported inference, missing evidence, assumption,
  alternative explanation, implementation defect, or preference.
- **Evidence:** source and relevant passage; calculation with inputs; test and
  observed output; or explicitly labelled untested scenario.
- **Impact:** how this changes the decision or result.
- **Disposition:** confirmed + change, rejected + reason, or unresolved + what
  would settle it. A suspicion without evidence does not become a confirmed error.

Do not impose a finding quota. “No material findings” is legitimate. Unsupported
allegations and preferences do not count as defects. Do not lower severity to fit
a quota or hide material findings in an appendix nobody reviews.

## Resolving disagreement

Apply the user's constraints first; establish facts with primary evidence or
reproduction. For designs and decisions, evaluate criteria, costs, alternatives,
reversibility, and failure conditions. If these do not determine a winner, present
the unresolved choice. Do not count votes, equate confidence with probability, or
combine incompatible plans merely to include both authors.

## Records and stopping

Small chat tasks need only a brief and concise findings in the conversation. Larger
tasks benefit from `brief.md`, `answer-a.md`, `answer-b.md`, `findings.md`, and
`final.md`. Put these in the user's designated output location, never publish them
automatically. CLI helper receipts record requested/reported model, exact argv,
input/output hashes, timestamps, exit code, and execution status.

Stop at sufficient evidence, no remaining material disagreements, the budget limit,
or a real access blocker. Preserve partial results and tell the user what remains.
Do not restart expensive completed work after an interruption if valid artifacts
already exist. A late change to the input invalidates affected findings, not all
unrelated verified work.
