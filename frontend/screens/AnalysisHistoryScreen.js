import React, { useEffect, useState } from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import Markdown from "react-native-markdown-display";

export default function AnalysisHistoryScreen() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const keys = await AsyncStorage.getAllKeys();
        const filtered = keys.filter((k) => k.startsWith("advisor_history_"));
        const all = await Promise.all(
          filtered.map((key) => AsyncStorage.getItem(key))
        );
        const parsed = all
          .map((json) => {
            try {
              return JSON.parse(json);
            } catch {
              return [];
            }
          })
          .flat()
          .filter((m) => m.mode === "pro" && m.sender === "bot");

        setHistory(parsed.reverse());
      } catch (err) {
        console.warn("❌ Error cargando historial de análisis:", err);
      }
    };

    load();
  }, []);

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <Text style={styles.timestamp}>
        {new Date(item.timestamp).toLocaleString()}
      </Text>
      <Markdown>{item.text}</Markdown>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={history}
        keyExtractor={(_, index) => index.toString()}
        renderItem={renderItem}
        contentContainerStyle={{ paddingBottom: 30 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fdfdfd",
    padding: 16,
  },
  card: {
    backgroundColor: "#fffef5",
    padding: 14,
    marginBottom: 12,
    borderRadius: 10,
    borderColor: "#eee",
    borderWidth: 1,
  },
  timestamp: {
    fontSize: 12,
    color: "#666",
    marginBottom: 6,
  },
});
