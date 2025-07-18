// screens/StatsScreen.js

import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";

const API_URL = "https://signalbot-api.onrender.com/stats_lite";

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
        <Stat label="📌 Total" value={stats.total_signals} />
        <Stat label="🟢 LONG" value={stats.long_count} />
        <Stat label="🔴 SHORT" value={stats.short_count} />
        <Stat label="⚪ ESPERAR" value={stats.wait_count} />
        <Stat label="📊 Confianza promedio" value={`${stats.avg_confidence}%`} />
        <Stat label="⚠️ Riesgo promedio" value={`${stats.avg_risk}/10`} />
      </View>
    </View>
  );
}

const Stat = ({ label, value }) => (
  <View style={styles.statRow}>
    <Text style={styles.statLabel}>{label}</Text>
    <Text style={styles.statValue}>{value}</Text>
  </View>
);

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
    elevation: 2,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  statRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  statLabel: {
    fontSize: 16,
    fontWeight: "500",
  },
  statValue: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
  },
});
