## Cause

Two separate problems, both from the skill's "sharp edges".

**1. Barely moves: wrong range for a hero at the top of the page.**
The hero is already fully visible at scroll 0, so its "entry" phase happened before the page loaded. With `entry 0% exit 100%`, the animation starts part-way through. Only the remaining fraction of the keyframe is spread over the scroll distance the user actually has, so the ±180px travel is mostly never reached. Fix: start the range at `entry 100%`.

**2. Completely stuck on one page: `overflow: hidden` on an ancestor.**
`overflow: hidden` makes an element a scroll container, even when nothing scrolls inside it. If a `view()` animation sits under such an ancestor, the timeline tracks the element inside that container. The animation still runs and DevTools still shows a transform, but the value stays frozen. `.hero` has `overflow: hidden`, which is the likely culprit. The "one page" that is stuck may also have another `overflow: hidden` or `auto` wrapper higher up (layout, a wrapper div). Check the ancestor chain and switch any of them to `overflow: clip`. This is observed in Chrome, so test in your target browsers.

**3. Gap exposed by the translation (a related bug).**
The background moves ±180px inside a box of the same size (`inset: 0`), so empty strips will show at the top and bottom once it really moves. Extend the element past the container by more than the maximum translation, plus a buffer.

## Fixed code

```html
<section class="hero">
  <div class="hero-bg hero-parallax"><img src="hero.jpg" alt=""></div>
  <h1>Welcome</h1>
</section>
<style>
.hero { position: relative; height: 100svh; overflow: clip; }

.hero-bg {
  position: absolute;
  inset-inline: 0;
  inset-block: -200px;           /* more than the 180px travel */
}
.hero-bg img { width: 100%; height: 100%; object-fit: cover; }

.hero-parallax {
  animation: hero-parallax linear both;
  animation-timeline: view();
  animation-range: entry 100% exit 100%;
  will-change: transform;
}

@keyframes hero-parallax {
  from { transform: translateY(0); }
  to   { transform: translateY(180px); }
}

@media (prefers-reduced-motion: reduce) {
  .hero-parallax { animation: none; transform: none; }
}
</style>
```

## Notes

- **Static fallback.** The `from` keyframe is now an identity transform. In browsers without `animation-timeline` support (Safari 17 and older), the image stays centred and correct. Your original `from` of `-180px` would have left a shifted image there.
- **Direction.** At the top of the page the useful travel is one-way as the hero scrolls out, so the image drifts from 0 to +180px. That lags behind the page, which is the usual hero effect. The wrapper moves as one unit, so the image and any overlay stay together and text contrast does not change.
- **Reduced motion.** The media query disables the animation and the transform.
- **No JavaScript.** Plain scroll-tied motion does not need a scroll listener or a client component.
- **Other pages.** If the hero is still stuck somewhere, inspect its ancestors for `overflow: hidden`, `auto` or `scroll`. Tailwind's `overflow-hidden` becomes `overflow-clip`.
- **Not run.** I did not run this in a browser, so check it in Chrome, Safari and Firefox.
