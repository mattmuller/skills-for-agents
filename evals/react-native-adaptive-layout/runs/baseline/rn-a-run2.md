## Corrected code

```tsx
import { useWindowDimensions, View, Text, Pressable, TextInput, FlatList, Image } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const MAX_CONTENT_WIDTH = 720; // readable cap for text, search and button
const MIN_TILE = 110;          // minimum thumbnail width
const GAP = 8;
const PAD = 16;

export default function CatalogScreen({ items, onBuy }) {
  const { width } = useWindowDimensions();            // live: rotation, fold, split view
  const insets = useSafeAreaInsets();
  const contentWidth = Math.min(width - PAD * 2, MAX_CONTENT_WIDTH * 1.6);
  const columns = Math.max(2, Math.floor((contentWidth + GAP) / (MIN_TILE + GAP)));
  const tile = (contentWidth - GAP * (columns - 1)) / columns;

  return (
    <View style={{ flex: 1, alignItems: 'center', paddingHorizontal: PAD,
                   paddingTop: insets.top, paddingBottom: insets.bottom + PAD }}>
      <View style={{ flex: 1, width: '100%', maxWidth: MAX_CONTENT_WIDTH * 1.6 }}>
        <Text accessibilityRole="header" style={{ fontSize: 24 }}>Catalog</Text>
        <View style={{ maxWidth: MAX_CONTENT_WIDTH }}>
          <TextInput placeholder="Search" accessibilityLabel="Search catalog"
            style={{ height: 44, borderWidth: 1, paddingHorizontal: 12 }} />
        </View>
        <FlatList
          key={columns}                                 // required when numColumns changes
          data={items}
          numColumns={columns}
          keyExtractor={(item) => String(item.id)}
          columnWrapperStyle={columns > 1 ? { gap: GAP } : undefined}
          contentContainerStyle={{ gap: GAP, paddingVertical: GAP }}
          renderItem={({ item }) => (
            <Image source={{ uri: item.thumb }} resizeMode="cover"
              style={{ width: tile, height: tile * 0.9 }} accessibilityIgnoresInvertColors />
          )}
        />
        <Pressable onPress={onBuy} accessibilityRole="button"
          style={{ height: 48, alignSelf: 'center', width: '100%', maxWidth: 400,
                   justifyContent: 'center', alignItems: 'center', backgroundColor: '#06c' }}>
          <Text style={{ color: '#fff' }}>Buy now</Text>
        </Pressable>
      </View>
    </View>
  );
}
```

## What changed and why

1. **`Dimensions.get` at module scope became `useWindowDimensions`.** The module-level value is read once and never updates on rotation, folding or unfolding, iPad split view or Stage Manager. A foldable that starts folded would stay "phone" forever.
2. **The `width > 700` boolean became a computed column count.** A fixed 5 columns at 852dp gives about 160dp tiles of 100dp height, which is the stretch testers see. Columns now derive from a minimum tile width, so any width works.
3. **Tile width ignored padding and gaps.** `width / n` overflowed the 16dp padding. It is now computed from the real content width.
4. **`key={columns}` on the FlatList.** React Native throws if `numColumns` changes without a new key.
5. **Content is capped and centred.** Search and the Buy button no longer span 800dp or more. Max widths keep them readable.
6. **Safe-area insets added**, so the title and button are not under the notch, home indicator or fold hinge area.
7. **Smaller fixes.** I added `keyExtractor`, `resizeMode`, accessibility roles and labels, centred button text, and input padding.

## Also check in app config (not visible in this file)

- `app.json`: `ios.supportsTablet: true`. An `orientation` of `portrait` locks the app, so use `default`. iPad multitasking needs all orientations unless `requireFullScreen` is set.
- Android: `resizeableActivity` must not be false, and rotation or fold changes must not restart the activity (`configChanges`, or accept the restart and test state).

## Verify on a device

- iPad: portrait, landscape, Split View at 1/3 and 1/2, Slide Over, Stage Manager resize.
- Foldable: fold and unfold mid-scroll. Check that scroll position, search text and the column count survive and update.
- Inner screen at 852dp: tile size, column count and that the button is not full width.
- Small phone and large font scale (200%): the Buy label fits and the tap targets stay at least 44 to 48dp.
- Dark mode and RTL, in case thumbnails or text rely on direction.
- Image performance with many items at 6 or more columns. Consider `expo-image` and a smaller thumbnail size.
- Hardware keyboard focus order on iPad, and the on-screen keyboard not covering the Buy button.
- Tablet landscape: would a two-pane layout fit better than a wider grid? That is a product decision.
