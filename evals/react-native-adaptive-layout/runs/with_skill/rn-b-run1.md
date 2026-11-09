# Plan: rail on wide screens, bar on phones

Principle: build one layout that adapts to width, not a tablet version. Decide from measured width, never from device name or orientation.

## 1. Orientation: assume nothing is locked

- **iPad:** `supportsTablet: true` means full screen, and prebuild has written all four iPad orientations into `Info.plist` despite `"orientation": "portrait"`. Assume landscape is reachable. Read the generated `Info.plist`, not `app.json`.
- **Android:** at `targetSdkVersion` 36, `android:screenOrientation="portrait"` was ignored at 600dp and above, so the app rotates on tablets and unfolded foldables. Android documents an opt-out, but it goes away at the next API level. Check the current behaviour-changes page.
- Design for both orientations at every size. Do not rely on the portrait lock for anything.

## 2. The navigation switch

- Classify with a pure function over `useWindowDimensions().width` (never `Dimensions.get()`, which does not update on fold). Compact is below 600dp. Medium and above (600dp+) gets the rail. Unit-test 599, 600, 839, 840, 1199 and 1200.
- **iOS:** use `NativeTabs` with `sidebarAdaptable`. It gives a real sidebar at regular width and does nothing on iPhone. The sidebar floats and counts as a left safe-area inset, so screens must request `left` and `right` edges too.
- **Android:** native tabs do not adapt (fixed bottom bar). Use `_layout.android.tsx` on the headless `expo-router/ui` `Tabs`.
- **State preservation:** mount ONE navigator and flip bar versus rail with a style only: `flexDirection: rail ? 'row-reverse' : 'column'` (row-reverse puts the list first visually, so the React tree stays identical). Set `detachInactiveScreens={false}`. Do not swap navigators or reorder the JSX at the breakpoint, because that remounts and wipes form input.
- Inside the rail, size content from the container width, not the window. 883dp minus an 80dp rail is 803dp, which is Medium.

## 3. Risks and checks

| Risk | Check |
|---|---|
| Fold or unfold remounts the navigator and loses a half-typed form | Type into a field, fold, unfold, and confirm text and cursor survive. Automate it. |
| Android activity recreated on fold | Confirm `configChanges` keeps `screenSize\|screenLayout\|smallestScreenSize`. Add a regression guard. |
| Tabletop posture (half-folded on a horizontal hinge) gets a rail | Width-only logic gets this wrong and RN has no posture API. Record it as a known wrong case. |
| Keyboard open at the breakpoint | Repeat the test with the keyboard up. |
| iOS content under the floating sidebar | Test iPad landscape at about 1030pt. Safe-area `left` and `right` are set. |
| Content stretched wide | Cap content, forms and buttons (for example 560dp) at the screen's content root, not on navigator `contentStyle`. Include sign-in. Leave media full bleed. |
| Modals | iPad shows inset sheets, Android shows full screen. Cap against the container, not the window. |
| Generated config differs from `app.json` | Inspect the prebuilt `Info.plist` and `AndroidManifest.xml`. |

Verify on an Android foldable emulator (about 852dp) and an iPad simulator (about 1032pt). Re-check these behaviours on your own Expo SDK 57 and expo-router versions, because the findings above came from earlier versions.
