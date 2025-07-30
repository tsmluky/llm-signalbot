// frontend/screens/LogsScreen.js

import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Picker,
} from "react-native";
import { API_SIGNALS } from "../constants";
import SignalCard from "../components/SignalCard";
import ResultCard from "../components/ResultCard";

const TOKEN_LIST = ["BTC", "ETH", "SOL", "MATIC", "ADA", "BNB"];

export default function LogsScreen() {
  const [selectedToken, setSelectedToken] = useState("ETH");
  const [signals, setSignals] = useState([]);
  const [evaluated, setEvaluated] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const base = `${API_SIGNALS}/lite/${selectedToken.toLowerCase()}`;
      const evalUrl = `${API_SIGNALS}/evaluated/${selectedToken.toLowerCase()}`;

      const [signalsRes, evaluatedRes] = await Promise.all([
        fetch(base),
        fetch(evalUrl),
      ]);

      const sData = await signalsRes.json();
      const eData = await evaluatedRes.json();

      if (sData.status === "ok") setSignals(sData.signals || []);
      else setSignals([]);

      if (eData.status === "ok") setEvaluated(eData.signals || []);
      else setEvaluated([]);
    } catch (err) {
      console.error("❌ Error al cargar señales:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignals();
  }, [selectedToken]);

  const renderItem = ({ item, index }) => {
    const result = evaluated.find((e) => e.id === item.id);
    const evaluatedResult = result
      ? {
          result: result.result?.toLowerCase(),
          percent: parseFloat(result.change_pct),
          evaluated: true,
        }
      : {
          result: "pendiente",
          percent: 0,
          evaluated: false,
        };

    return (
      <View style={styles.rowContainer} key={item.id || index.toString()}>
        <SignalCard
          content={item.raw || item.analysis || ""}
          timestamp={item.timestamp}
        />
        <ResultCard
          result={evaluatedResult.result}
          percent={evaluatedResult.percent}
          evaluated={evaluatedResult.evaluated}
        />
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>📡 Evaluación de Señales LITE</Text>

      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={selectedToken}
          style={styles.picker}
          onValueChange={setSelectedToken}
        >
          {TOKEN_LIST.map((token) => (
            <Picker.Item key={token} label={token} value={token} />
          ))}
        </Picker>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#007aff" />
      ) : signals.length === 0 ? (
        <Text style={styles.noData}>
          No hay señales registradas para este token.
        </Text>
      ) : (
        <FlatList
          data={signals}
          keyExtractor={(item, index) => item.id || index.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 40 }}
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
  pickerContainer: {
    marginBottom: 16,
    paddingHorizontal: 8,
  },
  picker: {
    height: 44,
    width: "100%",
  },
  rowContainer: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 20,
    paddingRight: 6,
  },
  noData: {
    textAlign: "center",
    marginTop: 40,
    fontSize: 16,
    color: "#888",
  },
});
