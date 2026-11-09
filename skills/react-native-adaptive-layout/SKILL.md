---
name: react-native-adaptive-layout
description: Adapt a React Native or Expo app to large screens - tablets, foldables, iPad landscape. Use whenever the task involves React Native layout widths or maxWidth, useWindowDimensions or Dimensions, breakpoints or window size classes, tab bars, navigation rails or sidebars, app.json orientation or supportsTablet, Android screenOrientation or resizeableActivity or configChanges, or whenever a native screen looks stretched, letterboxed or wrong on a tablet or unfolded device. Not for web or CSS responsive work.
allowed-tools: Read, Grep, Glob, Bash
---

# Adaptive layout in React Native

**Principle: do not build a tablet version. Build one layout that stops stretching.** Apple's guidance is to adapt structure to the available space, not to stretch individual elements to fill the screen. Most layouts that look amateurish at width are a phone control that was allowed to grow sideways.

React Native core has no window-size-class API. Flutter and SwiftUI ship helpers for this; in React Native you write the rules yourself.

## Breakpoints

One set that matches Material's window size classes and roughly Apple's size classes. Decide from **width, not device type or orientation**.

| Class | Width | Typical devices | Margins |
|---|---|---|---|
| Compact | `< 600dp` | Phones, folded foldables | 16dp |
| Medium | `600-839dp` | Small tablets, some foldable inner screens | 24dp |
| Expanded | `840-1199dp` | Larger foldable inner screens, tablets, iPad portrait | 24dp |
| Large | `1200-1599dp` | iPad landscape, Chromebooks | 24dp |
| X-Large | `>= 1600dp` | Ultra-wide | 24dp |

Apple's compact/regular maps onto this: compact is Compact, regular is Medium and up.

Measure a device, do not file it by name. A foldable inner screen measured at 852dp is Expanded, not Medium. Put the classifier in a pure function and unit-test the boundaries (599, 600, 839, 840, 1199, 1200).

## What caps and what expands

| Surface | Compact | Medium and above |
|---|---|---|
| Buttons | Full width (correct mobile idiom) | Capped and centred with the content column |
| Form fields | Full width | Capped, aligned with the buttons below |
| Body copy | Full width | Cap to a readable measure |
| Feed or list cards | Full width | Capped column |
| Menus, sheets, dropdowns, pickers | As the platform gives them | Sized to content and anchored; never full-bleed |
| Media, camera, video | Full bleed | Expands; do not cap |
| Image grids | Fixed sensible count | Column count derived from width |

A full-width button is right on a phone and wrong on a tablet. The rule depends on the breakpoint. "Cap everything everywhere" is the opposite failure and wastes the canvas.

## Navigation by size class

| Width | Material (Android) | Apple (iOS/iPadOS) |
|---|---|---|
| Compact | Navigation bar (bottom) | Tab bar |
| Medium and above | Navigation rail on the leading edge, outside any panes | Consider a sidebar instead of a tab bar |

- **Tabletop posture is an exception.** A foldable half-open on a horizontal hinge should show the bar, not the rail, even at large width. A width-only rule puts a rail on a half-folded phone. React Native has no posture API; record it as a known wrong case rather than pretend it is handled.
- **A navigator swapped at a breakpoint is the biggest regression risk.** Folding crosses the breakpoint, and a naive swap unmounts the navigator and destroys in-progress input. Design state preservation in and prove it with a test. See `references/navigation.md` for a pattern that avoids the remount by construction.

## React Native mechanics

- **`useWindowDimensions()`, never `Dimensions.get()`.** The static call does not update on rotation or fold.
- **Cap against the container, not the window.** A modal may already sit inside an inset sheet (iPad does this). Capping against window width then insets it twice into a narrow ribbon.
- **Apply the container at each screen's content root, inside its background**, not on the navigator's `contentStyle`. Capping the screen also caps its background, and a gradient or image grid letterboxed into a centred strip is worse than the stretch it replaces. Include sign-in and onboarding screens: the first screen a user sees is the one nobody remembered to cap.
- **Use `react-native-safe-area-context`** for asymmetric insets. Side-mounted navigation makes horizontal safe area non-symmetric.
- **Use a literal `maxWidth`** only where it does real work, such as centred empty-state or caption text.
- **Inside a rail, measure the content area, not the window.** The window width overstates the content width by the rail. 883dp minus an 80dp rail is 803dp: Medium, not Expanded. Tile size and column count both come out wrong if a grid reads the window.

