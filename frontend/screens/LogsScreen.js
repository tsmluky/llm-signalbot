import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_SIGNALS } from "../constants";
import SignalItem from "../components/SignalItem";

export default function LogsScreen() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCharts, setShowCharts] = useState(true);

  const fetchSignals = async () => {
    try {
      const res = await fetch(API_SIGNALS);
      const data = await res.json();
      if (data.status === "ok" && Array.isArray(data.signals)) {
        setSignals(data.signals);
      } else {
        console.warn("No se encontraron señales.");
      }
    } catch (err) {
      console.error("❌ Error al cargar señales:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchChartPreference = async () => {
    const value = await AsyncStorage.getItem("show_charts");
    if (value !== null) setShowCharts(value === "true");
  };

  useEffect(() => {
    fetchSignals();
    fetchChartPreference();
  }, []);

  const renderItem = ({ item }) => (
    <SignalItem item={item} showCharts={showCharts} />
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>📜 Historial de Señales LITE</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#007aff" />
      ) : (
        <FlatList
          data={signals}
          keyExtractor={(_, index) => index.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 30 }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f9f9f9",
    padding: 16,
  },
  header: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
    textAlign: "center",
  },
});
