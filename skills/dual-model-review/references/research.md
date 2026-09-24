# Research and decisions

Use this route for literature questions, market and product research, interpretation
of data, fact-checking, choosing a course of action, and other non-code work.

## Give every selected model a fair starting point

Specify the question, time period, geography, terminology, exclusions, relevant
constraints, available evidence, and the form of the answer. Separate facts supplied
by the user from hypotheses. Do not suggest the answer in the peer brief.

Two useful source modes:

- **Supplied corpus:** all reason over the same documents. This compares
  interpretation and inference, not completeness of the literature search.
- **Independent search:** each can look for sources separately. Keep citations,
  search scope, dates and sources supporting key claims; inspect the actual
  underlying publications. Record unequal tool access as a limitation.

The included CLI helper is a supplied-corpus transport. Claude runs with tools
disabled and Codex runs under a read-only sandbox. It is not a research browser.
For fresh-source discovery, use the host's search tools, an available peer research
connector, or separate tool-enabled chats with the same search brief. A third model
is useful only insofar as its evidence or reasoning adds something; three citations
ultimately copying one source are still one evidence trail.

## Challenge what could change the answer

Check whether the source establishes the claimed result, whether its sample,
denominator, geography and date apply, whether correlation was turned into
causation, and which alternatives could explain the observation. Distinguish
absence of evidence from evidence of absence. Repeated reporting of one source
does not constitute multiple independent confirmations.

For a recommendation, identify the decisive assumptions and the smallest new
observation that would change it. A model's plausible scenario is a hypothesis,
not a documented event. Estimates require inputs and ranges, not invented precision.
Keep the source's finding separate from your proposed action. During revision,
do not turn a qualified observation into a universal rule or remove its limitations.

For medical, legal, financial, or other consequential research, check current
authoritative sources and communicate material uncertainty. A second model is
not professional sign-off; neither is agreement among three models.

## Output for ordinary readers

Answer the user's question in their terms. Explain the evidence behind the main
conclusion, important alternatives, and what remains unknown. Add a short note
about what each peer changed. Do not turn a simple research request into
a wall of process terminology, tier numbers, or internal metadata.
