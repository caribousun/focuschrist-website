# Review-gate lesson: independent code review

A code-review validator can accidentally accept the implementer as its supposedly independent reviewer when it checks only that a commitment is well formed and matches a configured value. This mobile successor repeated that omission.

For future successor validators, bind the actual implementer and code reviewer to independently verified source records and reject an equal commitment. A missing implementer binding must fail closed. Test equal and missing commitments and altered reviewer evidence. Other review roles may overlap when applicable requirements allow it; do not invent additional separation requirements.

Commitments and structural checks do not authenticate a person. An independent verifier must confirm the actor-to-commitment associations and review evidence before pins are populated. Synthetic tests demonstrate rejection behavior only; they are not human concurrence or release approval.
