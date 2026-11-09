# Plan: one 4:5 image with 6 characters, 3 device screenshots, 2 style references

## Short answer
Do not send all 11 images in one call and hope. Gemini image models (Gemini 3 Pro Image supports up to 14 reference images, roughly 5 for human fidelity and 6 for objects; Flash Image handles fewer reliably) will accept it, but identity drift rises sharply past about 4-5 faces. Use a staged build.

## Recommended pipeline (3 passes)

**Pass 1: Scene and style (2 refs).** Send the 2 mood-board images only. Prompt for an empty 4:5 composition: layout, lighting, palette, background, with clearly empty zones (a band for the characters, three device-shaped slots). Output: a style-locked base plate. Set aspect ratio 4:5 explicitly in the API config, not just in the prompt.

**Pass 2: Characters (6 portraits + base plate).** Send the base plate first, then the 6 portraits in a fixed order. Label each in text: "Image 2 is Anna (left-most), Image 3 is Ben..." and map each name to a position. If faces drift, split this into two passes of 3 characters each, feeding the previous output back in as the base.

**Pass 3: Devices (3 screenshots + latest plate).** Send the plate, then the 3 screenshots, one per named device slot ("Image 5 fills the left phone screen"). Better still: do not let the model draw the screens at all. Generate devices with blank or neutral screens, then composite the real screenshots in code (Figma, Sharp, Pillow) with a perspective transform.

## Order of references
1. Style/mood boards (or the plate) first, as the "look" anchor.
2. Characters, in the order they appear left to right.
3. Screenshots last, in the order of their slots.
Always name each image by number and role in the prompt.

## Prompt structure
- One-line goal: "A 4:5 vertical social image, in the style of images 1-2."
- Layout block: where each character stands, where each device sits, relative scale.
- Per-reference mapping: "Image N = [name]: keep face, hair, skin tone and clothing exactly."
- Style block: palette, lighting, texture, in words as well as via the images.
- Negatives, stated positively: "no extra people, no text other than what is on the screens, no watermark."
- Do not describe the characters' faces in words; let the portraits carry identity.

## What can go wrong
- **Identity drift or blending**: faces merge, or two characters look alike. Fix with fewer faces per pass and distinct clothing cues.
- **Wrong person count**: 5 or 7 people. State "exactly six people" and check.
- **Screenshot corruption**: UI text becomes garbled, layouts are invented, aspect ratios are stretched. This is the highest risk; composite the real screenshots instead.
- **Style bleed**: mood-board content (objects, people) leaks in, not only style. Say "use for style only, do not copy subjects."
- **Reference weighting**: early images dominate; the last ones are ignored.
- **Crowding**: 9 subjects in 4:5 leaves each tiny; faces below about 150 px lose likeness. Consider a layout with three characters per row, and devices overlapping the background.
- **Wrong aspect ratio or cropping** if only the prompt asks for 4:5.
- **Consistency across the series**: save seeds, prompts and the character order for reuse.
- **Rights and disclosure**: AI-generated imagery may need labelling on the platform.

## Check before publishing
Count people, compare each face to its portrait, read every screen at full size, and look at hands and edges.
