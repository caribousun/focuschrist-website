# Ask Follow-up Visibility and Focus Repair Prompt

## Objective

Repair the conversation experience on both `ask.html` and the Pioneers Ask section in `pioneers.html`.

## Required behavior

1. Open the page and activate the Ask composer by clicking **Ask a Question**, typing a question, or choosing a suggested topic.
2. Submit the opening question and verify that the newest answer remains visible inside the conversation area without requiring the visitor to scroll the page or the chat manually.
3. After every answer finishes, keep the conversation region positioned so the newest answer is the active visual context and the follow-up composer is visible.
4. Automatically return focus to the next-question field after each answer, including after a topic selection and on touch or coarse-pointer devices. The visitor must be able to type the next question immediately without clicking the field again.
5. Preserve the answer's readable position when the field receives focus. Focusing the composer must not cause a second page jump that hides the newest answer.
6. Keep the composer enabled and ready after a successful answer, while retaining the existing disabled and loading states during a request.
7. Preserve conversation history, source links, related-study links, clear/new-question behavior, keyboard access, and the existing local-first/source-integrity routing.

## Verification sequence

Run the sequence independently on Ask and Pioneers:

- Activate the composer and submit an opening question or topic.
- Submit five follow-up questions in succession.
- After each response, record the actual viewport width, page scroll position, internal chat scroll position, newest-answer bounds, composer bounds, composer enabled state, and focused element.
- Confirm the newest answer intersects the viewport, the composer intersects the viewport, the composer is enabled, and focus is on the next-question field after the response settles.
- Repeat at a real desktop width and a real phone width, asserting `window.innerWidth` in each tested tab.
- Confirm that the user never needs to scroll to find the newest answer or click the follow-up field before typing the next question.

## Acceptance criteria

The repair passes only when both Ask surfaces satisfy the complete sequence at desktop and phone widths, with no horizontal overflow, no lost answer, no hidden composer, no focus loss after a settled response, and no regression to source links or clear-conversation behavior.
