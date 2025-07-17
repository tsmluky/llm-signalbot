// screens/LogsScreen.js
import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from "react-native";

const API_URL = "https://signalbot-api.onrender.com/signals_lite";

export default function LogsScreen() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSignals = async () => {
    try {
      const res = await fetch(API_URL);
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

  useEffect(() => {
    fetchSignals();
  }, []);

  const renderItem = ({ item }) => {
    const bgColor =
      item.action === "LONG"
        ? "#d4fcd2"
        : item.action === "SHORT"
        ? "#fddcdc"
        : "#e0e0e0";

    return (
      <View style={[styles.card, { backgroundColor: bgColor }]}>
        <Text style={styles.token}>
          {item.token} @ ${parseFloat(item.price || 0).toFixed(2)}
        </Text>
        <Text style={styles.action}>🎯 Acción: {item.action}</Text>
        <Text style={styles.details}>
          TP: {item.tp || "N/D"} | SL: {item.sl || "N/D"}
        </Text>
        <Text style={styles.details}>
          Confianza: {item.confidence || "?"}% | Riesgo: {item.risk || "?"}
        </Text>
        <Text style={styles.details}>⏳ Timeframe: {item.timeframe || "?"}</Text>
        <Text style={styles.timestamp}>
          {new Date(item.timestamp).toLocaleString()}
        </Text>
      </View>
    );
  };

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
    backgroundColor: "#fafafa",
    padding: 16,
  },
  header: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 12,
    textAlign: "center",
  },
  card: {
    padding: 12,
    marginBottom: 12,
    borderRadius: 10,
    elevation: 2,
  },
  token: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 4,
  },
  action: {
    fontSize: 15,
    fontWeight: "600",
    marginBottom: 2,
  },
  details: {
    fontSize: 14,
    marginBottom: 1,
  },
  timestamp: {
    marginTop: 6,
    fontSize: 12,
    color: "#555",
  },
});
