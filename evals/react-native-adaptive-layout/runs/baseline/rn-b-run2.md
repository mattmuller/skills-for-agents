# Plan: rail on wide screens, tabs on phones

## 1. Orientation: assume it is not locked on large screens
- **Android (target API 36):** Android 16 ignores `orientation` and resizability restrictions on displays with smallest width of 600dp or more. `"orientation": "portrait"` will not hold on tablets, on an unfolded foldable, or in a freeform window. The app must handle landscape, any window size, and live size changes.
- **iOS:** `supportsTablet: true` makes the app a native iPad app. Apple expects all orientations on iPad, and resizable windows on recent iPadOS. A portrait-only iPad app is letterboxed or rejected for multitasking. Either set iPad orientations to all (`ios.infoPlist` `UISupportedInterfaceOrientations~ipad`) or accept the loss of Split View.
- Decision: change `orientation` to `"default"`. If phones must stay portrait, lock only on compact width at runtime with `expo-screen-orientation`. Treat that lock as a phone-only preference, never as a layout assumption.
- Keep Android `resizeableActivity` true. Confirm the manifest's `configChanges` covers `screenSize|smallestScreenSize|screenLayout|orientation|density`, so a fold does not recreate the activity and wipe form state.

## 2. Navigation switch
- Decide from **window width**, not device type, orientation or `Platform`. Use `useWindowDimensions()`, which updates on fold, split-screen and resize. Do not use `Dimensions.get('screen')` or a value read once.
- Breakpoint: 600dp (compact below, rail at 600 and above). Consider 840dp for a wider rail with labels.
- Use **one** tab navigator. Switch only its presentation: React Navigation 7 bottom tabs accept `tabBarPosition: 'left' | 'bottom'`. Alternatively supply a custom `tabBar` that renders a rail or a bar from the same state.
- Never render two different navigators or layouts conditionally. That remounts the tree, resets stack state and destroys typed input.
- Cap content width on wide windows (`maxWidth`) and use safe-area insets for the rail.

## 3. Risks
1. Fold or unfold while a form is open: remount loses text. Keep screens mounted and keep form state outside the layout switch, for example in a form library or store.
2. Keyboard up during a resize: the layout may jump, the focused field may be hidden, and the keyboard may drop. The rail also costs width when the keyboard is open in landscape.
3. Stale dimensions after fold on some Android versions: check insets and window size settle.
4. Flicker at the breakpoint when width hovers near 600 (split-screen drag): consider a small hysteresis.
5. iOS iPad resizable windows and Stage Manager: same code path, but untested by default.
6. Hidden portrait assumptions: fixed widths, full-width images, modals and sheets that look stretched.
7. Deep-link or back stack behaves differently if the tab order changes between bar and rail.

## 4. Checks
- Android: resizable emulator and a Pixel Fold or Tablet AVD with fold and unfold; split-screen and freeform; rotate on tablet.
- Type into a form, with the keyboard open, then fold and unfold. Text, focus, scroll and the selected tab must survive.
- Assert tab state and screen mount count do not reset (a test or a logged mount counter).
- iPad: Split View, Slide Over, Stage Manager resize, both orientations.
- Phone: confirm a portrait lock still works and the bar is shown.
- Test accessibility: focus order and labels in both the rail and the bar, plus font scaling.
