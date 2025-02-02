## Couple of notes

#### Expressions
- The parser ignores all whitespace, and so "a b <-> c" will be interpreted as "ab↔c".
- Anything that isn't detected as an operator/bracket will be considered a variable, so stuff like "a$% /\ b***" is valid.
- That being said, most of the time trying to use characters reserved as operators won't pass the syntax check, i.e. "a< <-> b", and in the case it does the result will be undefined.