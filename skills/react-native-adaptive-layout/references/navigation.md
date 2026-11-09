# Navigation in expo-router across size classes

Verified on device and against installed source (expo-router 57.0.12, react-native-screens) on 18 Sep 2026. Re-check on your versions. The two platforms needed opposite approaches.

## iPadOS: one prop

`<NativeTabs sidebarAdaptable>` sets UIKit's `tabBarControllerMode` to `tabSidebar` and renders a real leading sidebar at regular width (seen at 1376pt landscape). It does nothing on iPhone. Two traps:

- The sidebar is a floating overlay, not a column. It does not narrow the content view, and iOS reports it as a left safe-area inset. A screen that asks `SafeAreaView` for `edges={['top']}` discards that inset and renders under the sidebar. Ask for `'left'` and `'right'` too.
- The selected tab label rendered in the system blue; `labelStyle` did not reach it.

## Android: you render it

In the version checked, react-native-screens' `TabsContainer.kt` built a fixed `BottomNavigationView` and referenced no `NavigationRail`, so native tabs never adapted. Use a platform file (`_layout.android.tsx` resolves over `_layout.tsx` and leaves iOS on its real `UITabBar`) built on the headless `expo-router/ui` `Tabs`.

## Keeping state across the breakpoint

Mount one navigator and make bar-versus-rail a single style property on it:

```tsx
<Tabs style={{ flex: 1, flexDirection: rail ? 'row-reverse' : 'column' }}>
  <TabSlot detachInactiveScreens={false} />
  <TabList style={rail ? railStyle : barStyle}>...</TabList>
</Tabs>
```

`row-reverse` does real work. The rail must sit on the leading edge, but `TabList` is written after `TabSlot`. Reversing the axis puts it first visually while the React tree stays identical on both sides of 600dp. Reordering the JSX instead can make React unmount and remount. A style change cannot remount anything, so a half-written draft surviving a fold is structural (seen: 25-character draft, cursor intact after fold and unfold). `detachInactiveScreens={false}` keeps the other tabs mounted so switching does not lose scroll position.

Width alone gets tabletop posture wrong; see SKILL.md.
