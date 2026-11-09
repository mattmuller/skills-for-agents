# Assessment: analytics hit before consent

Scope note: I only have the dataLayer capture. I could not check the GTM container, the site code, the CookieYes dashboard or any CSP. Those checks are listed as not done at the end.

## What is wrong

1. **Consent default comes too late (step 4).** `gtm.js`, `gtm.dom` and the GA4 config (steps 1-3) all run before `consent default`. The GA4 hit at step 3 therefore went out with no consent state set. That is the privacy finding, and it is confirmed by your sequence.
2. **The GA4 config is probably on the wrong trigger.** It fires at DOM-ready level, so it is likely on All Pages or Page View. A Google tag that is gated on consent can only fire after the consent state exists.
3. **The consent default is also late.** The CookieYes tag is probably not on **Consent Initialization - All Pages**. That trigger runs before every other tag. A custom HTML tag or hard-coded `gtag('consent','default')` may also be setting it. I cannot tell which from the capture.
4. **`wait_for_update: 500` is not a fix.** It only delays tags that already read a default. Here the default never existed when the hit fired.

## Consent Mode v2 findings

- The default sets only `ad_storage` and `analytics_storage`. Consent Mode v2 has seven types. `ad_user_data` and `ad_personalization` are missing from both the default and the update. They must be set, or Google ads and audiences will not work for EU traffic.
- Also set `functionality_storage`, `personalization_storage` and `security_storage` explicitly. Read the category-to-type mapping from CookieYes. Do not assume it.
- The Accept update (step 6) looks fine for the two types it covers, but is incomplete for the same reason.

## Correct sequence

1. `consent default` with all relevant types `denied` (including `ad_user_data` and `ad_personalization`), plus `wait_for_update`.
2. `gtm.js` / Container Loaded.
3. `gtm.dom`.
4. Banner shown. GA4 either not fired, or fired only as cookieless pings under Consent Mode.
5. User clicks Accept: `consent update` moves all mapped types to `granted`.
6. GA4 config fires, with consent granted.

On Reject, the types stay `denied`.

## What to change

1. Set the CookieYes tag trigger to **Consent Initialization - All Pages**. Use the CookieYes template, with the website key matching the dashboard.
2. Turn on Google Consent Mode in the template. Set all seven defaults to `denied`, in the template.
3. Remove any other default-consent source: custom HTML tags, `gtag('consent','default')` in the page, a second CMP.
4. Remove any hard-coded CookieYes script from the site. Load it by one route only.
5. Do not use the CookieYes tag as a setup tag for other tags.
6. Keep the GA4 tag on All Pages, but turn on built-in consent checks for `analytics_storage`. Then it waits for the update.
7. Confirm the CSP allows the CookieYes domains seen in the Network tab.

## Verify

In a private window with extensions off, read the dataLayer before clicking. Expect `consent default` first and no GA4 request. Accept, confirm the update, reload and confirm the choice persists.

## Not checked

GTM container, tag triggers, site code for a second load, CookieYes category mapping, CSP.
