// frontend/screens/LogsScreen.js
import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from "react-native";
import { API_SIGNALS } from "../constants";
import EvaluatedSignalCard from "../components/EvaluatedSignalCard";
import { Picker } from "@react-native-picker/picker"

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
  const [selectedToken, setSelectedToken] = useState("ETH");

  const fetchSignals = useCallback(async () => {
    setLoading(true);
    try {
      const url = `${API_SIGNALS}/lite/${selectedToken.toLowerCase()}`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.status === "ok" && Array.isArray(data.signals)) {
        const cleanSignals = data.signals.filter(
          (s) =>
            s &&
            typeof s === "object" &&
            s.timestamp &&
            s.price &&
            s.action &&
            s.confidence &&
            s.risk &&
            s.timeframe
        );

        const parsed = cleanSignals.reverse().map((s, index) => ({
          ...s,
          id: `${s.timestamp}-${index}`, // ID único
        }));
        setSignals(parsed);
      } else {
        console.warn("⚠️ Respuesta inesperada:", data);
        setSignals([]);
      }
    } catch (err) {
      console.error("❌ Error al cargar señales:", err);
      Alert.alert("Error", "No se pudo cargar el historial.");
      setSignals([]);
    } finally {
      setLoading(false);
    }
  }, [selectedToken]);

  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

  const deleteSignal = (signalId) => {
    Alert.alert("¿Eliminar señal?", "Esta acción no se puede deshacer.", [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Eliminar",
        style: "destructive",
        onPress: () => {
          setSignals((prev) => prev.filter((s) => s.id !== signalId));
        },
      },
    ]);
  };

  const renderItem = ({ item }) => {
    if (!item || typeof item !== "object") {
      console.warn("❌ Item inválido:", item);
      return (
        <Text style={{ color: "red", padding: 10 }}>
          ❌ Error: señal inválida
        </Text>
      );
    }

    const {
      timestamp,
      action,
      price,
      confidence,
      risk,
      timeframe
    } = item;

    if (!timestamp || !action || !price || !confidence || !risk || !timeframe) {
      console.warn("⚠️ Señal incompleta:", item);
      return (
        <Text style={{ color: "orange", padding: 10 }}>
          ⚠️ Señal incompleta
        </Text>
      );
    }

    return (
      <EvaluatedSignalCard
        signal={item}
        onDelete={() => deleteSignal(item.id)}
      />
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
          {Object.keys(TOKEN_IDS).map((token) => (
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
          keyExtractor={(item) => item.id}
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
  noData: {
    textAlign: "center",
    marginTop: 40,
    fontSize: 16,
    color: "#888",
  },
});
