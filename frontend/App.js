// App.js
import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HomeScreen from "./screens/HomeScreen";
import ChatScreen from "./screens/ChatScreen";
import LogsScreen from "./screens/LogsScreen"; // 👈 Añadido si usas Logs
import StatsScreen from "./screens/StatsScreen"; // 👈 Añadido si usas Stats

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Inicio"
        screenOptions={{
          headerStyle: { backgroundColor: "#007aff" },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "bold" },
        }}
      >
        <Stack.Screen
          name="Inicio"
          component={HomeScreen}
          options={{ title: "LLM SignalBot" }}
        />
        <Stack.Screen
          name="Chat"
          component={ChatScreen}
          options={({ route }) => ({
            title: `Análisis: ${route.params?.token || "Token"}`,
          })}
        />
        <Stack.Screen
          name="Historial"
          component={LogsScreen}
          options={{ title: "Historial de Señales" }}
        />
        <Stack.Screen
          name="Estadísticas"
          component={StatsScreen}
          options={{ title: "Estadísticas Globales" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
