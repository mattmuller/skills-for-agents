My hero parallax barely moves, and in one page it is completely stuck even though DevTools shows a transform applied. Fix it and explain.

```html
<section class="hero">
  <div class="hero-bg"><img src="hero.jpg" alt=""></div>
  <h1>Welcome</h1>
</section>
<style>
.hero { position: relative; height: 100svh; overflow: hidden; }
.hero-bg { position: absolute; inset: 0; animation: lag linear both; animation-timeline: view(); animation-range: entry 0% exit 100%; }
@keyframes lag { from { transform: translateY(-180px); } to { transform: translateY(180px); } }
</style>
```
The hero is the first thing on the page.
