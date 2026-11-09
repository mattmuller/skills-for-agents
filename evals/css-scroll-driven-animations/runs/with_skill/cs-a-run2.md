## Cause

Three separate problems.

1. **`overflow: hidden` on `.hero` (the "stuck" page).** It makes `.hero` a scroll container, even though nothing scrolls in it. `view()` then tracks `.hero-bg` against `.hero`, not the viewport. The animation runs and DevTools shows a transform, but the value stays frozen. Use `overflow: clip`, which clips painting without creating a scroll container.

2. **Wrong range for a hero at the top of the page ("barely moves").** At scroll 0 the hero is already fully visible, so its entry phase is over before the user scrolls. With `entry 0% exit 100%` the animation starts part-way through, and only the remaining fraction maps onto real scroll distance. Use `entry 100% exit 100%`, so the whole keyframe spans the scroll the user actually has.

3. **Keyframes are not a valid static look, and they expose gaps.** `from` is `translateY(-180px)`. Browsers without support, and reduced-motion users, are stuck at that offset. And `inset: 0` with a 180px translation shows empty strips at the container edge.

## Fix

```html
<section class="hero">
  <div class="hero-bg hero-parallax"><img src="hero.jpg" alt=""></div>
  <h1>Welcome</h1>
</section>
<style>
.hero { position: relative; height: 100svh; overflow: clip; }

/* Extend past the container by more than the max translation (180px) plus a buffer */
.hero-bg {
  position: absolute;
  inset-block: -240px;
  inset-inline: 0;
}
.hero-bg img { width: 100%; height: 100%; object-fit: cover; }

@keyframes hero-parallax {
  from { transform: translateY(0); }      /* identity: a correct static fallback */
  to   { transform: translateY(180px); }  /* background lags behind the scroll */
}

.hero-parallax {
  animation: hero-parallax linear both;
  animation-timeline: view();
  animation-range: entry 100% exit 100%;
  will-change: transform;
}

@media (prefers-reduced-motion: reduce) {
  .hero-parallax { animation: none; transform: none; }
}
</style>
```

## Why each change

- `overflow: clip` keeps the timeline resolving against the viewport. It still hides the extended background. This was observed in Chrome, so test your target browsers.
- `entry 100% exit 100%` gives the full 0 to 180px travel across the real scroll distance (hero top at the viewport top, until it has fully left).
- The wrapper `.hero-bg` is animated, not the `img`, so any overlay on it moves as one unit and text contrast stays constant.
- The `-240px` insets cover the 180px translation plus a 60px buffer. Without them the background's top edge pulls away from the hero.
- `from` is now the identity transform, so browsers without `animation-timeline` (Safari 17 and older) show a normal, correct hero.
- Reduced motion turns the effect off entirely.
- No JavaScript or client component is needed. Only `transform` is animated.

## Caveat

The "stuck" symptom is only guaranteed if an `overflow: hidden` ancestor exists on that page. If it persists after switching to `clip`, check for other `overflow` values (`auto`, `scroll`, `hidden`) on ancestors. I did not run this in a browser.
