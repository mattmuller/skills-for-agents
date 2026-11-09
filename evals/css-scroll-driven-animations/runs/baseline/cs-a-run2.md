# Hero parallax: why it stalls and the fix

## Causes

**1. The stuck page: `overflow: hidden` makes `.hero` a scroll container.**
`view()` measures the subject against its *nearest ancestor scroll container*. `.hero-bg` sits inside `.hero`, and `overflow: hidden` turns `.hero` into a scroller, even though it never scrolls. The timeline therefore tracks a scrollport that never moves. Progress stays at 0, so the `from` keyframe (`translateY(-180px)`) stays applied. That is why DevTools shows a transform but nothing moves.

**2. The weak movement elsewhere: the hero is the first thing on the page.**
The range `entry 0%` to `exit 100%` covers the subject's height plus the viewport's height (about 200svh of travel). A top-of-page hero can only scroll about 100svh before it leaves, and scroll position 0 is already the halfway point, because the hero already fills the viewport. The animation therefore only plays its second half, 0 to +180px, and the whole thing is spread over a long scroll. It looks like it barely moves.

**3. A latent bug: the layer is too small.**
`.hero-bg` is exactly `inset: 0`. Translating it by ±180px exposes 180px of empty hero at the top or bottom.

## Fix

Drive the effect from the root scroll position and keep the clipping:

```css
.hero { position: relative; height: 100svh; overflow: clip; } /* clip does not create a scroller */

.hero-bg {
  position: absolute;
  inset: -20% 0 -20% 0;            /* overscan so no gaps show */
  animation: lag linear both;
  animation-timeline: scroll(root);  /* hero is at the top, so use page scroll, not view() */
  animation-range: 0 100svh;         /* play over the hero's own scroll distance */
}
.hero-bg img { width: 100%; height: 100%; object-fit: cover; }

@keyframes lag {
  from { transform: translateY(0); }
  to   { transform: translateY(15svh); }  /* background lags behind the page */
}

@media (prefers-reduced-motion: reduce) {
  .hero-bg { animation: none; }
}
```

Why each change matters:

- `overflow: clip` clips like `hidden` but creates no scroll container, so any `view()` use inside the hero resolves to the page. This fixes the stuck case by itself.
- `scroll(root)` with `0 100svh` maps progress to the one thing that can actually change for a top-of-page element. The animation now starts at scroll 0 and finishes as the hero leaves.
- The `inset` overscan must be at least the translate distance (20% of 100svh is 20svh, which covers 15svh).
- If the hero were mid-page, `view()` with `exit 0% exit 100%` would also work. With `overflow: clip`, you can use `animation-timeline: view()` on the hero itself.
- The reduced-motion block follows the "static fallback" rule for motion.

## Caveats

Scroll-driven animations are unsupported in Firefox (at the time of writing) and older Safari. Wrap the rule in `@supports (animation-timeline: scroll())` so the image simply stays static elsewhere. Animating `transform` stays on the compositor, so it runs smoothly.
