# CookieYes + GTM diagnosis

**Scope:** I only have the layout snippet and a tag list. I have no container export, no browser, no CSP headers and no CookieYes dashboard. Anything needing those is marked "not checked".

## 1. One consent manager, loaded one way: FAIL (main cause)
The layout hard-codes `<script id="cookieyes" src=".../script.js">`. The GTM tag "CookieYes CMP" also loads CookieYes. That is two loads of the same banner. This explains both symptoms:
- **Two banners:** each load renders its own.
- **Console error from a CookieYes file:** the script initialises twice, or its second run hits an already-built DOM.

**Fix:** pick GTM as the single route and delete the hard-coded script tag from the layout. Also grep the whole repo for `cookieyes` and the website key (plugins, theme files, Shopify-style liquid templates) and check for any second CMP. Not checked: the rest of the codebase.

## 2. The GTM tag: FAIL on several points
- **Trigger:** "CookieYes CMP" fires on All Pages. It must fire on **Consent Initialization - All Pages**, so consent is set before other tags evaluate. This also lets tags fire before consent.
- **Duplicate default consent:** the Custom HTML "Default consent" tag also sets defaults. It races the template's own defaults (Support GCM is on). Delete it, or at least stop it competing. It also sets only two of the seven types.
- **Setup tag:** "GA4 Config" uses "CookieYes CMP" as a setup tag. Remove that link. Rely on consent settings and the Consent Initialization trigger instead.
- **Not checked:** the website key in the template against the dashboard.

## 3. Consent Mode v2 signals: partly wrong, rest unverified
The custom default sets only `ad_storage` and `analytics_storage`. It omits `ad_user_data` and `ad_personalization`, which v2 requires. After removing the custom tag, let the CookieYes template set all defaults. Then verify in Tag Assistant or `dataLayer`: defaults are `denied` before the first Google tag fires, accept moves the right types to `granted`, reject leaves them `denied`. Read the category-to-type mapping from the dashboard; do not assume it. Not checked: live signals.

## 4. CSP: not checked
If the shop sends a CSP, confirm `script-src` and `connect-src` allow the CookieYes CDN and logging domains. Copy the domains from the Network tab. A block also produces a console error and a lost choice.

## 5. Check after the fix (clean state)
Open a private window with extensions off. Confirm one banner and no console error. Read the consent defaults before touching the banner. Accept, reload, and confirm the choice persists. Repeat with reject. If the choice is lost, check CSP, ad blockers and cookie domain.

## Order of changes
1. Remove the hard-coded script.
2. Move the CookieYes CMP trigger to Consent Initialization - All Pages.
3. Delete the custom "Default consent" tag.
4. Remove the setup-tag link from GA4 Config.
5. Re-test.
