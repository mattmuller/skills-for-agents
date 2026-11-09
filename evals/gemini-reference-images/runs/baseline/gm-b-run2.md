# Plan: one 4:5 image, 6 characters, 3 device screenshots, 2 mood boards

## Core advice: do not do it in one pass
Gemini image models accept many reference images (roughly 14 on current Flash/Pro image models, with about 5 to 6 people held reliably). Fifteen is too many, and consistency drops well before the limit. Use a staged build.

## Reference budget (11 total, in a single pass)
Send in this order, and label each in the prompt:
1. **Mood board A** (style, colour, lighting)
2. **Mood board B** (style, texture, composition)
3. to 8. **Character portraits 1 to 6**, always in the same fixed order
9. to 11. **Screenshots 1 to 3**

Style first sets the global look. Characters come next as identity anchors. Screenshots go last because they are literal content.

## Better: staged workflow
- **Pass 1, characters.** Send the 2 mood boards and 6 portraits (8 refs). Ask for the group scene only, with three blank, plain, glowing device screens, in 4:5.
- **Pass 2, screens.** Send the pass 1 output plus the 3 screenshots. Ask it to replace the blank screens, leaving everything else untouched.
- **Fallback for exact UI:** composite the real screenshots onto the devices yourself (Figma, an image editor or sharp perspective warp). Models redraw text and UI, so this is the only way to get pixel-accurate screens.

## Prompt structure
- Open with the output: "A 4:5 portrait social image, realistic, [mood]."
- Give a **reference map**: "Images 1-2 are style references only. Match palette, lighting and grain. Do not copy their content. Images 3-8 are six people, in this order: Anna (3), Ben (4)... Keep each face, hair and age exactly as shown. Images 9-11 are app screens."
- Describe the **layout** with positions: who stands where, which device sits where, and which screenshot goes on which device. Use left, centre, right and foreground, background.
- State the **negatives**: no extra people, no added text, no watermarks, do not alter the UI on the screens.
- Keep it to one paragraph of clear, short sentences. Name every character by label, not "the woman".

## What could go wrong
- **Identity drift or blending.** With six faces, features swap, or two characters look alike. Mitigate with fixed ordering, names and distinct clothing notes, plus regenerating or inpainting single faces.
- **Style leakage.** Mood-board subjects, text or objects appear in the result. Say "style only" explicitly, or reduce to one board.
- **Garbled UI.** Screenshot text becomes gibberish, or layouts are redrawn. This is the most likely failure. Composite them if accuracy matters.
- **Wrong screenshot on the wrong device**, or screens merged or reused.
- **Crowding at 4:5.** Nine subjects in a narrow frame gives small faces, and small faces lose likeness. Consider 3 to 4 characters large, or a grouped layout, or make the image higher resolution.
- **Aspect ratio ignored.** Set it via the API image config, not just in text. Check the output size.
- **Reference ordering mistaken.** The model may mix up indices. Verify the first output before iterating.
- **Rights and disclosure.** Recurring characters may be AI-generated, so apply your AI-disclosure rules to the final image.

## Iteration
Generate 4 to 8 candidates, pick the best, and fix faults with targeted edits ("keep everything, change only person 4's face to match image 6") rather than full regenerations.
