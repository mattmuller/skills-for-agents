# Plan: rail on wide screens, tabs on phones

## 1. Orientation assumptions

- **iPad:** `"orientation": "portrait"` is ignored for the iPad's purposes only if `UIRequiresFullScreen` is false. With `supportsTablet: true`, Expo's config plugin writes the iPad orientations too, so an iPad can be locked to portrait. iPad multitasking (Split View, Slide Over, Stage Manager) needs all four orientations and no full-screen requirement. Assume tablets will rotate and resize freely. Remove the portrait lock, or set `"orientation": "default"`. Then lock phones to portrait in code with `expo-screen-orientation` if design wants that.
- **Android API 36:** Android 16 ignores orientation, resizability and aspect-ratio restrictions on screens with a smallest width of 600dp or more (large screens, foldables, tablets). The `portrait` lock does nothing there, and apps can no longer opt out. Assume the app is landscape-capable, resizable and multi-window on those devices. The Expo app can't "stay portrait" on an unfolded foldable.
- **Never assume a device class from orientation.** Use window width.

## 2. Navigation switch

- Read the width with `useWindowDimensions()`. Do not use `Dimensions.get`, which doesn't update on fold or resize. Derive a size class: compact is under 600dp, medium and up is 600dp or more.
- Put the breakpoint in one hook (`useWindowSizeClass`). Add hysteresis or a small debounce so a resize drag doesn't flap.
- Keep one set of routes. Change only the navigator chrome. In expo-router, use a custom layout around `Tabs` (or `Slot` and a rail component). Pass `tabBar={...}` to render a rail when wide and the default bar when compact. Alternatively use `tabBarPosition: 'left'` where the React Navigation version supports it.
- The route tree and navigation state must not change with the switch. Then the selected tab and nested stacks survive a fold.
- Cap content width and let lists reflow with columns, so a wide screen is not a stretched phone layout.
- Do not conditionally mount two different navigators. That remounts screens and loses state.

## 3. Risks and checks

| Risk | Check |
|---|---|
| Fold or unfold while typing: the activity is recreated or resized, so the keyboard and focus may drop and typed text can be lost | Type half a form, fold and unfold. Text, cursor and focus must survive. Hold form state in a store or the parent, not in components under the switched chrome. |
| Remount from the switch resets screens and scroll position | Compare screen state before and after the fold. Confirm the layout component identity is stable. |
| Android config changes (`configChanges`) missing, so the activity restarts | Verify `screenSize`, `smallestScreenSize`, `screenLayout` and `orientation` handling in the manifest. Test with "Don't keep activities". |
| Keyboard avoidance and insets differ on the wide layout | Test the keyboard with the rail visible, and in split-screen. |
| iPad Split View or Stage Manager gives a compact-width window on a large device | Test in Slide Over. It must show the bottom bar, since the rule is width, not device. |
| Rail focus order and accessibility | Check TalkBack and VoiceOver order, a hardware keyboard Tab order, and 44px touch targets. |

Devices to test: a foldable emulator (Pixel Fold, resizable emulator), a tablet at 600dp and 840dp, iPad in portrait, landscape and Split View. Check light and dark mode. Run one automated test per size class that asserts rail versus tab bar.
