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
