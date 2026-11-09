rn-a items (1 point each):
1 Replaces Dimensions.get with useWindowDimensions (reactive)
2 Decides from width/breakpoint (e.g. 600/840), not an "isTablet" flag/device type
3 Caps content (buttons/fields/text) with maxWidth + centring (alignSelf center) so phone stays full width
4 Uses width:'100%' with maxWidth (or equivalent) / caps against container not window
5 Image grid column count derived from width; does not widen thumbnails by window width; 3 columns on phone kept
6 Does not use onLayout+Math.min as the main approach
7 Says media/image surfaces may expand while buttons/forms cap (breakpoint-dependent rule)
8 Device verification list includes checking generated native config (Info.plist / manifest) or fold/rotation re-render
