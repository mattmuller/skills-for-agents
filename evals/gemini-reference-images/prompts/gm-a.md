My image generation helper calls a Gemini image model through the AI SDK with two reference images (a logo and a product screenshot). About one call in three throws "No image returned: " with nothing after the colon. Find the likely causes and give me the fixed code.

```ts
const prompt = `A desk with a laptop showing the attached screenshot. The screen shows a dashboard with a blue bar chart and the title "Sales". Soft window light. No watermarks, no extra text.`;
const result = await generateText({
  model,
  prompt: [{ role: 'user', content: [
    { type: 'text', text: prompt },
    { type: 'file', mediaType: 'image/png', data: logoBytes },
    { type: 'file', mediaType: 'image/png', data: screenshotBytes },
  ]}],
  providerOptions: { google: { responseModalities: ['IMAGE'] } },
});
const img = result.files[0];
if (!img) throw new Error('No image returned: ' + result.text);
```
