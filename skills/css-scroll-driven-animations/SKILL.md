---
name: css-scroll-driven-animations
description: Use native CSS scroll-driven animations (animation-timeline view() and scroll()) for any effect whose progress is tied to scroll position - parallax, reveal on scroll, scroll-linked progress bars, fade-ins, image drift, header or hero lag. Use when the user asks for parallax, scroll effects, scroll-triggered animation, reveal on scroll, a reading-progress bar, or animation-timeline, and also when they suggest an animation library, Intersection Observer or a scroll listener for motion that simply follows scroll position.
---

# CSS scroll-driven animations

Native `animation-timeline` ties an animation's progress to scroll position with no JavaScript. It needs no client-side component, and the browser can run it off the main thread, which is cheaper than a `scroll` listener with `requestAnimationFrame`. Always pair it with `prefers-reduced-motion`.

## When to use it

- Parallax backgrounds.
- Reveal on scroll (fade or slide in as an element enters).
- Scroll-linked progress bars and sticky indicators.
- Any animation whose progress is driven by scroll position.

## When not to use it

- Identical behaviour is required in browsers without support. Check current support (caniuse or MDN) before choosing; see "Support" below.
- The animation is tied to time, not scroll. Use `@keyframes` with `animation-duration`.
- You need scroll velocity or direction logic. Use a JavaScript scroll library.

## Two timeline types

### `view()`: an element's visibility in the viewport

Progress follows how much of the element is visible.

```css
.reveal-on-scroll {
  animation: slide-up linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;   /* plays while the element enters */
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(2rem); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### `scroll()`: progress of a scroll container

Progress follows the container's total scroll position. Use it for reading-progress bars.

```css
.reading-progress {
  transform-origin: left;
  animation: fill-bar linear;
  animation-timeline: scroll(root block);
}
@keyframes fill-bar {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
```

## `animation-range` cheat sheet

| Range | When the animation plays |
|---|---|
| `entry 0% entry 100%` | While the element enters the viewport |
| `exit 0% exit 100%` | While it exits |
| `entry 0% exit 100%` | Full traversal: enter, scroll through, exit |
| `cover 0% cover 100%` | The whole time any part is visible |
| `contain 0% contain 100%` | Only while fully inside the viewport |

## Sharp edges

### `overflow: hidden` on an ancestor can freeze a `view()` timeline

`view()` tracks the element relative to its nearest scroll container. `overflow: hidden` makes an element a scroll container even when nothing scrolls inside it. If such an ancestor sits between the animated element and the viewport, the animation still runs and computed styles show a transform, but the timeline tracks the element inside that container and the value stays stuck at one position.

Use `overflow: clip` instead. It clips painting without creating a scroll container, so `view()` keeps resolving against the viewport. In Tailwind that is `overflow-clip`, not `overflow-hidden`. Observed in Chrome; test in your target browsers.

```css
.hero { overflow: hidden; }  /* animation freezes */
.hero { overflow: clip; }    /* view() still tracks the viewport */
```

### Elements at the top of the page need `entry 100%` as the start

At scroll position 0 an element at the top of the page is already fully visible: its "entry" phase happened before the page loaded. With `entry 0% exit 100%` the animation starts part-way through and only the remaining fraction maps onto real scrolling, often too little to notice. Use `animation-range: entry 100% exit 100%` so the full keyframe spans the scroll distance the user actually has.

### Cover the gap a translation exposes

If a keyframe moves an absolutely positioned element by, say, 180px each way, strips of empty space show at the edges of its container at some scroll positions. Extend the element past its container by at least the maximum translation plus a small buffer, and put `overflow: clip` on the container.

```html
<div class="hero">                      <!-- position: relative; overflow: clip -->
  <div class="hero-bg"></div>        <!-- position: absolute; inset-block: -240px; inset-inline: 0 -->
</div>
```

Animate the wrapper that holds the image and any overlay, not the image alone, so the pair moves as one unit and text contrast stays constant.

## Rules

1. **Pair every scroll-driven animation with `prefers-reduced-motion`.** Add a matching `@media (prefers-reduced-motion: reduce)` rule that sets `animation: none; transform: none;`.
2. **Do not add JavaScript for plain scroll-tied motion.** If you are about to add a scroll listener or Intersection Observer only for this, use CSS.
3. **No client-side component is needed.** In a server-rendered framework, do not mark a component client-only just for a scroll effect.
4. **Put keyframes next to your existing animation CSS** instead of making a new file per effect.
5. **Name classes by purpose** (`hero-parallax`, `reveal-up`), not `fx-a`.
6. **Design a valid static fallback.** Browsers without support ignore `animation-timeline` and the element stays at its `from` keyframe. Make `from` a correct static look; an identity transform usually is.

## Example: hero parallax

```css
@keyframes hero-parallax {
  from { transform: translateY(0); }
  to   { transform: translateY(-12%); }
}

.hero-parallax {
  animation: hero-parallax linear both;
  animation-timeline: view();
  animation-range: entry 0% exit 100%;
  will-change: transform;
}

@media (prefers-reduced-motion: reduce) {
  .hero-parallax { animation: none; transform: none; }
}
```

For a hero at the very top of the page, change the range to `entry 100% exit 100%` as described above.

## Performance

- Animate only `transform` and `opacity`; they avoid layout and paint.
- Use `will-change: transform` sparingly, only on elements that are animating.

## Support

Verified by the skill's author in April 2026: Chrome, Edge and Opera shipped; Firefox listed as shipped; Safari 18 and later shipped; Safari 17 and older ignore the property and show the static fallback. Browser support moves quickly, so check MDN's compatibility table for `animation-timeline` before relying on this. Where an older browser is a hard requirement, use a JavaScript scroll library and accept a client-side component.

## References

- MDN: `animation-timeline`
- MDN: `animation-range`
- MDN: Using CSS scroll-driven animations
