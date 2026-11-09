# CatalogScreen: one layout that stops stretching

Root causes: `Dimensions.get` runs once at import, so it never updates on rotation, fold or split-screen. The `isTablet` flag guesses from one width. The 852dp inner screen is Expanded (840-1199), not "tablet vs phone". The tile width ignores the 16dp padding. The search field and Buy button grow to full width, which is a phone control pulled sideways.

```tsx
import { useWindowDimensions, View, Text, Pressable, TextInput, FlatList, Image } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export type Breakpoint = 'compact' | 'medium' | 'expanded' | 'large';
export const breakpointForWidth = (w: number): Breakpoint =>
  w < 600 ? 'compact' : w < 840 ? 'medium' : w < 1200 ? 'expanded' : 'large';

const CONTENT_MAX_WIDTH = 560;

export function columnsFor(contentWidth: number, bp: Breakpoint) {
  if (bp === 'compact') return 3;
  const n = Math.floor(contentWidth / 180);
  return Math.max(4, n - (n % 2)); // even count, Medium and up only
}

export default function CatalogScreen({ items, onBuy }) {
  const { width } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const bp = breakpointForWidth(width);
  const margin = bp === 'compact' ? 16 : 24;
  const contentWidth = width - insets.left - insets.right - margin * 2;
  const cols = columnsFor(contentWidth, bp);
  const tile = Math.floor(contentWidth / cols);
  const column = { width: '100%', maxWidth: CONTENT_MAX_WIDTH, alignSelf: 'center' } as const;

  return (
    <View style={{ flex: 1, paddingHorizontal: margin + 0, paddingLeft: insets.left + margin,
                   paddingRight: insets.right + margin, paddingTop: 16 }}>
      <View style={column}>
        <Text accessibilityRole="header" style={{ fontSize: 24 }}>Catalog</Text>
        <TextInput placeholder="Search" style={{ height: 44, borderWidth: 1 }} />
      </View>
      <FlatList
        key={cols}                       // numColumns cannot change on a live list
        data={items}
        numColumns={cols}
        renderItem={({ item }) => (
          <Image source={{ uri: item.thumb }} style={{ width: tile, height: 100 }} />
        )}
      />
      <View style={[column, { paddingBottom: insets.bottom + 8 }]}>
        <Pressable accessibilityRole="button" onPress={onBuy}
          style={{ height: 48, backgroundColor: '#06c', justifyContent: 'center', alignItems: 'center' }}>
          <Text style={{ color: '#fff' }}>Buy now</Text>
        </Pressable>
      </View>
    </View>
  );
}
```

## What changed and why
1. `Dimensions.get` became `useWindowDimensions`, so rotation and fold re-render.
2. Breakpoint comes from width through a pure function, not an `isTablet` guess. Unit-test 599/600/839/840/1199/1200.
3. Title, search and button sit in a capped column (`width:'100%'`, `maxWidth`, `alignSelf:'center'`). The cap is inert on phones, so compact cannot regress. Buttons and fields are capped above 600dp, full width below.
4. The image grid is not capped. Column count is derived from content width, minus padding and insets. It was hardcoded 5, which gave about 170dp tiles that ignored padding.
5. Even column count applies only at Medium and up. Three stays on phones.
6. `key={cols}` is needed because `numColumns` cannot change on a mounted FlatList.
7. Margins are 16 on compact and 24 above. Safe-area insets replace the bare padding, since side-mounted UI makes them asymmetric.
8. Added button centring and accessibility roles.

## Verify on a device
- Fold and unfold with text typed in the search box: input must survive, and the grid must re-column.
- iPad: read the generated `Info.plist` (all four orientations may be written despite `orientation: "portrait"`). Check `supportsTablet`.
- Android: `targetSdkVersion` 36 may ignore `screenOrientation` at 600dp and above. Confirm `configChanges` still lists `screenSize|screenLayout|smallestScreenSize`, or fold state is lost.
- iPad split view and Slide Over, and 852dp versus 1032pt portrait and landscape: tile size, no letterboxing.
- If a rail or sidebar is added later, measure content width, not window width.
- Tabletop posture (half-folded) is not detectable in React Native; note it as a known wrong case.
- Landscape with notch or side insets: nothing clipped.
