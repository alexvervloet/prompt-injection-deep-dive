# Lessons

Things that did not go the way the plan assumed. Written when they happened.

## The demo of a defense found the hole in the defense

**Expected:** the nonce is the real boundary in `fence_document`, and stripping
tag-shaped lines is defence in depth. Belt-and-braces code that would not
actually be load-bearing, written quickly.

**What happened:** example 13 lists near-miss tags a fuzzy reader might honour,
and prints whether each one survives the strip. Four were removed. `<
/untrusted_document >` survived, because the pattern allowed whitespace
everywhere except between the angle bracket and the slash.

The nonce meant the hole was not exploitable, which is exactly why it would have
survived review. Nothing failed. The only reason it surfaced is that the example
prints a row per variant instead of asserting "the strip works", so a reader
sees five rows and one of them said SURVIVES in a table designed to say
"removed".

**Next time:** when a lab demonstrates a defense, make it enumerate cases and
show the result of each one rather than summarising. A table with a wrong row in
it is self-correcting in a way that a green check mark is not. And a pattern
matching "text a human would read as X" needs its whitespace assumptions tested
at every position, not just the ones that occurred to whoever wrote it.

## Fixing an encoding bug must not sand off the honest failures

**Expected:** folding text before matching would strictly improve the heuristic
detector.

**What happened:** it did, and briefly that looked like a problem. The dive's
whole argument about input detection rests on two demonstrations: the heuristic
misses an obfuscated attack, and it false-flags a benign "ignore the typos"
message. A detector that suddenly caught everything would have quietly destroyed
the lesson.

It did not, because the two remaining failures are the interesting ones.
Paraphrase still walks past folding, since folding cannot read. The benign
message still trips, since it really does contain the word. What folding removed
was only the encoding family, which was never the point being made.

Worth stating because the temptation ran the other way for a moment: leaving a
real bug in place to protect a teaching example would be the exact dishonesty
this series is built against. The right move was to fix it and then check that
the surviving failures still carry the argument, which they do.

**Next time:** after hardening something a lesson depends on, re-read the lesson
before the code. If the fix makes the teaching example stop teaching, the
example was demonstrating the wrong thing.

## "Cannot be replayed" was true and answered a different question

**Expected:** the approval control was finished. Its docstring said an approval
"cannot be replayed against a different tenant, tool, or object", there was an
exercise called "Design an approval replay attack", and a test asserted the
binding held.

**What happened:** all of that was accurate and none of it covered replay at the
same target. Fifty authorizations from one approval returned True. The sentence
in the docstring is carefully worded and every word of it is correct, which is
exactly why nobody noticed the clause it does not contain.

The tell was available the whole time. `RequestBudget` in the same repository
burns a reservation id exactly once, and `incidents.py` dedups replayed
operations. One codebase, three modules, two strengths of the same idea, and the
weakest one guarded the irreversible effects.

**Next time:** when a security claim is scoped by a prepositional phrase, read
the phrase as the boundary of the claim rather than as detail. "Cannot be
replayed *against a different X*" is a statement about aiming, not about
freshness. And when one module in a codebase implements an idea more strongly
than another, that is a finding, not a style inconsistency.

## An idempotency key looks like a nonce and is not one

**Expected:** requiring an idempotency key on writes was replay protection, and
`ApprovalChallenge` would be a small addition to something already most of the
way there.

**What happened:** they are unrelated controls that share a shape. An
idempotency key guarantees a duplicate submission converges on one effect, which
is a correctness property, and a predictable value serves it perfectly well. A
nonce guarantees a duplicate is refused, which is a security property, and a
predictable value destroys it. The broker accepted any non-empty string and the
model chose it.

Writing the two of them as a table in the chapter was what made the difference
legible. In prose they kept reading as the same paragraph.

**Next time:** when two controls share a vocabulary, put them in a table with a
column for who issues the value and a column for whether it may be predictable.
If those columns differ, the controls differ, whatever the code calls them.
