# Recommendation: CSS scroll-driven animations, not framer-motion

Both effects depend on scroll position, which CSS now handles natively. Use `animation-timeline: view()` for the card reveal and `scroll()` for the progress bar.

Why this beats framer-motion plus an Intersection Observer:

- **No client JS.** `motion.*` needs `'use client'`, so every card becomes a client boundary and you ship the library for a fade.
- **Compositor-driven.** No scroll listeners, no observer callbacks, no hydration cost.
- **Cards stay Server Components.** Only a class name changes.

The catch is browser support. Chromium and Safari have it. Firefox has lagged, so check caniuse. Wrapping everything in `@supports` means unsupported browsers simply see static, fully visible content.

## CSS

```css
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .card-reveal {
      animation: card-rise linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 40%;
    }
    @keyframes card-rise {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: none; }
    }

    .read-progress {
      position: fixed;
      inset: 0 0 auto 0;
      height: 3px;
      background: hsl(var(--primary));
      transform-origin: 0 50%;
      animation: read-grow linear both;
      animation-timeline: scroll(root);
      z-index: 50;
    }
    @keyframes read-grow {
      from { transform: scaleX(0); }
      to   { transform: scaleX(1); }
    }
  }
}
```

## Usage (both Server Components)

```tsx
export function ArticleCard({ post }: { post: Post }) {
  return (
    <article className="card-reveal rounded-lg border bg-card p-6">
      <h2>{post.title}</h2>
      <p>{post.excerpt}</p>
    </article>
  );
}

// app/blog/[slug]/page.tsx
export default function Page() {
  return (
    <>
      <div className="read-progress" aria-hidden="true" />
      {/* article body */}
    </>
  );
}
```

Render the bar in the article page or layout only. `scroll(root)` tracks the whole page; to track just the article body, use a named `view-timeline` on the `<article>`.

## If you must support older browsers

Add a small client fallback that does nothing where CSS support exists, and apply the hidden state only inside the effect so server HTML stays visible:

```tsx
'use client';
import { useEffect, useRef } from 'react';

export function RevealFallback({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (CSS.supports('animation-timeline: view()')) return;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const el = ref.current!;
    el.style.cssText = 'opacity:0;transform:translateY(16px);transition:.5s';
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        el.style.opacity = '1';
        el.style.transform = 'none';
        io.disconnect();
      }
    });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return <div ref={ref}>{children}</div>;
}
```

Keep framer-motion for later if you need springs, layout animations or gestures.
