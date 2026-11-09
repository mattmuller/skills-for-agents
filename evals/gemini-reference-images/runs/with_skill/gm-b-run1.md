# Plan: one 4:5 image, 6 characters, 3 screens, 2 style references

## The core problem

Eleven loose references is inside the 14-image ceiling, but the sub-limits are the issue. The skill lists characters at 4 on `gemini-3.1-flash-image` and 5 on `gemini-3-pro-image`. Six characters exceeds both. Categories are inferred from undifferentiated `file` parts, so you cannot declare them. Send fewer images, and pack several subjects into each one.

## References: 4 images, in this order

The skill says to stay at 4 or fewer where possible. Reference parts always come before the text part.

1. **Character sheet.** One image: a clean 3x2 grid of the six portraits, same scale, plain background, with a number or label under each.
2. **Screens sheet.** One image: the three screenshots side by side, flat and unframed, in the order they will appear.
3. **Mood-board A.**
4. **Mood-board B.**

Compositing is the one thing I would test first. One image can carry several people, but identity fidelity can drop with six faces in one frame. If faces drift, split into two sheets of three. That gives 5 references, still fine.

Use `gemini-3-pro-image` if its 5-character allowance matters. Re-read the current model limits first, because they change.

## Prompt

Call through `generateText` with `responseModalities: ['IMAGE']` and `imageConfig: { aspectRatio: '4:5', imageSize: '2K' }`.

Write the prompt as four short parts:

- **Roles.** "Image 1 is a sheet of six people, labelled 1 to 6. Keep each face and hair exactly as shown. Image 2 holds three app screens, left to right. Images 3 and 4 are style references only: take palette, light, grain and composition mood, not their content or people."
- **Scene.** One scene only: where the six stand or sit, what they hold, where the devices are, the light, the lens. Say who holds which screen by number.
- **Format.** Portrait 4:5, keep faces and devices clear of the edges for cropping.
- **Tone.** Describe the look you want positively.

Two rules from the skill:
- **Do not describe what is on the screens.** Words about their contents fight the real picture and give a hybrid. Describe only the devices and hands.
- **Never write "no watermarks".** With references attached, Gemini can read it as a request to strip watermarks and refuse the whole call. Leave negative-prompt boilerplate out entirely.

## What can go wrong

- **Refusal that looks like flakiness.** It returns `finishReason: 'content-filter'`, no files and empty text. Log `finishReason`, retry an empty result, and throw only when attempts run out.
- **Face drift or blended people.** Six identities is a lot. Expect two characters to look alike or one to change age or hair. Check each against its portrait.
- **Wrong person to wrong screen or prop.** Numbering helps but does not guarantee it.
- **Garbled screen text.** The model redraws, it does not paste. Small labels and names come back plausible but wrong. Fine at thumbnail size, wrong if anyone zooms in. Inspect the output, or composite the real screenshots onto the devices afterwards for exact fidelity.
- **Style leakage.** The mood boards can bleed in their subjects or people. State that they are style only.
- **Crowding.** Nine subjects in one frame leads to odd hands, extra devices and cropped faces. Keep the scene simple, or generate the characters and composite devices in post.
- **Disclosure.** Using real portraits and screenshots does not make the result less synthetic. Apply whatever AI-labelling rules govern the image.

## Fallback

If one-shot results are unreliable, generate two images of three characters each and combine them, or generate the scene and place the real screenshots in post.
