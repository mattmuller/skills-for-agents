# CookieYes + GTM diagnosis

Likely cause: CookieYes is loaded twice. The same banner script is hard-coded in the layout and also injected by the "CookieYes CMP" GTM tag. This explains both symptoms. Two instances each render a banner, and the second initialisation throws an error from the CookieYes `script.js`.

## 1. One consent manager, one route (found: broken)
- The layout has a hard-coded `<script id="cookieyes" ...>` and GTM also has the CookieYes template tag.
- Fix: choose GTM and delete the hard-coded script tag. Keep one route only.
- Check: grep the whole codebase for `cookieyes` and the website key. Look in other layouts, themes, plugins and the shop platform's apps or integrations. Confirm no second CMP is active.

## 2. GTM tag (found: three problems)
- "CookieYes CMP" fires on **All Pages**. Change the trigger to **Consent Initialization - All Pages**.
- "Default consent" is a Custom HTML tag that calls `gtag('consent','default',...)`. It competes with the CookieYes template, which sets defaults itself when Support GCM is on. Remove it, or make it the only default setter and turn off the template's defaults. Never keep both.
- "GA4 Config" uses "CookieYes CMP" as a setup tag. Remove that link. It ties firing order to the CMP tag. Rely on consent initialisation and the consent state instead.
- Check: the website key in the template matches the CookieYes dashboard. I could not verify this from what you gave me.

## 3. Consent Mode v2 signals (found: incomplete)
- The custom default sets only `ad_storage` and `analytics_storage`. Consent Mode v2 also needs `ad_user_data` and `ad_personalization`, and optionally the other three types.
- After removing the custom tag, set the full defaults in the CookieYes template.
- Check in Tag Assistant or `dataLayer`: default is `denied` before the first Google tag. Accept moves the right types to `granted`. Reject keeps them `denied`. Read the category-to-signal mapping from the template and dashboard. Do not assume it.

## 4. CSP (not checked)
- If the site sends a CSP header, check `script-src` and `connect-src` for the CookieYes CDN and logging domains. Copy the domains from the Network tab.
- A block here causes script errors and choices that are not remembered.

## 5. Other checks
- Load timing: the script error may also come from loading before the DOM is ready. Re-test after the fixes before chasing this.
- The framework GTM component could render the snippet twice (for example once in layout and once in a page or template). Check that GTM appears once.
- Ad blockers and extensions can also produce console errors.

## 6. Clean test
- Use a private window with extensions off. Read the consent signals before touching the banner.
- Expect one banner and no console error.
- Accept, check the update event, reload, and confirm the choice persists.

## Not checked
I had no container export, CSP headers, website key or browser access. Everything above comes from the snippets supplied.
