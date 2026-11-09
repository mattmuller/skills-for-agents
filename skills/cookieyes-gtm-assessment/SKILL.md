---
name: cookieyes-gtm-assessment
description: Diagnose a CookieYes consent banner loaded through Google Tag Manager with Google Consent Mode v2. Use when a consent banner shows twice, does not show, does not remember the choice, when script errors name a CookieYes file, when tags fire before consent, when Consent Mode signals look wrong in Tag Assistant or the data layer, or when someone asks whether a site's CookieYes and GTM setup is correct.
allowed-tools: Read, Grep, Glob, Bash
---

# CookieYes with GTM: assessment

Work through the checks in order. Each one finds a cause that produces the symptoms above. Report what you found at each step, including steps that were clean.

## What you need first

Ask for, or find, these. Do not guess them.

- The GTM container ID (format `GTM-XXXXXXX`) and how GTM is installed in the site (a snippet, a framework component, a plugin).
- A way to read the container: the GTM UI export (JSON), the GTM API, or screenshots of the tag list. If you have none, say so and limit the assessment to the site code.
- The CookieYes website key from the CookieYes dashboard.

## 1. One consent manager, loaded one way

CookieYes can be loaded through a GTM tag or by pasting its script into the page. Doing both is the most common cause of double banners, errors and lost choices.

Search the site code for hard-coded loads:

```sh
grep -rniE "cookieyes|cdn-cookieyes" --include="*.{html,js,jsx,ts,tsx,php,liquid,hbs}" . 2>/dev/null | grep -v node_modules
grep -rn "<website-key>" . | grep -v node_modules     # the CookieYes website key
```

If GTM is the chosen route, the site code should contain no CookieYes script tag. Also check for a second consent platform (another CMP tag or plugin). Only one may be active.

## 2. The GTM tag

In the container, check the CookieYes tag:

- It uses the CookieYes template, with the website key matching the dashboard.
- Its trigger is **Consent Initialization - All Pages**, not All Pages or Page View. Consent defaults must be set before any other tag evaluates.
- Google Consent Mode support is enabled in the template settings.
- No other tag also sets a default consent state. A second "default consent" tag overrides or races the first. Check the tag list for anything that calls `gtag('consent', 'default', ...)`, including custom HTML tags.
- No tag uses the CookieYes tag as a setup tag. That ties other tags to it in a way that can reorder firing.

## 3. Consent Mode v2 signals

Google Consent Mode v2 has seven consent types: `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`, `functionality_storage`, `personalization_storage`, `security_storage`. Version 2 added `ad_user_data` and `ad_personalization`.

Verify in the browser (Tag Assistant, or the `dataLayer` in the console):

- The default state is `denied` for the types that need consent, set before the first Google tag fires.
- After accepting, an update event moves the right types to `granted`.
- After rejecting, they stay `denied`.
- Which CookieYes category controls which type is set in CookieYes and in the template. Read the mapping from the dashboard or template; do not assume it.

## 4. Content Security Policy

If the site sends a CSP header, the CookieYes script and its requests must be allowed, or the banner fails or does not persist. Read the policy in the response headers and check `script-src` and `connect-src` for the CookieYes CDN and logging domains shown in the Network tab. Copy domains from what the browser actually requests, not from memory.

## 5. Symptom table

| Symptom | Check first |
|---|---|
| Two banners | A hard-coded script plus the GTM tag, or two CMPs |
| Script error naming a CookieYes file | Script loaded twice, loaded before the DOM is ready, or blocked by CSP |
| Choice not remembered | CSP or an ad blocker blocking the request, cookie domain mismatch, or the banner re-initialised on each page |
| No banner | Wrong trigger, wrong website key, GTM not on the page, banner hidden by CSS or CSP |
| Tags fire before consent | Consent defaults set after the first tag, or the tag trigger set to All Pages |

## 6. Test in a clean state

Open a private window with extensions off, load the site, and read the consent signals before touching the banner. Then accept, check the update, reload, and confirm the choice persists.

## Report

List per step: what was checked, what was found, and the fix. Name anything you could not check (for example, no container access) rather than marking it clean.
