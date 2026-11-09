# Plan: rail on wide screens, tab bar on phones

## 1. Orientation: assume nothing is locked on tablets

- **iPad:** `"orientation": "portrait"` with `supportsTablet: true` does not hold. Prebuild can write all four orientations into `UISupportedInterfaceOrientations~ipad`, so iPad landscape is reachable. Read the generated `Info.plist`, not `app.json`.
- **Android API 36:** at 600dp and above, `android:screenOrientation="portrait"` is ignored. Android documents this as a large-screen restriction that is ignored from Android 16, with an opt-out that expires at the next API level. Check the current behaviour-changes page for your target.
- **Plan for it:** treat landscape and resizable windows as normal on tablets and unfolded foldables. Decide from width, never from device type or orientation. Check both platforms' generated native config, because these are observed traps and may differ on your SDK.

## 2. The navigation switch

- Use `useWindowDimensions()`, never `Dimensions.get()`, because the static call does not update on fold or rotation.
- Put the classifier in a pure, unit-tested function: compact below 600dp, medium 600-839, expanded 840-1199, large 1200 and up. Test 599, 600, 839, 840, 1199 and 1200.
- Compact gets the bottom bar. Medium and up gets a leading-edge rail.
- **iOS:** `NativeTabs` with `sidebarAdaptable` gives a real sidebar at regular width, and does nothing on iPhone.
  - The sidebar floats as an overlay and is reported as a left safe-area inset. Ask `SafeAreaView` for left and right edges too.
  - Without `sidebarAdaptable`, tabs became a floating pill.
- **Android:** native tabs did not adapt. Render the rail yourself in `_layout.android.tsx`, using the headless `expo-router/ui` `Tabs`.
- **Mount one navigator, never swap at the breakpoint.** A swap unmounts the navigator and destroys in-progress form input. Make bar-versus-rail one style property:
  - `flexDirection` is `row-reverse` for the rail and `column` for the bar.
  - Keep the same React tree on both sides of 600dp, and do not reorder the JSX.
  - Set `detachInactiveScreens={false}` so other tabs keep scroll position.
- Cap content against the container, not the window, and apply the cap at each screen's content root inside its background. Inside the rail, measure the content area (window width minus the rail).

## 3. Risks and checks

| Risk | Check |
|---|---|
| Typing in a form during fold or unfold loses input | Type a draft, fold and unfold on a foldable emulator, and confirm text and cursor survive. Do this on both platforms and automate it if you can. |
| Android recreates the activity on fold | Confirm `configChanges` includes `screenSize\|screenLayout\|smallestScreenSize`. Add a regression guard next to it, because a silent break is easy. |
| Tabletop posture (half-open on a horizontal hinge) gets a rail from a width-only rule | React Native has no posture API. Record this as a known wrong case. |
| Orientation assumptions | Inspect `Info.plist` and `AndroidManifest.xml`, and run on a tablet in landscape on both platforms. |
| iOS content under the sidebar | Test with left and right safe-area edges at about 1030pt. |
| Modals differ: iPad shows an inset sheet, Android shows full screen | Cap against the container, or you will inset a narrow ribbon twice. |
| Sign-in and onboarding forgotten | Include them in the layout pass. |

Run a manual pass at about 850dp (foldable inner screen) and 1030pt (iPad). Confirm buttons and fields are capped above 600dp, media still expands, and a phone is unchanged. Re-verify every trap on your own SDK 57 build before relying on it.
