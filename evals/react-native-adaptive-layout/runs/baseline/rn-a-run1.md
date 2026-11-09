# CatalogScreen: large-screen fixes

## Root causes
1. `Dimensions.get('window')` runs once at module load. It never updates on rotation, split view or fold/unfold.
2. `width > 700` guesses a device class. The 852dp inner screen counts as "tablet" and gets 5 columns, yet nothing caps content width, so search and Buy stretch edge to edge.
3. Tile width `width / cols` ignores the 16dp padding, so tiles overflow.
4. Changing `numColumns` on a mounted FlatList needs a new `key`.

## Corrected code
```tsx
import { View, Text, Pressable, TextInput, FlatList, Image, useWindowDimensions } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const PAD = 16, GAP = 8, MAX_CONTENT = 840, MIN_TILE = 120;

export default function CatalogScreen({ items, onBuy }) {
  const { width: winW } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const contentW = Math.min(winW, MAX_CONTENT);
  const inner = contentW - PAD * 2;
  const cols = Math.max(2, Math.floor((inner + GAP) / (MIN_TILE + GAP)));
  const tile = (inner - GAP * (cols - 1)) / cols;

  return (
    <View style={{ flex: 1, alignItems: 'center' }}>
      <View style={{ flex: 1, width: contentW, paddingHorizontal: PAD, paddingTop: insets.top + PAD }}>
        <Text accessibilityRole="header" style={{ fontSize: 24 }}>Catalog</Text>
        <TextInput accessibilityLabel="Search catalog" placeholder="Search"
          style={{ height: 44, borderWidth: 1, borderRadius: 8, paddingHorizontal: 12 }} />
        <FlatList
          key={cols}
          data={items}
          numColumns={cols}
          keyExtractor={(i) => String(i.id)}
          columnWrapperStyle={{ gap: GAP }}
          contentContainerStyle={{ gap: GAP, paddingVertical: GAP }}
          renderItem={({ item }) => (
            <Image source={{ uri: item.thumb }} accessibilityLabel={item.name}
              style={{ width: tile, aspectRatio: 1, borderRadius: 8 }} />
          )}
        />
        <Pressable onPress={onBuy} accessibilityRole="button"
          style={{ minHeight: 48, justifyContent: 'center', alignItems: 'center', borderRadius: 8,
                   backgroundColor: '#06c', marginBottom: insets.bottom + PAD }}>
          <Text style={{ color: '#fff' }}>Buy now</Text>
        </Pressable>
      </View>
    </View>
  );
}
```
`cols` is at least 2 because `columnWrapperStyle` throws with one column.

## What changed and why
- `useWindowDimensions` follows the real window.
- Columns come from available width and a minimum tile size, not a device flag.
- Content is centred with a max width.
- Tile maths subtracts padding and gaps; `aspectRatio` replaces fixed height.
- `key={cols}` remounts on column change.
- Safe-area insets, accessibility roles/labels, `keyExtractor`, 48dp button.

## Config outside this file
- `app.json`: `orientation: "default"` (not portrait), `ios.supportsTablet: true`.
- Android: no locked `screenOrientation`; keep `resizeableActivity` true or the app letterboxes.

## Verify on a device
- Fold and unfold mid-session: layout reflows, scroll position and search text survive.
- iPad: both orientations, split view, Stage Manager resizing.
- Foldable: outer screen, 852dp inner, tabletop posture, resized split window.
- Is the column count right at 852dp? Tune `MIN_TILE` and `MAX_CONTENT`.
- Keyboard open: Buy button not covered.
- Cutouts, hinge area, home indicator.
- Large font scale; VoiceOver/TalkBack on button and images.
- Scroll performance with many thumbnails.
