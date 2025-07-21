// screens/LogsScreen.js
import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
} from "react-native";
import { LineChart } from "react-native-chart-kit";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_STATS } from "../constants";

const API_URL = API_STATS

const CHART_WIDTH = Dimensions.get("window").width - 48;

const TOKEN_IDS = {
  BTC: "bitcoin",
  ETH: "ethereum",
  SOL: "solana",
  MATIC: "matic-network",
  ADA: "cardano",
  BNB: "binancecoin",
};

export default function LogsScreen() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCharts, setShowCharts] = useState(true);
  const [chartCache, setChartCache] = useState({}); // cache por token

  const fetchSignals = async () => {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      if (data.status === "ok" && Array.isArray(data.signals)) {
        setSignals(data.signals);
      } else {
        console.warn("⚠️ No se encontraron señales.");
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

  const fetchPriceChart = async (token) => {
    if (chartCache[token]) return chartCache[token];

    const id = TOKEN_IDS[token.toUpperCase()];
    if (!id) return [];

    try {
      const url = `https://api.coingecko.com/api/v3/coins/${id}/market_chart?vs_currency=usd&days=1`;
      const res = await fetch(url);
      const data = await res.json();
      const prices = data.prices.map(([_, p]) => p).slice(-20);
      setChartCache((prev) => ({ ...prev, [token]: prices }));
      return prices;
    } catch (err) {
      console.warn(`⚠️ Error al obtener precios de ${token}:`, err);
      return [];
    }
  };

  useEffect(() => {
    fetchSignals();
    fetchChartPreference();
  }, []);

  const renderItem = ({ item }) => {
    const [chartData, setChartData] = useState([]);

    useEffect(() => {
      if (showCharts && item.token) {
        fetchPriceChart(item.token).then(setChartData);
      }
    }, []);

    let bgColor = "#e0e0e0";
    if (item.action === "LONG") bgColor = "#e2fbe2";
    if (item.action === "SHORT") bgColor = "#fde1e1";
    if (item.action === "WAIT") bgColor = "#f2f2f2";

    const safe = (val, fallback = "N/D") =>
      val !== undefined && val !== null && val !== "" ? val : fallback;

    return (
      <View style={[styles.card, { backgroundColor: bgColor }]}>
        <View style={styles.row}>
          <Text style={styles.token}>{safe(item.token)}</Text>
          <Text style={styles.price}>
            @ ${parseFloat(item.price || 0).toFixed(2)}
          </Text>
        </View>
        <Text style={styles.action}>🎯 {safe(item.action)}</Text>
        <Text style={styles.details}>
          TP: {safe(item.tp)} | SL: {safe(item.sl)}
        </Text>
        <Text style={styles.details}>
          Confianza: {safe(item.confidence, "?")}% | Riesgo: {safe(item.risk, "?")}/10
        </Text>
        <Text style={styles.details}>⏳ Timeframe: {safe(item.timeframe)}</Text>
        <Text style={styles.timestamp}>
          {new Date(item.timestamp).toLocaleString()}
        </Text>
        {showCharts && chartData.length > 0 && (
          <LineChart
            data={{
              labels: [],
              datasets: [{ data: chartData }],
            }}
            width={CHART_WIDTH}
            height={160}
            withDots={false}
            withVerticalLabels={false}
            withHorizontalLabels={false}
            withInnerLines={false}
            chartConfig={{
              backgroundGradientFrom: "#fff",
              backgroundGradientTo: "#fff",
              color: () => "#007aff",
              strokeWidth: 2,
            }}
            style={{ marginTop: 10, borderRadius: 8 }}
          />
        )}
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
    backgroundColor: "#f9f9f9",
    padding: 16,
  },
  header: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 16,
    textAlign: "center",
  },
  card: {
    padding: 14,
    marginBottom: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#ddd",
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  token: {
    fontSize: 16,
    fontWeight: "bold",
  },
  price: {
    fontSize: 14,
    fontStyle: "italic",
    color: "#333",
  },
  action: {
    fontSize: 15,
    fontWeight: "600",
    marginVertical: 4,
  },
  details: {
    fontSize: 14,
  },
  timestamp: {
    marginTop: 6,
    fontSize: 12,
    color: "#777",
  },
});
