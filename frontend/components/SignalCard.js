import React from "react";
import { View, Text, StyleSheet } from "react-native";

const parseSignal = (raw) => {
  const extract = (label) => {
    const match = raw?.match(new RegExp(`\\[${label}\\]:\\s*(.+)`));
    return match ? match[1].trim() : "N/A";
  };

  return {
    action: extract("ACTION"),
    confidence: extract("CONFIDENCE"),
    risk: extract("RISK"),
    timeframe: extract("TIMEFRAME"),
    price: extract("PRICE"),
  };
};

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

const SignalCard = ({ content, timestamp }) => {
  const { action, confidence, risk, timeframe, price } = parseSignal(content);
  const bgColor = getCardColor(action);

  let formattedTime = "—";
  try {
    formattedTime = new Date(timestamp).toLocaleString("es-ES", {
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

  return (
    <View style={[styles.card, { backgroundColor: bgColor }]}>
      <View style={styles.row}>
        <Text style={styles.label}>🕓 Hora:</Text>
        <Text style={styles.value}>{formattedTime}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>💰 Precio:</Text>
        <Text style={styles.value}>
          {price !== "N/A" ? `$${price}` : "N/D"}
        </Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>🎯 Acción:</Text>
        <Text style={styles.value}>{action}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>📈 Confianza:</Text>
        <Text style={styles.value}>{confidence}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>⚠️ Riesgo:</Text>
        <Text style={styles.value}>{risk}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>⏱️ Timeframe:</Text>
        <Text style={styles.value}>{timeframe}</Text>
      </View>
    </View>
  );
};

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
    marginBottom: 8,
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
});

export default SignalCard;
