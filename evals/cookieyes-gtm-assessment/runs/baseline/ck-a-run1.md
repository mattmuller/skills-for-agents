# Diagnosis: two CookieYes banners plus a console error

## Most likely cause: CookieYes is loaded twice

1. **Hard-coded script in the layout.** The `<script id="cookieyes" src=".../script.js">` tag loads CookieYes directly.
2. **GTM tag "CookieYes CMP".** The CookieYes template injects the same CMP script again on All Pages.

Both run and each renders a banner. Two instances also fight over the same `cookieyes-consent` cookie and the same DOM ids. That commonly causes a console error from `script.js` (for example a null element or duplicate initialisation).

## Second problem: consent defaults are wrong and race each other

- The "Default consent" Custom HTML tag fires on Consent Initialization. It sets only `ad_storage` and `analytics_storage`. It omits `ad_user_data`, `ad_personalization`, `functionality_storage`, `personalization_storage` and `security_storage`. Consent Mode v2 needs the two ad signals above, so this default is incomplete.
- It also has no `wait_for_update` and no `region` scoping.
- The CookieYes template with "Support GCM" already sets defaults. Two sources of defaults gives unpredictable order and values.
- The CMP tag fires on All Pages, so the consent update can arrive after the GA4 and ad tags are ready. The CookieYes tag should be on Consent Initialization. The setup-tag link to GA4 Config does not fix this ordering.
- The hard-coded script sits in the head with no ordering relative to GTM. It can run before or after the defaults.

## What to change

1. **Keep one loader.** Preferred option: remove the hard-coded `<script>` and let the GTM template load CookieYes. Alternative: keep the script and delete the GTM tag. Do not keep both.
2. **Move "CookieYes CMP" to the Consent Initialization - All Pages trigger.** Leave GA4 Config on All Pages, or use Initialization, with the CMP as its setup tag.
3. **Delete the Custom HTML "Default consent" tag.** Use the template's built-in defaults. Set all seven signals to denied, set `wait_for_update` (for example 500 ms), and add regions if needed.
4. **In the CookieYes dashboard, confirm GCM is on and "Google Tag Manager" is not also used as a second integration.**
5. **Check Tag Manager's built-in consent settings.** Set GA4 to require `analytics_storage`, and ad tags to require `ad_storage`, `ad_user_data` and `ad_personalization`.

## What else to check

- **Plugins.** Check the shop platform for a CookieYes plugin or app, or a theme setting that injects it a third time. Also check for a second CMP, such as the platform's own banner.
- **Console error.** Read the full message and stack trace in the console. Note the line in `script.js`. If it is a 404 or CSP block, check the site key and the Content-Security-Policy.
- **Network tab.** Filter for `cdn-cookieyes.com`. You should see exactly one `script.js` request.
- **GTM Preview and Tag Assistant.** Confirm the order: default consent, then CMP, then tags. Confirm a consent update fires after the user chooses.
- **DevTools, Application tab.** Confirm one `cookieyes-consent` cookie. Test in a clean profile.
- **Banner trigger.** Confirm the banner appears once on reload, and that GA4 sends nothing before consent.
- **Staging and production.** Make sure only one container is published and the workspace has no unpublished duplicates.
