# Recommendation: native CSS scroll-driven animations, no JS

Use neither framer-motion nor an Intersection Observer. Both effects follow scroll position, so CSS `animation-timeline` handles them. You get no client component, no hydration cost, and your Server Components stay Server Components. (`motion` and IO would force `'use client'` on every card or a wrapper.)

## CSS (put it next to your existing animation CSS, e.g. `globals.css`)

```css
/* Static fallback first: cards and bar are valid with no animation support. */
@supports (animation-timeline: view()) {
  @keyframes reveal-up {
    from { opacity: 0; transform: translateY(2rem); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .reveal-up {
    animation: reveal-up linear both;
    animation-timeline: view();
    animation-range: entry 0% entry 100%;
  }

  @keyframes fill-bar {
    from { transform: scaleX(0); }
    to   { transform: scaleX(1); }
  }

  .reading-progress {
    position: fixed;
    inset: 0 0 auto 0;
    height: 3px;
    z-index: 50;
    background: hsl(var(--primary));
    transform-origin: left;
    animation: fill-bar linear;
    animation-timeline: scroll(root block);
  }
}

@media (prefers-reduced-motion: reduce) {
  .reveal-up,
  .reading-progress { animation: none; transform: none; opacity: 1; }
}
```

Wrapping in `@supports` matters. An unsupported browser (Safari 17 and older) would otherwise stay on the `from` keyframe, leaving cards at `opacity: 0`. Here they simply show normally, and the bar does not render.

## Components (both stay Server Components)

```tsx
// app/blog/page.tsx
{posts.map((post) => (
  <article key={post.slug} className="reveal-up rounded-lg bg-card p-6">
    {/* card content */}
  </article>
))}
```

```tsx
// app/blog/[slug]/page.tsx
<div className="reading-progress" aria-hidden="true" />
```

The bar is decorative, so `aria-hidden` is right. Put it only in the article layout or page, so it appears only there.

## Gotchas

- **`overflow: hidden` on an ancestor** of the cards can freeze the `view()` timeline, because it makes that ancestor the scroll container. Use `overflow-clip` instead (Tailwind), not `overflow-hidden`.
- **Cards already visible at scroll 0** (first row on a tall screen) have finished "entering" before load, so they show part-way faded. If that looks off, start those cards with `animation-range: entry 100% cover 30%`, or leave the first row without the class.
- **Animate only `transform` and `opacity`.** That is what the code does, and it keeps the work off layout and paint.
- **Stagger:** a per-card `animation-delay` does nothing on a scroll timeline. Each card's progress follows its own position, which gives a natural stagger when the rows sit at different heights.

## Support and when to fall back

Chrome, Edge, Opera, Firefox and Safari 18+ support it (verified April 2026 by the skill's author; recheck MDN before launch). Older Safari gets the static, fully visible look. If you must have identical animation in every browser, or need scroll velocity or direction logic, then accept a client component and use a JS library. For a blog, the graceful fallback is almost certainly fine.

## Verification

Not run: I wrote this from the skill's reference, and I did not test it in a browser or in your codebase.
