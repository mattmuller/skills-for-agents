# Why about one call in three returns "No image returned: "

## Likely causes, most probable first

**1. "No watermarks" in the prompt (the main suspect).** With reference images attached, Gemini appears to read "no watermarks" as a request to strip watermarks from the supplied images (your logo, for one) and refuses the whole call. The refusal comes back as `finishReason: 'content-filter'`, zero files and an empty `result.text`. That matches your empty message after the colon. The failure is intermittent because refusal is probabilistic. Remove the phrase and the filter should stop firing.

**2. The error message hides the real reason.** You print `result.text`, which is empty on a refusal. Log `result.finishReason` so you can tell a content-filter refusal from an ordinary empty response.

**3. No retry.** The model sometimes returns nothing for ordinary reasons. Retry a few times and only throw when the attempts are spent.

**4. Prompt describes the screen contents.** "A dashboard with a blue bar chart and the title 'Sales'" fights the attached screenshot and produces a hybrid. It makes a refusal no more likely, but it hurts quality. Describe only the scene around the screen.

**5. Reference order.** Put the image parts before the text part. Yours has the text first.

## Fixed code

```ts
const prompt = `A desk with a laptop showing the attached screenshot on its screen. Soft window light, shallow depth of field, a notebook and a coffee cup beside the laptop.`;

const MAX_ATTEMPTS = 3;
let img;
let lastFinish: string | undefined;

for (let attempt = 1; attempt <= MAX_ATTEMPTS && !img; attempt++) {
  const result = await generateText({
    model,
    prompt: [{ role: 'user', content: [
      // references first, instruction last
      { type: 'file', mediaType: 'image/png', data: logoBytes },
      { type: 'file', mediaType: 'image/png', data: screenshotBytes },
      { type: 'text', text: prompt },
    ]}],
    providerOptions: { google: { responseModalities: ['IMAGE'] } },
  });
  lastFinish = result.finishReason;
  img = result.files.find((f) => f.mediaType.startsWith('image/'));
}

if (!img) {
  throw new Error(`No image returned after ${MAX_ATTEMPTS} attempts (finishReason: ${lastFinish})`);
}
```

## What changed

- Removed "No watermarks, no extra text". Avoid any watermark wording while references are attached.
- Removed the description of the dashboard, chart and title.
- Moved the reference images before the text.
- Added retries, and `finishReason` in the error.
- Picked the first file whose `mediaType` starts with `image/`, not blindly `files[0]`.

## Caveats

- I did not run this. The watermark wording is the best-supported cause, not a proven one. Test it: run 20 calls with the old prompt and 20 with the new one, and log `finishReason` for each.
- If `content-filter` still appears with the new prompt, check whether the logo itself triggers it. Try the call without the logo.
- The model redraws the screenshot rather than pasting it, so small text on the screen can come back garbled. Check the output before anyone zooms in.
- An image built from real references is still AI-generated. Apply your disclosure rules to it.