## The two patterns

**Breakpoint from live dimensions** (reactive, so it survives rotation and fold):

```tsx
import { useWindowDimensions } from 'react-native';

export type Breakpoint = 'compact' | 'medium' | 'expanded' | 'large';

export function breakpointForWidth(width: number): Breakpoint {
  if (width < 600) return 'compact';
  if (width < 840) return 'medium';
  if (width < 1200) return 'expanded';
  return 'large';
}

export function useBreakpoint(): Breakpoint {
  const { width } = useWindowDimensions(); // not Dimensions.get()
  return breakpointForWidth(width);
}
```

**Content container.** Three style properties do the job. In flexbox, `maxWidth` resolves against the parent's available width, so capping against the container holds by construction:

```tsx
import { View } from 'react-native';

export const CONTENT_MAX_WIDTH = 560; // text, forms, buttons
export const CARD_MAX_WIDTH = 640;    // image-plus-caption cards

export function ContentContainer({ variant = 'readable', children }) {
  const maxWidth = variant === 'readable' ? CONTENT_MAX_WIDTH : CARD_MAX_WIDTH;
  return (
    <View style={{ width: '100%', maxWidth, alignSelf: 'center' }}>
      {children}
    </View>
  );
}
```

`width: '100%'` is load-bearing: without it a `maxWidth` box shrink-wraps its content and a short column centres as a narrow strip. Below the cap (every phone) all three properties are inert, so the compact layout cannot regress and needs no branch. For a `ScrollView` or list, spread the same three properties into `contentContainerStyle`.

Do not reach for `onLayout` plus `Math.min`. Flexbox already gives this, and measuring costs a render per instance, a nested `View`, and a first frame at full width that snaps to the cap. Measure only when flexbox cannot express the rule.

A wide-card cap should be a content measure, not a breakpoint. At 852dp an 840 cap leaves 6dp each side, which looks like the bug it fixes. Pin the chosen value with a test so its justification lives in an assertion.

Media, camera and grid surfaces render outside this container; they do not get a variant.

## Device and SDK traps

Observed by the skill's author on an Android foldable emulator (852dp) and an iPad simulator (1032pt), Expo SDK 57 and React Native 0.86, on 18 Sep 2026. Not re-verified since. Check each against your own SDK before relying on it. Details and the evidence are in `references/expo-and-device-traps.md`:

1. Expo prebuild wrote all four iPad orientations into `Info.plist` even with `orientation: "portrait"`. Read the generated plist, not `app.json`.
2. Android with `targetSdkVersion` 36 ignored `android:screenOrientation="portrait"` at 600dp and above.
3. `expo-router` native tabs did not adapt on Android; on iPadOS they became a floating pill unless the sidebar option was set.
4. iPad presented modal routes as inset sheets; Android presented the same route full-screen.
5. An odd grid column count can be right on a phone; an even count only matters at Medium and up.
6. Android fold state survived because `configChanges` listed `screenSize|screenLayout|smallestScreenSize`. Guard that line with a regression check.

## Review checklist

- At about 850dp and 1030pt, does anything interactive look like a phone control pulled sideways?
- Buttons and fields capped above 600dp, full width below?
- Menus, sheets and pickers sized to content?
- Media and camera surfaces still expanding?
- Caps measured against the container, not the window?
- Sign-in and onboarding screens covered, not only the main tabs?
- `useWindowDimensions`, not `Dimensions.get()`?
- Even-column rule confined to Medium and above?
- Navigation: rail or sidebar above 600dp, bar in tabletop posture?
- In-progress input survives fold and unfold, tested rather than assumed?
- Generated native config (`Info.plist`, `AndroidManifest.xml`) checked, not only `app.json`?

## Sources

- Material Design 3: window size classes, navigation rail guidelines
- Android Developers: build adaptive navigation
- Apple Human Interface Guidelines: layout
