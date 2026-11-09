---
name: gemini-reference-images
description: Generate images with Gemini from reference images - the same character across several pictures, a real product screenshot placed inside a generated scene, style matching - and debug Gemini image calls that return no image. Use when writing or fixing code that sends reference images to a Gemini image model, when a call returns an empty result or a content-filter finish reason, or when planning how many references to attach.
---

# Gemini image generation with reference images

Gemini can generate an image from images you supply, not only from a prompt. That is how you keep one character consistent across a set, or render a real product screenshot inside a generated scene instead of an invented one.

## Limits by model

Taken from the Gemini API image-generation documentation on 19 Sep 2026. Model names and limits change; re-read the current page before relying on them.

Up to 14 reference images in total, with per-category sub-limits that are separate allocations rather than one shared pool:

| Model | objects | characters | style |
|---|---|---|---|
| `gemini-3.1-flash-image` | 10 | 4 | 3 |
| `gemini-3-pro-image` | 6 | 5 | - |
| `gemini-3.1-flash-lite-image` | 14 | - | - |

Product screenshots and character portraits therefore do not compete for budget. One image can carry several screens and several people.

**The categories are inferred, not declared.** Through the AI SDK and a gateway you send undifferentiated `file` parts; no field says "this one is a character". Treat 14 as the real ceiling and stay well under it. The category limits describe what the model can do, not something you can assert. In practice two screens plus two people is plenty.

## The call

Through the Vercel AI Gateway the image model behaved as a language model: it answered the text API with the picture in `files`, and the dedicated image API rejected it. Check how your own provider route exposes it.

```ts
const result = await generateText({
  model,
  prompt: [{ role: 'user', content: [
    ...references.map((r) => ({ type: 'file', mediaType: r.mediaType, data: r.bytes })),
    { type: 'text', text: prompt },        // images first, then the instruction
  ]}],
  providerOptions: { google: {
    responseModalities: ['IMAGE'],
    imageConfig: { aspectRatio: '4:5', imageSize: '2K' },
  }},
});
const file = result.files.find((f) => f.mediaType.startsWith('image/'));
```

Aspect ratios: `1:1 3:2 2:3 3:4 4:3 4:5 5:4 9:16 16:9 21:9`. Sizes: `512px 1K 2K 4K`.

## Traps

**1. Do not write "no watermarks" when references are attached.** Gemini appears to read it as a request to remove watermarks from the supplied images and refuses the whole call. Measured in Sep 2026, two runs per prompt tail, two references attached:

| Prompt tail | Result |
|---|---|
| "Never an illustration, a 3D render..." | image, image |
| "People, faces, hands... are all welcome." | image, image |
| "No other company's logo." | image, image |
| "No watermarks." | content-filter, content-filter |

Only the watermark wording tripped it. A negative-prompt convention copied from another image tool (many end with `watermark, over-saturated, stock-image`) can silently break every call.

**2. A refusal looks like a flaky model.** It returned `finishReason: 'content-filter'`, zero files and an empty string. If your error message prints `result.text` you see nothing and conclude the API is unreliable. Always log `finishReason`.

**3. Retry an empty response before throwing.** The model occasionally returns nothing for ordinary reasons. Throw only after the attempts are spent, and put `finishReason` in the error.

**4. Do not describe what is on a supplied screen.** The screenshot is already there; words about its contents fight the picture and produce a hybrid. Describe only the scene that holds it: the table, the light, the hands.

**5. The model redraws; it does not paste.** Small text on a reference screen can come back subtly garbled, with plausible but wrong names and labels. That is fine at thumbnail size and wrong for anything a reader will zoom into. Check the output rather than assuming fidelity.

**6. References do not make the output less synthetic.** An image built from a real screenshot and a real portrait is still AI-generated. Apply whatever labelling or disclosure rules govern your use of generated images; check what applies to you rather than assuming references exempt it.

## Checklist for a reference-image pipeline

- Reference parts come before the text part.
- Fewer than 14 references; ideally 4 or fewer.
- Prompt describes the scene, not the content of supplied screens.
- No watermark wording in the prompt.
- `finishReason` is logged and empty results are retried.
- Output is inspected for garbled small text before publishing.
