# GTM + CookieYes: analytics fires before consent

## What is wrong

1. **The GA4 config hit (step 3) fires before the consent default (step 4).** GA4 sees no consent state, so it treats analytics as allowed and sends a hit. This is the privacy finding. The hit contains a client ID, page URL and referrer, and it was sent before the visitor chose anything.
2. **The `consent default` arrives too late.** It must be the first thing on the page. Here it comes after `gtm.js`, `gtm.dom` and the config. This usually means CookieYes is loaded through a GTM tag, or loaded late, so it runs after the container starts.
3. **The GA4 tag is not gated on consent.** It fires on a plain All Pages trigger (or a hardcoded `gtag('config')`), with no consent requirement.
4. **Consent Mode v2 is incomplete.** The default sets only `ad_storage` and `analytics_storage`. v2 also needs `ad_user_data` and `ad_personalization`. `ad_user_data` and `ad_personalization` have been required for EEA and UK ad features since March 2024. `functionality_storage`, `personalization_storage` and `security_storage` are optional but usually set too. The update on Accept has the same gap.
5. **Minor:** `wait_for_update: 500` is only useful if a CMP sends an update during that window. It does not help when the default is late.

## What the sequence should look like

1. `["consent","default",{ad_storage:"denied", analytics_storage:"denied", ad_user_data:"denied", ad_personalization:"denied", wait_for_update:500}]`, before `gtm.js`, ideally with region scoping.
2. `gtm.js` (Container Loaded)
3. `gtm.dom`
4. GA4 config tag runs. Consent Mode only allows cookieless pings, or nothing if the tag requires consent. No cookies are set.
5. Banner shown.
6. Accept leads to `["consent","update",{ad_storage:"granted", analytics_storage:"granted", ad_user_data:"granted", ad_personalization:"granted"}]`.
7. GTM re-evaluates, and the GA4 tag fires with full cookies.

## What to change

- **Load CookieYes first.** Put the CookieYes script, with its GCM integration turned on, as the first script in `<head>`, above the GTM snippet. Do not load it from a GTM tag.
- **Or set the default yourself.** Add an inline `gtag('consent','default',{...all four denied...})` before the GTM snippet. CookieYes then sends updates only.
- **Enable Google Consent Mode in CookieYes.** Use the Settings > Consent Mode (GCM) option, and confirm all four v2 signals are mapped to your categories.
- **Gate the GA4 tag in GTM.** Under Advanced Settings > Consent Settings, require `analytics_storage`. Tags that use ads data should also require `ad_storage`, `ad_user_data` and `ad_personalization`. Turn on Consent Overview to check each tag.
- **Remove any hardcoded `gtag('config')`** or duplicate GA tag outside GTM.
- **Return visitors:** CookieYes must replay the stored choice with an update on page load.

## Verify

Test in a clean private window. Use GTM Preview and the Network tab filtered to `collect`. Expected: no `g/collect` request carrying `gcs=G111`-style granted values before Accept. The `gcs` parameter should read `G100` before consent, and `G111` or similar after Accept.
