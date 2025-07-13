// screens/StatsScreen.js
import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";

const API_URL = "http://localhost:8000/stats_lite"; // ⚠️ Cambiar por tu IP si usas móvil

export default function StatsScreen() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setStats(data.stats || {});
    } catch (err) {
      console.error("❌ Error al obtener estadísticas:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007aff" />
      </View>
    );
  }

  if (!stats || Object.keys(stats).length === 0) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>📊 Sin estadísticas disponibles aún.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📈 Estadísticas de Señales LITE</Text>
      <View style={styles.card}>
        <Text style={styles.item}>Total: {stats.total_signals}</Text>
        <Text style={styles.item}>🟢 LONG: {stats.long_count}</Text>
        <Text style={styles.item}>🔴 SHORT: {stats.short_count}</Text>
        <Text style={styles.item}>⚪ ESPERAR: {stats.wait_count}</Text>
        <Text style={styles.item}>📊 Confianza promedio: {stats.avg_confidence}%</Text>
        <Text style={styles.item}>⚠️ Riesgo promedio: {stats.avg_risk}/10</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fafafa",
    padding: 20,
    justifyContent: "center",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  card: {
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 10,
    elevation: 3,
  },
  item: {
    fontSize: 16,
    marginBottom: 10,
  },
});
