ck-a items:
1 Flags the hard-coded CookieYes script plus GTM tag as duplicate load -> double banner/error; remove one (GTM route: remove script tag)
2 Says CookieYes tag trigger must be Consent Initialization - All Pages, not All Pages
3 Flags the custom "Default consent" tag as conflicting second default consent source; remove/consolidate
4 Flags the GA4 tag's setup-tag dependency on the CMP tag
5 Notes Default consent lacks Consent Mode v2 types ad_user_data/ad_personalization (or similar v2 mention)
6 Suggests checks: CSP, second CMP/plugin, clean private-window test, read container if not provided
7 Does not invent specific CookieYes template IDs/IDs/claims it cannot know (no fabricated facts)
