# Plan: one 4:5 image, 6 characters, 3 device screenshots, 2 style references

## The problem up front

Sent as individual files, the count is 11 references, under the 14 ceiling. The per-category limits are the catch. The character limit is 4 on `gemini-3.1-flash-image` and 5 on `gemini-3-pro-image`. Neither reaches 6. The categories are inferred by the model, not declared by me, so I cannot assert them, but I should not plan to exceed them. Six separate portraits is the weak point of the plan.

## Reference plan

Send 7 to 8 files, not 11.

1. **Characters, packed.** Build two contact sheets, each a clean grid of 3 portraits on a neutral background, same scale, with a small label under each face ("A, B, C" and "D, E, F"). That is 2 character-type images carrying 6 people. One image can carry several people, so this stays inside the limit.
2. **Screenshots, packed.** Either send the 3 screens individually (objects allow 10) or combine them into one sheet. I would send them individually, so each stays sharp and I can tie each to a device by order.
3. **Style.** Send both mood-board images (the limit is 3 on flash-image, so 2 is fine).

Order: character sheets, then screenshots, then style images, then the text part last. Images always come before the instruction.

Model: `gemini-3.1-flash-image` (style and object headroom). Use `gemini-3-pro-image` only if faces drift, since it allows 5 characters.

Settings: `aspectRatio: '4:5'`, `imageSize: '2K'`, `responseModalities: ['IMAGE']`.

## Prompt

Refer to references by position, never by their content.

- "Image 1 shows characters A, B, C. Image 2 shows D, E, F. Keep each person's face, hair and build exactly as shown."
- "Images 3, 4 and 5 are app screens. Show them on three devices: a phone held by A, a tablet on a table, a laptop. Keep each screen exactly as supplied."
- "Images 6 and 7 are style references. Match their colour palette, lighting and mood, but not their subjects."
- Describe the scene only: where each person stands, the table, the light, the framing, and a 4:5 composition with space at the top for a headline.

Do not describe what is on the screens (the words fight the picture). Do not write "no watermarks": with references attached it can trigger a content-filter refusal on the whole call. Phrase everything positively.

## What could go wrong

- **Faces blend or swap.** Six people in one frame is above the model's character limit. Check each face against its portrait. Fallback: generate two images of 3 people and composite them, or add people in a second edit pass.
- **Wrong screen on the wrong device.** Order is only a hint. Check each device.
- **Garbled screen text.** The model redraws screens; small labels can come back wrong. Fine as a thumbnail, wrong if people zoom. Fallback: generate the scene with blank devices, then paste the real screenshots in afterwards.
- **Style bleed.** The mood-board subjects or text can leak in. Say "style only".
- **Empty result.** A refusal returns `finishReason: 'content-filter'`, no files and an empty string. Log `finishReason`, retry a few times, then throw.
- **Crowding.** Six people plus three devices in 4:5 may look busy. Plan the layout in the prompt.
- **Disclosure.** An image built from real portraits and screenshots is still AI-generated. Apply the labelling rules that cover this use, and do not assume references exempt it.
