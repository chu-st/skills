# The exchange

The user may ask for an investigation, review of existing work, or comparison.
These modes share an evidence standard but do not pretend to have the same
independence. A peer reviewing an existing draft necessarily sees that draft.

## Short investigation / comparison

1. The orchestrator writes a neutral brief and its own initial answer separately.
2. Each peer receives the same brief and raw evidence, not anyone else's answer.
3. Preserve all first answers before exchanging them. Label them A, B, C when useful;
   retain actual model identities in the execution record. Do not claim anonymity
   if the writing or tool interface reveals the author.
4. The orchestrator checks B (and C when selected) against evidence. If material
   disagreements remain, send one focused follow-up to the peer best positioned
   to resolve them, with the disputed claim and evidence, not a demand for consensus.
   Normal budget: one first call per peer plus at most one follow-up in total.
5. Resolve individual claims, then produce one answer. Agreement on a factual
   claim is strongest when supported by different independent evidence trails.

This short route does not require all peers to exchange answers or revise their
own versions. Preserving first answers before exchange is an ordering rule, not
a claim that every participant has reviewed every other participant.

## Full investigation / comparison

The orchestrator is one of the selected two or three authors, never a fourth.
Use the same question, raw evidence, criteria, and access assumptions for everyone.

1. **First answers:** each author independently proposes a solution. Preserve all
   first versions before sharing them; retain citations, assumptions and limitations.
2. **Mutual critique:** each author receives the other author's first answer, or
   both other answers when there are three. Use one packet per author. Request
   consequential findings with evidence, not a quota or a vote. Preserve all critiques
   before the revision stage so early criticism does not steer the other critics.
3. **Author revisions:** give each author their own first answer and the critiques
   of it. Each revises their version and records accepted findings with locations,
   rejected findings with reasons, and unresolved points. A change of position
   needs a source, corrected inference/calculation, clarified requirement or other
   inspectable reason; popularity and confidence alone are not reasons.
4. **Resolve material disagreements:** use [disagreements.md](disagreements.md)
   to expose competing positions, agree on useful checks where possible, and test
   claims or compare options against the user's criteria. If needed, use one bounded
   cooperative round with all authors; it is conditional, not a mandatory debate.
5. **Common draft:** the orchestrator verifies material findings, reconciles the
   revised proposals into one coherent draft and retains a short register of open
   consequential disagreements. Do not average incompatible solutions or erase
   a supported minority finding. Link accepted corrections to the draft.
6. **Independent closing check:** send each peer the same frozen common draft,
   original criteria, relevant evidence, correction record and open issues. Check
   for lost qualifications, unimplemented corrections, new unsupported claims,
   contradictions and unresolved issues that affect the outcome. Collect all
   replies before comparing them. This is an informed review of a common draft,
   not another independent first answer or proof of correctness through unanimity.
7. **Finish:** the orchestrator reproduces/checks findings and applies justified
   corrections. Check the changed locations and any new claims on the actual final
   version, using project tests where applicable. If a correction materially changes
   a reviewed conclusion, use the limited follow-up below when needed; otherwise
   state the remaining verification gap rather than saying that peers approved an
   unseen final version. Return the result with remaining uncertainties.

No participant launches more peers. Separate calls may restore explicit prior
packets rather than relying on persistent chat state. Keep first answers isolated;
later rounds are deliberately informed by the specified earlier versions.

## Reviewing an existing artifact

Send each peer the same frozen artifact, request, constraints, and acceptance criteria.
Request meaningful defects and counterexamples, not cosmetic edits or a mandatory
number of criticisms. The orchestrator reproduces or checks findings before applying them.
A peer's proposed command is not authorization to run it. For code or release work,
use the project's existing acceptance checks on the final version. Preserve all
selected peer reviews before comparing them; do not show the second's review to the third first.

In a **short** review, the orchestrator applies verified findings and checks the
final artifact. In a **full** review, preserve the independent first reviews,
resolve disputed material findings using the same bounded cooperation procedure,
have the designated author revise the artifact with dispositions, then send the
same frozen revised artifact and dispositions to all peers for an independent
closing check. Verify and apply corrections as in steps 6–7 above. Do not invent
independent original answers or make every reviewer rewrite the same shared file.
When authorship is outside the selected roster, record it without silently counting
the artifact's historical author as a new active model participant.

## Budgets and stopping by cycle

These counts are external peer responses when the orchestrator participates directly;
they exclude its own turns, tools and any relay needed for a different host. They
are neither prices nor proof that a more expensive cycle is better.

