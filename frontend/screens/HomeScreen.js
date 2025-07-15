import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Switch,
  Button,
} from "react-native";

const tokens = ["BTC", "ETH", "SOL", "MATIC", "ADA", "LINK", "DOGE", "AVAX"];

export default function HomeScreen({ navigation }) {
  const [isProMode, setIsProMode] = useState(false);

  const handleTokenPress = (token) => {
    navigation.navigate("Chat", {
      token,
      mode: isProMode ? "pro" : "lite",
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Selecciona un Token</Text>

      <View style={styles.modeContainer}>
        <Text style={styles.modeLabel}>
          Modo: {isProMode ? "PRO" : "LITE"}
        </Text>
        <Switch
          value={isProMode}
          onValueChange={setIsProMode}
          trackColor={{ false: "#aaa", true: "#81d4fa" }}
          thumbColor={isProMode ? "#007aff" : "#ccc"}
        />
      </View>

      <FlatList
        data={tokens}
        keyExtractor={(item) => item}
        numColumns={3}
        contentContainerStyle={styles.tokenGrid}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.tokenCard}
            onPress={() => handleTokenPress(item)}
          >
            <Text style={styles.tokenText}>{item}</Text>
          </TouchableOpacity>
        )}
      />

      <View style={styles.extraOptions}>
        <Button
          title="📜 Historial Señales LITE"
          onPress={() => navigation.navigate("Historial")}
        />
        <Button
          title="📈 Estadísticas Globales"
          onPress={() => navigation.navigate("Estadísticas")}
        />

        {/* ✅ Botón para acceder al nuevo modo Advisor */}
        <TouchableOpacity
          style={styles.navButton}
          onPress={() =>
            navigation.navigate("AdvisorChat", {
              token: "BTC",
              mode: "advisor",
            })
          }
        >
          <Text style={styles.buttonText}>🎓 Asesor Financiero</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 40,
    paddingHorizontal: 16,
    backgroundColor: "#fdfdfd",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 16,
  },
  modeContainer: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  modeLabel: {
    marginRight: 8,
    fontSize: 16,
    fontWeight: "500",
  },
  tokenGrid: {
    justifyContent: "center",
  },
  tokenCard: {
    backgroundColor: "#e1f5fe",
    padding: 20,
    margin: 8,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    width: 90,
    elevation: 3,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
  tokenText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#007aff",
  },
  extraOptions: {
    marginTop: 30,
    gap: 10,
  },
  navButton: {
    backgroundColor: "#2196f3",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "600",
  },
});
