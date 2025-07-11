import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

const tokens = ['BTC', 'ETH', 'SOL', 'MATIC'];

export default function HomeScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Elige un token para analizar</Text>
      {tokens.map((token) => (
        <Button
          key={token}
          title={token}
          onPress={() => navigation.navigate('Chat', { token })}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  title: { fontSize: 20, marginBottom: 20 },
});
