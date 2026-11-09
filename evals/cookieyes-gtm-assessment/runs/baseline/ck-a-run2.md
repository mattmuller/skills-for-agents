# Diagnosis: two cookie banners and a CookieYes console error

## Most likely cause: CookieYes is loaded twice

The site code hard-codes the CookieYes script in `<head>`. The GTM container also has a "CookieYes CMP" tag (the CookieYes template) on All Pages. Both load the same CMP, so the banner renders twice. The script initialises twice, and that is the likely source of the console error. Typical symptoms are "already initialised", duplicate `cookieyes` / `cky` element IDs, or a failed `getElementById` / null reference inside `script.js`.

## Second problem: consent defaults race and may conflict

- The "Default consent" Custom HTML tag fires on Consent Initialization, but it is a separate source of defaults from the CookieYes template. With Support GCM on, the template also sets its own defaults and updates.
- The custom tag sets only `ad_storage` and `analytics_storage`. It omits `ad_user_data`, `ad_personalization`, `functionality_storage`, `personalization_storage` and `security_storage`. Consent Mode v2 needs the first two.
- The hard-coded script in `<head>` can run before GTM and push its own `gtag('consent','default')` or `update`. That makes ordering unpredictable.
- "CookieYes CMP" fires on All Pages, so it also fires too late. A CMP tag must run on Consent Initialization - All Pages, before any other tag.
- GA4 Config uses "CookieYes CMP" as a setup tag, which is fine. But with the late trigger and the duplicate load, the sequencing is not reliable.

## What to change

1. **Choose one loading method.** The cleanest option is GTM only: delete the hard-coded `<script id="cookieyes">` from the layout. The alternative is to keep the hard-coded script and delete the GTM tag. Do not keep both.
2. **If you keep GTM:** change the "CookieYes CMP" trigger to Consent Initialization - All Pages. Fire it first, with a tag sequence or priority above any other consent tag.
3. **Delete the "Default consent" Custom HTML tag.** Let the CookieYes template, with GCM support on, set the defaults. If you need region-specific defaults, set them in the CookieYes dashboard or in the template's fields, not in a second source.
4. **Set the full v2 defaults** in the template: `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`, `functionality_storage`, `personalization_storage` and `security_storage`. Use `wait_for_update` of about 500 ms.
5. Keep the GA4 Config setup-tag dependency. Turn on built-in consent checks for GA4 so it respects `analytics_storage`.

## What else to check

- **Other injection routes.** Look for a CookieYes WordPress or Shopify plugin or app embed, a theme snippet, or a second GTM container. A plugin is a common hidden second loader.
- **The framework GTM component.** Confirm it loads only one container, and that it does not also inject a CMP.
- **The console error text and its stack frame.** Note the exact message and line. Also check for ad-blockers or CSP blocking `cdn-cookieyes.com`, and for a wrong `<KEY>`, which gives a 404 on `script.js`.
- **GTM Preview / Tag Assistant.** Verify that CookieYes fires once, on Consent Initialization, and that the Consent tab shows defaults denied and then updated after the choice.
- **The Network tab.** Confirm `script.js` is requested once.
- **GCM state in the dataLayer.** Use `google_tag_data.ics` or the Tag Assistant consent view.
- **Cache and CDN.** Purge after the fix, because stale pages may still carry both loaders.
- **Cookie scan and banner settings** in the CookieYes dashboard (one banner, correct regions and language).
