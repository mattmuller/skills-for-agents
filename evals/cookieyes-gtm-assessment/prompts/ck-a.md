Our shop shows two cookie banners and the browser console shows an error from a CookieYes script file. We use Google Tag Manager and CookieYes with Consent Mode v2. Diagnose likely causes from what is below and say what to change and what else to check.

app layout (site code):
```html
<head>
  <script id="cookieyes" src="https://cdn-cookieyes.com/client_data/<KEY>/script.js"></script>
  <!-- GTM snippet for GTM-ABC1234 loaded here by the framework component -->
</head>
```
GTM container tag list:
- "CookieYes CMP" (CookieYes template, Support GCM on) - trigger: All Pages
- "Default consent" (Custom HTML: gtag('consent','default',{ad_storage:'denied',analytics_storage:'denied'})) - trigger: Consent Initialization - All Pages
- "GA4 Config" - trigger: All Pages - setup tag: "CookieYes CMP"
