# Recommendation: CSS scroll-driven animations, no framer-motion, no observer

Both effects are tied to scroll position, so CSS can do them with zero JavaScript. That keeps your cards as Server Components. framer-motion would force `'use client'` on every card, add bundle weight, and make each card hydrate just to fade in. An Intersection Observer also needs a client component, and it flashes unstyled content before hydration.

Support: Chrome/Edge and Safari have `animation-timeline`. Firefox support lags (verify on caniuse). Wrapping the rules in `@supports` makes this progressive enhancement. Unsupported browsers simply show the cards and no bar. Nothing is ever hidden.

## CSS (`globals.css`)

```css
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .card-reveal {
      animation: card-in linear both;
      animation-timeline: view();
      animation-range: entry 0% entry 35%;
    }
    @keyframes card-in {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: none; }
    }

    .reading-progress {
      position: fixed;
      inset: 0 0 auto 0;
      height: 3px;
      background: var(--primary);
      transform-origin: left;
      animation: grow linear both;
      animation-timeline: scroll(root block);
      z-index: 50;
    }
    @keyframes grow {
      from { transform: scaleX(0); }
      to   { transform: scaleX(1); }
    }
  }
}
```

Reduced-motion users get the static page. The bar is decorative, so hiding it for them is fine.

## Usage (all Server Components)

```tsx
// components/ArticleCard.tsx - no 'use client'
export function ArticleCard({ post }: { post: Post }) {
  return (
    <article className="card-reveal rounded-lg border bg-card p-6">
      <h2>{post.title}</h2>
      <p className="text-muted-foreground">{post.excerpt}</p>
    </article>
  );
}

// app/blog/[slug]/page.tsx
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  return (
    <>
      <div className="reading-progress" aria-hidden="true" />
      <article>{/* ... */}</article>
    </>
  );
}
```

## Notes

- **Bar scope:** `scroll(root block)` measures the whole page, including comments and footer. If you want progress through the article body only, use `animation-timeline: view()` on the `<article>` element with `animation-range: contain` as the target, or accept the page-level approximation.
- **Stagger in a grid:** each card has its own view timeline, so cards in one row animate together. For a stagger, add a small `animation-range-start` offset per column with `:nth-child`.
- **Never set `opacity: 0` as a base style.** Only the animation controls it.

## When to reach for framer-motion instead

Use it only if you need exit animations, layout or shared-element transitions, or gesture-driven motion. None of those is needed here.

## Optional fallback for Firefox

If the bar must appear everywhere, add one tiny client component (about 15 lines) that sets `scaleX` from `scrollY / (scrollHeight - innerHeight)` in a passive scroll listener. Render it only where `CSS.supports('animation-timeline: scroll()')` is false. Cards need no fallback, since showing them statically is acceptable.
