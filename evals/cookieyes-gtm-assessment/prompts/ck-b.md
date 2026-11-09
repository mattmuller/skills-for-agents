Our shop uses GTM + CookieYes. A privacy review says analytics hits go out before the visitor chooses. Here is the dataLayer sequence captured on first page load in a clean private window, in order:

1. gtm.js (Container Loaded)
2. event: gtm.dom
3. ["config","G-XXXX"] (GA4 config fires, hit sent)
4. ["consent","default",{"ad_storage":"denied","analytics_storage":"denied","wait_for_update":500}]
5. banner shown
6. user clicks Accept -> ["consent","update",{"ad_storage":"granted","analytics_storage":"granted"}]

What is wrong, what should the sequence look like, and what exactly should we change? Mention anything about Consent Mode v2 you notice.
