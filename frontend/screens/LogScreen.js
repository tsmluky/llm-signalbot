import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from "react-native";

const API_URL = "http://localhost:8000/signals_lite"; // ⚠️ Cambiar IP real en móvil

export default function LogsScreen() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSignals = async () => {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setSignals(data.reverse()); // orden descendente
    } catch (err) {
      console.error("Error al cargar señales:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  const renderItem = ({ item }) => {
    const actionColor =
      item.action === "LONG"
        ? "#a5d6a7"
        : item.action === "SHORT"
        ? "#ef9a9a"
        : "#e0e0e0";

    return (
      <View style={[styles.card, { backgroundColor: actionColor }]}>
        <Text style={styles.token}>{item.token} @ ${item.price_at_analysis}</Text>
        <Text style={styles.action}>🎯 Acción: {item.action}</Text>
        <Text>TP: {item.take_profit} | SL: {item.stop_loss}</Text>
        <Text>Confianza: {item.confidence}% | Riesgo: {item.risk}/10</Text>
        <Text style={styles.timestamp}>{new Date(item.timestamp).toLocaleString()}</Text>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>📜 Historial de Señales Lite</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#007aff" />
      ) : (
        <FlatList
          data={signals}
          keyExtractor={(_, index) => index.toString()}
          renderItem={renderItem}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fdfdfd", padding: 16 },
  header: { fontSize: 20, fontWeight: "bold", marginBottom: 12 },
  card: {
    padding: 12,
    marginBottom: 10,
    borderRadius: 10,
    elevation: 2,
  },
  token: {
    fontWeight: "bold",
    fontSize: 16,
    marginBottom: 4,
  },
  action: {
    fontSize: 15,
    fontWeight: "600",
    marginBottom: 2,
  },
  timestamp: {
    marginTop: 6,
    fontSize: 12,
    color: "#555",
  },
});
