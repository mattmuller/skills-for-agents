# Assessment: analytics hit fires before consent

Scope: I had only the dataLayer capture. I had no GTM container export, no site code and no CookieYes dashboard. The checks below that need those are marked "not checked".

## What is wrong

1. **The GA4 config fires (step 3) before the consent default is set (step 4).** The hit is sent with no consent state. The privacy review is right. The `denied` default arrives after the hit has gone out.
2. **The default is set too late.** Consent defaults must be set before any other tag evaluates. In GTM that means the CookieYes tag (or a default-consent tag) must run on the **Consent Initialization - All Pages** trigger. Probable cause: the CookieYes tag, or a custom `gtag('consent','default')` snippet, is on All Pages or Page View. The GA4 tag also fires on a plain trigger. I cannot confirm this without the container.
3. **Consent Mode v2 is incomplete.** The default sets only `ad_storage` and `analytics_storage`. v2 has seven types: `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`, `functionality_storage`, `personalization_storage` and `security_storage`. `ad_user_data` and `ad_personalization` are missing. They are the two added in v2. Without them, Google ads and remarketing features may not work for EEA traffic. The update on Accept also grants only two types.
4. **`wait_for_update: 500` does little here.** It only helps when a CMP sends an update soon after the default. This banner waits for a click, so the value is only useful for returning visitors whose stored choice loads quickly.

## Correct sequence

1. Consent Initialization: `["consent","default",{ad_storage:"denied", analytics_storage:"denied", ad_user_data:"denied", ad_personalization:"denied", functionality_storage:"denied", personalization_storage:"denied", security_storage:"granted", wait_for_update:500}]`
2. gtm.js, then gtm.dom
3. Banner shown. GA4 config and event tags are held by consent, or send only cookieless pings.
4. User clicks Accept: `["consent","update",{...all relevant types "granted"}]`
5. GA4 config fires with `analytics_storage: granted`.
6. On Reject, the types stay `denied`.

## What to change

- **CookieYes tag:** use the CookieYes template, put its trigger on Consent Initialization - All Pages, and confirm the website key matches the dashboard. Turn on Google Consent Mode in the template.
- **Remove any other default-consent source:** custom HTML tags calling `gtag('consent','default')` and any CookieYes script pasted into the site code. Only one may set defaults.
- **Add the missing v2 types** to the default and update in the template and the CookieYes dashboard. Check which CookieYes category maps to which type. Do not assume it.
- **GA4 tag:** keep its trigger as it is. Add built-in consent checks: require `analytics_storage`. Do not rely on trigger order alone.
- **Do not make CookieYes a setup tag** for other tags.
- **CSP:** if the site sends a CSP header, allow the CookieYes CDN and logging domains. Copy the domains from the Network tab.

## Verify

Open a private window with extensions off. Read the dataLayer before touching the banner. Confirm the default comes first, with all seven types. Confirm no GA hit leaves before the choice. Accept, confirm the update, reload, and confirm the choice persists. Repeat with Reject.

## Not checked

Container tags and triggers, site code for hard-coded CookieYes scripts, the website key, the CookieYes category mapping and the CSP.
