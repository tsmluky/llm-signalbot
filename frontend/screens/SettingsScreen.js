// screens/SettingsScreen.js
import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  Switch,
  StyleSheet,
  ActivityIndicator,
  Alert,
  TouchableOpacity,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Picker } from "@react-native-picker/picker";
import { API_BASE } from "../constants";

const AVAILABLE_TOKENS = ["BTC", "ETH", "SOL", "MATIC", "ADA", "BNB"];

export default function SettingsScreen() {
  const [defaultMode, setDefaultMode] = useState("lite");
  const [favoriteToken, setFavoriteToken] = useState("BTC");
  const [showCharts, setShowCharts] = useState(true);
  const [loading, setLoading] = useState(true);

  const loadSettings = async () => {
    try {
      const mode = await AsyncStorage.getItem("default_mode");
      const token = await AsyncStorage.getItem("favorite_token");
      const charts = await AsyncStorage.getItem("show_charts");

      if (mode) setDefaultMode(mode);
      if (token) setFavoriteToken(token);
      if (charts !== null) setShowCharts(charts === "true");
    } catch (e) {
      console.warn("❌ Error al cargar ajustes:", e);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      await AsyncStorage.setItem("default_mode", defaultMode);
      await AsyncStorage.setItem("favorite_token", favoriteToken);
      await AsyncStorage.setItem("show_charts", showCharts.toString());
    } catch (e) {
      console.warn("❌ Error al guardar ajustes:", e);
    }
  };

  const handleResetHistory = async () => {
    Alert.alert(
      "¿Confirmar borrado?",
      `¿Deseas borrar el historial del token ${favoriteToken} (${defaultMode.toUpperCase()})?`,
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Borrar",
          style: "destructive",
          onPress: async () => {
            try {
              const url = `${API_BASE}/reset/${defaultMode}/${favoriteToken.toLowerCase()}`;
              console.log("🧼 Reset URL:", url);

              const res = await fetch(url, { method: "DELETE" });
              const data = await res.json();
              console.log("🔁 Reset response:", data);

              if (res.ok && data?.status === "ok") {
                Alert.alert("✅ Historial borrado correctamente");
              } else {
                Alert.alert("⚠️ No se pudo borrar", data?.message || "Error desconocido");
              }
            } catch (error) {
              console.error("❌ Error al resetear historial:", error);
              Alert.alert("❌ Error al borrar", error.message);
            }
          },
        },
      ]
    );
  };

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    if (!loading) saveSettings();
  }, [defaultMode, favoriteToken, showCharts]);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007aff" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>⚙️ Ajustes de SignalBot</Text>

      <View style={styles.setting}>
        <Text style={styles.label}>🎯 Modo por defecto:</Text>
        <View style={styles.row}>
          <Text style={styles.option}>LITE</Text>
          <Switch
            value={defaultMode === "pro"}
            onValueChange={(val) => setDefaultMode(val ? "pro" : "lite")}
            trackColor={{ false: "#ccc", true: "#81d4fa" }}
            thumbColor={defaultMode === "pro" ? "#007aff" : "#eee"}
          />
          <Text style={styles.option}>PRO</Text>
        </View>
      </View>

      <View style={styles.setting}>
        <Text style={styles.label}>💠 Token favorito:</Text>
        <View style={styles.pickerWrapper}>
          <Picker
            selectedValue={favoriteToken}
            onValueChange={setFavoriteToken}
            style={styles.picker}
            dropdownIconColor="#007aff"
            mode="dropdown"
          >
            {AVAILABLE_TOKENS.map((token) => (
              <Picker.Item key={token} label={token} value={token} />
            ))}
          </Picker>
        </View>
      </View>

      <View style={styles.setting}>
        <Text style={styles.label}>📊 Mostrar gráficos en señales:</Text>
        <Switch
          value={showCharts}
          onValueChange={setShowCharts}
          trackColor={{ false: "#ccc", true: "#81d4fa" }}
          thumbColor={showCharts ? "#007aff" : "#eee"}
        />
      </View>

      <TouchableOpacity style={styles.resetButton} onPress={handleResetHistory}>
        <Text style={styles.resetText}>🧼 Borrar historial de este token</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fefefe",
    padding: 20,
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 24,
    textAlign: "center",
  },
  setting: {
    marginBottom: 28,
  },
  label: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 8,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
  },
  option: {
    fontSize: 15,
    marginHorizontal: 8,
    fontWeight: "500",
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 6,
    overflow: "hidden",
  },
  picker: {
    height: 44,
    width: "100%",
  },
  resetButton: {
    marginTop: 20,
    padding: 12,
    backgroundColor: "#eee",
    borderRadius: 8,
    alignItems: "center",
  },
  resetText: {
    color: "#444",
    fontWeight: "500",
  },
});
