# GTM + CookieYes: analytics fires before consent

## What is wrong

1. **Ordering.** The GA4 config (step 3) runs before the consent default (step 4). GA4 has no consent state yet, so it sends a hit as fully granted. That is the leak the review found. The `denied` default arrives too late to affect it.
2. **CookieYes is loading late.** Its consent default must be the first thing in the dataLayer, before `gtm.js`. Here it runs after `gtm.dom`, so it is probably loaded through GTM or deferred instead of being hard-coded in the page head.
3. **GA4 is not gated.** The GA4 tag fires on a plain trigger (for example Initialization or All Pages) and has no consent requirement. Even with a correct default, it would still depend on timing.
4. **Consent Mode v2 is incomplete.** The default sets only `ad_storage` and `analytics_storage`. v2 also needs `ad_user_data` and `ad_personalization`. Without them, Google ads and audience features can be treated as non-compliant. Also consider `functionality_storage`, `personalization_storage` and `security_storage`.
5. **`wait_for_update: 500` is too short.** CookieYes needs time to read a stored choice. A returning visitor's saved choice may arrive after 500 ms, so the visitor is treated as denied and then updated. This is a smaller issue.
6. **No region logic.** The default is `denied` everywhere. That is the safest setting, but you can scope it with `region` if you want different behaviour outside the EEA and UK.

## What the sequence should look like

1. `["consent","default",{ad_storage:"denied",analytics_storage:"denied",ad_user_data:"denied",ad_personalization:"denied",wait_for_update:500}]`, also set `["set","url_passthrough",true]` and `["set","ads_data_redaction",true]` if wanted.
2. `gtm.js` (container loaded)
3. `gtm.dom` and the other built-in events
4. GA4 tag evaluated. Consent is denied, so it either does not fire or sends cookieless pings only if Consent Mode (advanced) is intended.
5. Banner shown
6. User clicks Accept: `["consent","update",{ad_storage:"granted",analytics_storage:"granted",ad_user_data:"granted",ad_personalization:"granted"}]`
7. GA4 fires, now with granted state.

## What to change

- **Put CookieYes first.** Paste the CookieYes script as the first script in `<head>`, above the GTM snippet. Remove any copy of it that loads through a GTM tag. Turn on its GTM/Google Consent Mode integration in the CookieYes dashboard.
- **Add a hard-coded default** before GTM if the CookieYes script is not first. It must include all four v2 signals.
- **Gate the GA4 tag.** In GTM, open the tag, go to Advanced Settings, then Consent Settings, and require `analytics_storage`. Enable the container's "Enable consent overview". Use Google tags with built-in consent checks.
- **Fire GA4 on Initialization, not before consent.** Keep the config and event tags on a trigger that the consent update can release.
- **Choose basic or advanced mode on purpose.** Basic: nothing loads until Accept. Advanced: cookieless pings go out while denied. Tell the privacy reviewer which you chose, as advanced still sends data.
- **Verify.** Clear cookies, open a private window, and check in GTM Preview and the Network tab. There must be no `google-analytics.com/g/collect` request before Accept (or only `gcs=G100` cookieless pings in advanced mode). After Accept, `gcs=G111` should appear.
