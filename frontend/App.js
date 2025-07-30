// App.js

import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Ionicons } from "@expo/vector-icons";

import ChatScreen from "./screens/ChatScreen";
import AdvisorChatScreen from "./screens/AdvisorChatScreen";
import LogsScreen from "./screens/LogsScreen";
import SettingsScreen from "./screens/SettingsScreen";

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        initialRouteName="Chat"
        screenOptions={({ route }) => ({
          tabBarIcon: ({ color, size }) => {
            let iconName;
            switch (route.name) {
              case "Chat":
                iconName = "chatbubble-ellipses";
                break;
              case "Advisor":
                iconName = "school";
                break;
              case "Historial":
                iconName = "list";
                break;
              case "Ajustes":
                iconName = "settings";
                break;
              default:
                iconName = "ellipse";
            }
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: "#007aff",
          tabBarInactiveTintColor: "gray",
          headerStyle: { backgroundColor: "#007aff" },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "bold" },
        })}
      >
        <Tab.Screen name="Chat" component={ChatScreen} />
        <Tab.Screen name="Advisor" component={AdvisorChatScreen} options={{ title: "Asesor" }} />
        <Tab.Screen name="Historial" component={LogsScreen} />
        <Tab.Screen name="Ajustes" component={SettingsScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
