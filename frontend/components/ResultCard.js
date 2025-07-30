import React from "react";
import { View, Text, StyleSheet } from "react-native";

const ResultCard = ({ result, percent = 0, evaluated }) => {
  const safePercent = isNaN(percent) ? 0 : percent;

  const getColor = () => {
    if (!evaluated) return "#ccc";
    return result === "correct" ? "#d4f8d4" : "#f9d0d0";
  };

  const getText = () => {
    if (!evaluated) return "⏳ En espera de evaluación";
    return result === "correct"
      ? `✅ CORRECTA (+${safePercent.toFixed(2)}%)`
      : `❌ INCORRECTA (${safePercent.toFixed(2)}%)`;
  };

  return (
    <View style={[styles.card, { backgroundColor: getColor() }]}>
      <Text style={styles.text}>{getText()}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    padding: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#ddd",
    minWidth: 130,
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 8,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  text: {
    fontSize: 13,
    fontWeight: "bold",
    textAlign: "center",
    color: "#333",
  },
});

export default ResultCard;