| Route | Two participants | Three participants |
|---|---:|---:|
| Short investigation / comparison / review | 1 | 2 |
| Full investigation / comparison | 4 | 8 |
| Full review of an existing artifact | 2 | 4 |

For a material unresolved issue, a full cycle may add **one cooperative response
per peer** (one extra for two participants; two for three). Include this conditional
allowance in the announced budget. Skip it when existing evidence settles the
issue or another exchange cannot help. In short mode use the targeted follow-up
below instead; do not silently expand it into a full cooperation round.

Allow at most **one additional targeted peer response in total** when a new material
finding, evidence, or a final correction justifies it and the agreed budget permits.
Do not repeat rounds to force agreement. A lower user budget takes precedence:
explain the feasible stages before calls; do not silently label a shortened run full.
The user's explicit full-cycle request authorizes the ordinary stages, not a change
of provider/product or an unapproved paid route. If a selected route fails, preserve
the work; do not silently switch to another billing path.

Stop when the planned checks are complete with material findings resolved, when no
new evidence or useful check can move a remaining disagreement, at the budget limit,
or on an access blocker. Report unresolved items and incomplete stages separately.
Unanimity, repeated agreement, and lack of new wording are not quality gates.

## Adding a third later

If the user adds a third after a two-model result, preserve the existing work and
original first answers; record that the third joined after the initial exchange.
Do not describe the whole earlier process as three independent participants.
For an unqualified “add a third”, default to a new independent answer: give the third only the original neutral brief and
raw evidence. If the user instead wants it to judge an existing disagreement,
send that disagreement and label the result **informed follow-up review**, not an
independent third first answer. In either route, resolve claims with evidence;
the third is not an arbiter whose vote overrules facts or the user's priorities.

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

For an accepted material correction, retain the original claim, the correction,
and its location in the final answer. This can be a short note; no separate file
is needed for a small task. After synthesis, check those locations against the
evidence and check any newly introduced claims. Preserve scope and qualifications.

Do not impose a finding quota. “No material findings” is legitimate. Unsupported
allegations and preferences do not count as defects. Do not lower severity to fit
a quota or hide material findings in an appendix nobody reviews.
Critique the claim actually made, without strengthening it to refute it. Report
only criticism actually raised; do not invent rejected objections to fill a section.

## Verifying decisive claims and resolving disagreement

Apply the user's constraints first; establish facts with primary evidence or
reproduction. For designs and decisions, evaluate criteria, costs, alternatives,
reversibility, and failure conditions. If these do not determine a winner, present
the unresolved choice. Do not count votes, equate confidence with probability, or
combine incompatible plans merely to include every author. A minority finding
with stronger evidence can overturn two agreeing models.

Check the decisive shared premises too. Trace a claim that drives the conclusion
to the source or a reproducible calculation even when neither model objects to it.

Describe the peer's contribution by comparing the saved first and final answers.
Do not credit the peer with a conclusion already present. Distinguish discovering
a problem from verifying it: a check devised after a finding is not a pre-existing
control. Record unsupported criticism and regressions as well as useful corrections.

## Records and stopping

Keep a compact roster: role, requested product/model, reported model, identity
evidence, access route, response status, and contribution. Count the orchestrator
as one participant; count no simulated roles or duplicate underlying models.
Delivery PASS does not establish identity or overall completion. If any requested
slot is missing, mismatched, or unverified, the requested roster is incomplete;
report verified partial results and the affected slots separately. A completed
two-model subset does not satisfy an explicit three-model request. A manual reply
can be examined even with unverified identity; label that limitation instead of
discarding useful evidence or presenting the requested roster as verified.

Small chat tasks need only a brief and concise findings in the conversation. Larger
tasks benefit from `brief.md`, `answer-a.md`, `answer-b.md`, optionally `answer-c.md`, `findings.md`, and
`final.md`. Put these in the user's designated output location, never publish them
automatically. CLI helper receipts record requested/reported model, exact argv,
input/output byte hashes, timestamps, exit code, execution status, and the model
identity assessment. Hashes refer to the saved UTF-8 `input.md` and `response.md`
files; verify their bytes without rewriting line endings. The receipt describes
the helper's submitted brief, not an unchanged copy of the original source file.

Stop at sufficient evidence, no remaining material disagreements, the budget limit,
or a real access blocker. Preserve partial results and tell the user what remains.
Do not restart expensive completed work after an interruption if valid artifacts
already exist. A late change to the input invalidates affected findings, not all
unrelated verified work.
