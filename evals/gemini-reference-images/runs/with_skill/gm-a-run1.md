# Intermittent "No image returned: " from Gemini with reference images

## Likely causes

1. **"No watermarks" in the prompt (main suspect).** With reference images attached, Gemini seems to read this as a request to strip watermarks from the supplied images. It refuses the whole call. The refusal comes back as `finishReason: 'content-filter'`, zero files and an empty `result.text`. That matches your empty message after the colon. Your prompt ends "No watermarks, no extra text." Remove it.

2. **The error hides the real reason.** A refusal looks like a flaky model because you print only `result.text`, which is empty. Log `finishReason`.

3. **No retry.** The model sometimes returns nothing for ordinary reasons. Throw only after the attempts are used up.

4. **The prompt describes what is on the screen.** "Dashboard with a blue bar chart and the title 'Sales'" fights the real screenshot and gives a hybrid or odd output. Describe only the scene that holds it: desk, laptop, light.

5. **Ordering.** Put the reference parts before the text part.

6. **Roles of the two references are unclear.** The logo and the screenshot are sent as identical undifferentiated file parts. Gemini infers the categories. Say plainly in the scene text where each should appear, but do not describe their contents. Two references is well under the 14 ceiling, so count is not the problem.

I cannot say which cause fires on your one-in-three calls without a logged `finishReason`. Cause 1 is the likeliest, since it is a deterministic trigger on every call that gets that wording. If every call contained it, though, you would see far more than a third failing, so the retry and logging changes will show whether a second cause is involved.

## Fixed code

```ts
const prompt = `A tidy desk with a laptop whose screen shows the attached screenshot, filling the screen. The attached logo appears subtly, for example on a sticker on the laptop lid. Soft window light, shallow depth of field.`;

const references = [
  { mediaType: 'image/png', bytes: screenshotBytes },
  { mediaType: 'image/png', bytes: logoBytes },
];

const MAX_ATTEMPTS = 3;
let lastReason = 'unknown';

for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
  const result = await generateText({
    model,
    prompt: [{ role: 'user', content: [
      // references first, then the instruction
      ...references.map((r) => ({
        type: 'file' as const,
        mediaType: r.mediaType,
        data: r.bytes,
      })),
      { type: 'text' as const, text: prompt },
    ]}],
    providerOptions: { google: { responseModalities: ['IMAGE'] } },
  });

  const img = result.files.find((f) => f.mediaType.startsWith('image/'));
  if (img) return img;

  lastReason = String(result.finishReason);
  console.warn(`Gemini attempt ${attempt} returned no image`, {
    finishReason: result.finishReason,
    text: result.text,
  });
}

throw new Error(
  `No image returned after ${MAX_ATTEMPTS} attempts (finishReason: ${lastReason})`,
);
```

## Changes

- Removed "No watermarks, no extra text".
- Removed the description of the screen contents.
- References now come before the text.
- Takes the first `image/*` file rather than `files[0]`.
- Logs `finishReason` and retries before throwing.

## After the fix

- If `content-filter` still shows up, look for other wording that could read as "remove something from the supplied images".
- Check the output for garbled small text on the screen. The model redraws the screenshot rather than pasting it, so zoomed-in text may be wrong.
- The result is still AI-generated. Apply whatever disclosure rules cover generated images where you publish it.
