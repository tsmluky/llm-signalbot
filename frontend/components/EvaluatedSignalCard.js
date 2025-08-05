import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { AntDesign } from "@expo/vector-icons";

const TOKEN_IDS = {
  BTC: "bitcoin",
  ETH: "ethereum",
  SOL: "solana",
  MATIC: "matic-network",
  ADA: "cardano",
  BNB: "binancecoin",
};

const evaluateSignal = async (signal) => {
  try {
    const tokenId = TOKEN_IDS[signal.token?.toUpperCase()];
    if (!tokenId || !signal.timestamp || !signal.price || !signal.action) return { evaluated: false };

    const past = new Date(signal.timestamp);
    const now = new Date();
    const hoursPassed = (now - past) / 1000 / 60 / 60;

    if (hoursPassed < 2) return { evaluated: false };

    const url = `https://api.coingecko.com/api/v3/coins/${tokenId}/market_chart?vs_currency=usd&days=1`;
    const res = await fetch(url);
    const data = await res.json();

    const futurePrice = data.prices.find(([t]) => {
      const diff = Math.abs(t - past.getTime());
      return diff > 2 * 60 * 60 * 1000;
    });

    if (!futurePrice) return { evaluated: false };

    const final = futurePrice[1];
    const initial = parseFloat(signal.price);
    if (!initial || isNaN(initial)) return { evaluated: false };

    const diffPercent = ((final - initial) / initial) * 100;
    const action = signal.action.toUpperCase();

    let result = "pending";
    if (action === "LONG" && diffPercent > 1) result = "correct";
    else if (action === "SHORT" && diffPercent < -1) result = "correct";
    else if (action === "WAIT" && Math.abs(diffPercent) < 1) result = "correct";
    else result = "wrong";

    return {
      evaluated: true,
      result,
      percent: parseFloat(diffPercent.toFixed(2)),
    };
  } catch (err) {
    console.warn("❌ Error evaluando señal:", err);
    return { evaluated: false };
  }
};

export default function EvaluatedSignalCard({ signal, onDelete }) {
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!signal.evaluation || !signal.evaluation.result) {
      evaluateSignal(signal).then(setResult);
    } else {
      setResult(signal.evaluation);
    }
  }, []);

  const getCardColor = (action) => {
    switch (action?.toUpperCase()) {
      case "LONG":
        return "#e2fbe2";
      case "SHORT":
        return "#fde1e1";
      case "WAIT":
      case "ESPERAR":
        return "#fff9d9";
      default:
        return "#f5f5f5";
    }
  };

  const bgColor = getCardColor(signal.action);

  let formattedTime = "—";
  try {
    formattedTime = new Date(signal.timestamp).toLocaleString("es-ES", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  } catch {
    formattedTime = "—";
  }

  const renderEvaluation = () => {
    if (!result || !result.evaluated) {
      return (
        <Text style={styles.pendingEval}>
          ⏳ En espera de evaluación (mín. 2h)
        </Text>
      );
    }

    const { result: res, percent } = result;
    const isCorrect = res === "correct";

    return (
      <Text style={[styles.evalResult, { color: isCorrect ? "#2e7d32" : "#c62828" }]}>
        {isCorrect ? "✅ CORRECTA" : "❌ INCORRECTA"} ({percent > 0 ? "+" : ""}
        {percent}%)
      </Text>
    );
  };

  return (
    <View style={[styles.card, { backgroundColor: bgColor }]}>
      <View style={styles.header}>
        <Text style={styles.title}>📡 SEÑAL LITE</Text>
        <TouchableOpacity onPress={onDelete}>
          <AntDesign name="closecircleo" size={20} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>🕓 Hora:</Text>
        <Text style={styles.value}>{formattedTime}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>💰 Precio:</Text>
        <Text style={styles.value}>
          {signal.price ? `$${signal.price}` : "N/D"}
        </Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>🎯 Acción:</Text>
        <Text style={styles.value}>{signal.action}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>📈 Confianza:</Text>
        <Text style={styles.value}>{signal.confidence}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>⚠️ Riesgo:</Text>
        <Text style={styles.value}>{signal.risk}</Text>
      </View>
      <View style={styles.row}>
        <Text style={styles.label}>⏱️ Timeframe:</Text>
        <Text style={styles.value}>{signal.timeframe}</Text>
      </View>

      <View style={styles.evalContainer}>{renderEvaluation()}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: "#ddd",
    backgroundColor: "#fefefe",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 1,
    marginBottom: 14,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  title: {
    fontSize: 15,
    fontWeight: "bold",
    color: "#aa8800",
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 6,
  },
  label: {
    fontWeight: "600",
    color: "#444",
    fontSize: 13,
  },
  value: {
    fontSize: 13,
    color: "#000",
  },
  evalContainer: {
    marginTop: 10,
    alignItems: "center",
  },
  evalResult: {
    fontSize: 14,
    fontWeight: "bold",
  },
  pendingEval: {
    fontSize: 13,
    color: "#777",
  },
});
