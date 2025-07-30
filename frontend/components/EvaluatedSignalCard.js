import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { AntDesign } from "@expo/vector-icons";
import SignalCard from "./SignalCard";
import ResultCard from "./ResultCard";

const TOKEN_IDS = {
  BTC: "bitcoin",
  ETH: "ethereum",
  SOL: "solana",
  MATIC: "matic-network",
  ADA: "cardano",
  BNB: "binancecoin",
};

const evaluateSignal = async (signal) => {
  const tokenId = TOKEN_IDS[signal.token?.toUpperCase()];
  if (!tokenId || !signal.timestamp || !signal.analysis) return { evaluated: false };

  const past = new Date(signal.timestamp);
  const now = new Date();
  const hoursPassed = (now - past) / 1000 / 60 / 60;

  if (hoursPassed < 2) return { evaluated: false };

  try {
    const url = `https://api.coingecko.com/api/v3/coins/${tokenId}/market_chart?vs_currency=usd&days=1`;
    const res = await fetch(url);
    const data = await res.json();

    const futurePrice = data.prices.find(([t]) => {
      const diff = Math.abs(t - past.getTime());
      return diff > 2 * 60 * 60 * 1000;
    });

    if (!futurePrice) return { evaluated: false };

    const final = futurePrice[1];
    const priceMatch = signal.analysis.match(/\[PRICE\]:\s*(\d+(\.\d+)?)/);
    const initial = priceMatch ? parseFloat(priceMatch[1]) : NaN;
    if (!initial || isNaN(initial)) return { evaluated: false };

    const diffPercent = ((final - initial) / initial) * 100;
    const actionMatch = signal.analysis.match(/\[ACTION\]:\s*(\w+)/);
    const action = actionMatch ? actionMatch[1].toUpperCase() : "WAIT";

    let result = "pending";
    if (action === "LONG" && diffPercent > 1) result = "correct";
    else if (action === "SHORT" && diffPercent < -1) result = "correct";
    else if (action === "WAIT" && Math.abs(diffPercent) < 1) result = "correct";
    else result = "wrong";

    return {
      evaluated: true,
      result,
      percent: diffPercent,
    };
  } catch (err) {
    console.warn("❌ Error evaluando señal:", err);
    return { evaluated: false };
  }
};

export default function EvaluatedSignalCard({ signal, onDelete }) {
  const [result, setResult] = useState(null);

  useEffect(() => {
    evaluateSignal(signal).then(setResult);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>📡 SEÑAL LITE</Text>
        <TouchableOpacity onPress={onDelete}>
          <AntDesign name="closecircleo" size={20} color="#888" />
        </TouchableOpacity>
      </View>
      <View style={styles.rowContainer}>
        <SignalCard content={signal.analysis} timestamp={signal.timestamp} />
        <ResultCard
          result={result?.result}
          percent={result?.percent || 0}
          evaluated={result?.evaluated || false}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 20,
    paddingHorizontal: 6,
  },
  rowContainer: {
    flexDirection: "row",
    alignItems: "flex-start",
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
    marginHorizontal: 12,
  },
  title: {
    fontSize: 15,
    fontWeight: "bold",
    color: "#aa8800",
  },
});
