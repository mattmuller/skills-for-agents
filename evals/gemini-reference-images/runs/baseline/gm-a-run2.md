# Intermittent "No image returned" from Gemini image calls

The empty text after the colon means the model answered with no text and no image part. That is almost always a non-image finish, not a bug in your parsing. Likely causes, most probable first:

1. **`responseModalities: ['IMAGE']` only.** Gemini image models (the "flash image" family) are built for `['TEXT', 'IMAGE']`. With image-only, a turn where the model "wants" to reply in text, or refuses, produces an empty response. Use both.
2. **The model never decided to draw.** Your prompt reads as a description ("A desk with a laptop showing...") and the second reference image is never mentioned. With two unlabeled images, the model sometimes treats the request as a question about them. Say "Generate an image" and name each reference.
3. **Safety or policy stop with no text.** A logo plus a screenshot of a product can trip filters or `IMAGE_OTHER`/`PROHIBITED_CONTENT` finish reasons. These come back with empty text. Your error hides `finishReason` and `providerMetadata.google`, so you cannot tell.
4. **Negative instructions.** "No watermarks, no extra text" while also asking for a screen with a title "Sales" is contradictory. It raises refusal and no-output rates. State what you want positively.
5. **Transient or truncated responses.** One-in-three on identical input suggests nondeterminism. A single retry is the standard fix; no retry exists today.

## Fixed code

```ts
const prompt = [
  'Generate a realistic image.',
  'Image 1 is a company logo. Image 2 is a screenshot of a dashboard.',
  'Scene: a desk with an open laptop. The laptop screen shows image 2, unchanged.',
  'Place the logo from image 1 as a small sticker on the laptop lid.',
  'Soft window light, shallow depth of field.',
].join(' ');

async function generateScene(attempts = 3) {
  let last = '';
  for (let i = 0; i < attempts; i++) {
    const result = await generateText({
      model,
      messages: [{
        role: 'user',
        content: [
          { type: 'text', text: prompt },
          { type: 'text', text: 'Image 1 (logo):' },
          { type: 'file', mediaType: 'image/png', data: logoBytes },
          { type: 'text', text: 'Image 2 (dashboard screenshot):' },
          { type: 'file', mediaType: 'image/png', data: screenshotBytes },
        ],
      }],
      providerOptions: { google: { responseModalities: ['TEXT', 'IMAGE'] } },
    });

    // Images can arrive on any step, so search them all.
    const img = [result.files, ...result.steps.map(s => s.files)]
      .flat()
      .find(f => f?.mediaType?.startsWith('image/'));
    if (img) return img;

    last = JSON.stringify({
      finishReason: result.finishReason,
      text: result.text,
      google: result.providerMetadata?.google,
    });
    await new Promise(r => setTimeout(r, 500 * 2 ** i));
  }
  throw new Error('No image returned after retries: ' + last);
}
```

Notes:
- `prompt` and `messages` are mutually exclusive in the AI SDK. Use `messages` when you pass structured content, as above. If your SDK version accepts the nested form you wrote, keep it, but do not pass both.
- Log `finishReason` and `providerMetadata.google` (safety ratings, `promptFeedback`). If failures cluster on `SAFETY` or `IMAGE_OTHER`, the cause is content (item 3), and retrying will not help; change the inputs instead.
- If the logo is not essential, drop it. Fewer references reduce failures.
- Do not rely on the model rendering the exact title "Sales". Passing the screenshot and saying "unchanged" is more reliable than describing the chart.
- Retry only on empty results, not on thrown API errors such as 4xx.
