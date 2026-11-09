# Recommendation: native CSS scroll-driven animations, no framer-motion, no Intersection Observer

Both effects are driven purely by scroll position, so CSS `animation-timeline` covers them. That means no client components, no JS bundle cost, and your cards and article pages stay Server Components. Framer-motion or an Intersection Observer would force `'use client'` on every card wrapper for no gain.

## 1. Card reveal (`view()` timeline)

```css
/* globals.css, next to your other animation CSS */
@keyframes reveal-up {
  from { opacity: 0; transform: translateY(2rem); }
  to   { opacity: 1; transform: translateY(0); }
}

.reveal-up {
  animation: reveal-up linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;   /* plays while the card enters */
}

@media (prefers-reduced-motion: reduce) {
  .reveal-up { animation: none; transform: none; opacity: 1; }
}
```

```tsx
// ArticleCard.tsx - stays a Server Component
export function ArticleCard({ post }: { post: Post }) {
  return (
    <article className="reveal-up rounded-lg border border-border bg-card p-6">
      <h2>{post.title}</h2>
      <p className="text-muted-foreground">{post.excerpt}</p>
    </article>
  );
}
```

Cards already visible on first paint (top of the list) are at the end of their entry phase at scroll 0, so they show at or near their final state. If you want them to animate anyway, use `entry 100% exit 100%` for those only.

## 2. Reading-progress bar (`scroll()` timeline)

```css
@keyframes fill-bar {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}

.reading-progress {
  position: fixed;
  inset: 0 0 auto 0;
  height: 3px;
  background: hsl(var(--primary));
  transform-origin: left;
  transform: scaleX(0);
  animation: fill-bar linear;
  animation-timeline: scroll(root block);
}

@media (prefers-reduced-motion: reduce) {
  .reading-progress { animation: none; transform: none; }
}
```

```tsx
// app/blog/[slug]/page.tsx (Server Component)
<div className="reading-progress" aria-hidden="true" />
```

Reduced-motion note: a static full-width bar would be misleading, so you may prefer `display: none` there instead of `transform: none`.

## Sharp edges for your layout

- **Do not use `overflow-hidden` on an ancestor** of a revealing card (wrappers, grid containers). It creates a scroll container and can freeze the `view()` timeline. Use `overflow-clip` instead.
- **Static fallback is valid.** Unsupported browsers ignore `animation-timeline`. The bar then stays at `scaleX(0)` (invisible), and cards sit at their `from` keyframe (opacity 0), which would hide them. To be safe, wrap the reveal in `@supports (animation-timeline: view()) { ... }` so unsupported browsers get fully visible cards.
- Animate only `transform` and `opacity`.

## Support

Chrome, Edge and Opera ship it. Safari 18+ and Firefox are listed as shipped (verified April 2026), but support moves quickly, so check MDN's `animation-timeline` table before launch. Older browsers get the static fallback above, which is acceptable for decorative motion. Only if identical behaviour in old browsers is a hard requirement should you fall back to a JS library, accepting a client component.
