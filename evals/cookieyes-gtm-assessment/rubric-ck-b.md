ck-b items:
1 Identifies consent default fires AFTER GA4 config (wrong order)
2 Fix: consent default must be set first, via Consent Initialization trigger / before any tag
3 GA4 tag should be gated/fires after consent state exists (consent checks / default denied before it)
4 Notes missing ad_user_data and ad_personalization (Consent Mode v2)
5 Mentions wait_for_update is fine/relevant, and expected correct sequence (default denied -> tags -> update after accept)
6 Suggests verifying in Tag Assistant/dataLayer in a clean window after the change
7 Mentions checking for a second default-consent source or hard-coded CMP (duplicate) as a possible cause
