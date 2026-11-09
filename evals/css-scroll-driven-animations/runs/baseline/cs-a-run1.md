# Hero parallax: why it barely moves, and why one page is stuck

## Cause 1: the range starts before the page can scroll

The hero is the first thing on the page. At scroll 0 it is already fully inside the viewport. `animation-range: entry 0% exit 100%` runs from the moment the hero's top edge enters at the bottom of the viewport to the moment its bottom edge leaves at the top. That span is about 200svh of scroll.

At load you are already about 50% through it, and the page only scrolls about 100svh before the hero is gone. So:

- The animation starts mid-way, at roughly `translateY(0)`, so the keyframe's `-180px` start is never seen.
- It only covers the second half of the keyframes. You get 0 to 180px of movement, spread over a full viewport of scroll. That reads as "barely moves".

For a hero that is already on screen, use only the exit phase: `exit 0% exit 100%`. Or use `cover 0% cover 100%` and keyframes that start at 0.

## Cause 2: the stuck page (transform shows, nothing moves)

A `view()` timeline tracks the nearest ancestor scroll container. If something between the hero and the viewport has `overflow: hidden`, `auto` or `clip` on one axis, that element becomes the scroller. A common case is `overflow-x: hidden` on `body` or a wrapper, or `html { overflow: hidden }` with an inner scroll area. If that element does not scroll, the timeline progress never changes. DevTools shows a transform because the animation holds its initial frame (`both` fill), but it never advances.

Fix: remove the overflow from the ancestor. Use `overflow-x: clip` on the wrapper, which does not create a scroll container. Or bind the timeline explicitly to the real scroller with `scroll(root)`.

Two further traps:

- If `animation-timeline` comes before the `animation` shorthand, the shorthand resets it to `auto`. Your order is correct. Keep it that way.
- The element is observed through its own box. Make the subject something that does not move, as in the fix below.

## Cause 3: the image runs out of room

`.hero-bg` is `inset: 0` and translates up to 180px. Because the hero has `overflow: hidden`, a gap appears at the top or bottom as soon as the layer moves. Oversize the layer by at least the travel distance.

## Fix

```html
<section class="hero">
  <div class="hero-bg"><img src="hero.jpg" alt=""></div>
  <h1>Welcome</h1>
</section>
<style>
.hero { position: relative; height: 100svh; overflow: clip; }
.hero-bg {
  position: absolute;
  inset: -180px 0;            /* room for the travel */
}
.hero-bg img { width: 100%; height: 100%; object-fit: cover; }

@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .hero-bg {
      animation: lag linear both;
      animation-timeline: scroll(root block);   /* nearest-scroller trap avoided */
      animation-range: 0 100svh;                /* hero's whole time on screen */
    }
    @keyframes lag {
      from { transform: translateY(0); }
      to   { transform: translateY(180px); }    /* slower than the page */
    }
  }
}
</style>
```

- `scroll(root)` ties the animation to the document scroll from 0 to 100svh. That is exactly the hero's time on screen, and it is independent of the hero's own box.
- If the hero is not the first element, use `view-timeline: --hero block` on `.hero` and `animation-timeline: --hero` on the child, with `animation-range: exit 0% exit 100%`.
- The `@supports` and reduced-motion guards leave the image static in browsers that lack scroll-driven animations and for users who ask for less motion.
