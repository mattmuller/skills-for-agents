Our Expo app (SDK 57) is used on phones but testers say it looks stretched on an iPad and on a foldable whose inner screen is 852dp wide. Review this screen and give me the corrected code plus a list of what you changed and why. Also list anything you would verify on a device.

```tsx
import { Dimensions, View, Text, Pressable, TextInput, FlatList, Image } from 'react-native';
const { width } = Dimensions.get('window');
const isTablet = width > 700;

export default function CatalogScreen({ items, onBuy }) {
  return (
    <View style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 24 }}>Catalog</Text>
      <TextInput placeholder="Search" style={{ height: 44, borderWidth: 1 }} />
      <FlatList
        data={items}
        numColumns={isTablet ? 5 : 3}
        renderItem={({ item }) => (
          <Image source={{ uri: item.thumb }} style={{ width: width / (isTablet ? 5 : 3), height: 100 }} />
        )}
      />
      <Pressable onPress={onBuy} style={{ height: 48, backgroundColor: '#06c' }}>
        <Text style={{ color: '#fff' }}>Buy now</Text>
      </Pressable>
    </View>
  );
}
```
