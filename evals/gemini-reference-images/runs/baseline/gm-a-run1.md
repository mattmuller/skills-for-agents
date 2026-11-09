# Intermittent "No image returned: " from a Gemini image call

## Likely causes

The empty text after the colon means the model returned no image part and no text part. That usually means a block or a refusal, not a transport error. Check `finishReason`, `result.response`, and `providerMetadata.google` (safety ratings, `promptFeedback`) to confirm.

1. **`responseModalities: ['IMAGE']` only.** Gemini image models (the "flash-image" family) expect `['TEXT', 'IMAGE']`. With IMAGE alone, the model sometimes has nothing it can emit and returns an empty candidate. This is the most common cause of a one-in-three failure.
2. **Prompt content that triggers a safety or "image other" stop.** The prompt asks for a literal title ("Sales") and a chart rendered on a screen, plus negative instructions ("No watermarks, no extra text"). Negations contradict the requested text, and the model sometimes stops with `IMAGE_OTHER` or `NO_IMAGE`. Reference images that contain a logo or a real UI can also trip the filters.
3. **Ambiguous references.** Both images are sent as unlabelled `file` parts. The prompt mentions only "the attached screenshot", never the logo. The model sometimes answers with a text question or nothing. Label each image and say what to do with it.
4. **Text-only reply.** The model sometimes returns text ("I can't...") instead of an image. Your error shows `result.text`, which is empty here, so a safety block (cause 2) is more likely than a chatty refusal.
5. **No retry, no diagnostics.** The failure is stochastic, so a retry usually succeeds. Your code throws on the first miss and discards the reason.
6. **Large inputs.** Two full-size PNGs can push the request near size limits and cause truncated output. Downscale them (about 1024 px on the long side).

## Fixed code

```ts
import { generateText } from 'ai';

const prompt = [
  'Create a realistic image of a desk with a laptop in soft window light.',
  'Image 1 is a brand logo: place it subtly on the desk, for example on a notebook.',
  'Image 2 is a product screenshot: show it on the laptop screen, unchanged.',
  'Use only the text that appears in the screenshot.',
].join(' ');

async function generateImage(maxAttempts = 3) {
  let lastReason = 'unknown';
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const result = await generateText({
      model,
      messages: [{
        role: 'user',
        content: [
          { type: 'text', text: prompt },
          { type: 'text', text: 'Image 1 (logo):' },
          { type: 'file', mediaType: 'image/png', data: logoBytes },
          { type: 'text', text: 'Image 2 (screenshot):' },
          { type: 'file', mediaType: 'image/png', data: screenshotBytes },
        ],
      }],
      providerOptions: {
        google: { responseModalities: ['TEXT', 'IMAGE'] },
      },
    });

    const img = result.files.find(f => f.mediaType.startsWith('image/'));
    if (img) return img;

    lastReason = JSON.stringify({
      finishReason: result.finishReason,
      text: result.text,
      google: result.providerMetadata?.google,
    });
    console.warn(`No image (attempt ${attempt}): ${lastReason}`);
    await new Promise(r => setTimeout(r, 500 * attempt));
  }
  throw new Error('No image returned after retries: ' + lastReason);
}
```

## Notes

- I changed `prompt:` to `messages:` because the AI SDK expects an array of messages there. Use whichever form your SDK version accepts.
- Remove negations where you can. Describe what you want, not what to avoid.
- Log `finishReason` and the safety ratings for a day. They will tell you which cause dominates. If the reason is a safety block, retries will not help, and you must change the prompt or the references.
