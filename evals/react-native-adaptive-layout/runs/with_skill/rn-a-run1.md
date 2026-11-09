# CatalogScreen: one layout that stops stretching

Not run on a device.

```tsx
import { useWindowDimensions, View, Text, Pressable, TextInput, FlatList, Image } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export function breakpointForWidth(w: number) {
  if (w < 600) return 'compact';
  if (w < 840) return 'medium';
  if (w < 1200) return 'expanded';
  return 'large';
}
const COLUMNS = { compact: 3, medium: 4, expanded: 6, large: 8 }; // even at medium+
const col = { width: '100%', maxWidth: 560, alignSelf: 'center' } as const;

export default function CatalogScreen({ items, onBuy }) {
  const { width } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const bp = breakpointForWidth(width);
  const margin = bp === 'compact' ? 16 : 24;
  const columns = COLUMNS[bp];
  const left = margin + insets.left, right = margin + insets.right;
  const tile = Math.floor((width - left - right) / columns);

  return (
    <View style={{ flex: 1, paddingLeft: left, paddingRight: right }}>
      <View style={col}>
        <Text style={{ fontSize: 24 }}>Catalog</Text>
        <TextInput placeholder="Search" style={{ height: 44, borderWidth: 1 }} />
      </View>
      <FlatList
        key={columns}
        data={items}
        numColumns={columns}
        keyExtractor={(i) => String(i.id)}
        renderItem={({ item }) => (
          <Image source={{ uri: item.thumb }} style={{ width: tile, height: 100 }} />
        )}
      />
      <View style={col}>
        <Pressable onPress={onBuy} style={{ height: 48, backgroundColor: '#06c' }}>
          <Text style={{ color: '#fff' }}>Buy now</Text>
        </Pressable>
      </View>
    </View>
  );
}
```

## What changed and why

1. `Dimensions.get` became `useWindowDimensions`. The static value misses rotation, split view and fold.
2. `width > 700` became width classes (600/840/1200). The 852dp inner screen is Expanded. Unit-test the boundaries.
3. Columns come from the class. Phones keep 3. Medium and up use even counts.
4. Tile width subtracts margins and side insets. The old `width / n` ignored the 16dp padding, so tiles overflowed.
5. Search and Buy are capped at 560 and centred. `width: '100%'` is needed or the box shrinks. Phones are unaffected. The grid is not capped.
6. Margins are 16 at Compact, 24 above, plus side safe-area insets.
7. `key={columns}` avoids the "cannot change numColumns" error at a breakpoint. I added `keyExtractor`.

## Verify on a device

- Foldable at 852dp and iPad at 1032pt, portrait and landscape.
- Fold and unfold with text in Search. It must survive. On Android confirm `configChanges` keeps `screenSize|screenLayout|smallestScreenSize`.
- Generated `Info.plist` and `AndroidManifest.xml`, not only `app.json`. iPad may allow all orientations. Android 16 may ignore a portrait lock at 600dp and above.
- Side insets in landscape.
- If a rail or sidebar is added, tile size must use the content width, not the window.
- A last row that is not full.
- If shown as a modal, the iPad inset sheet against Android full-screen. Check for a double inset.
