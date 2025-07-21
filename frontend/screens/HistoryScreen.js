import React, { useState } from "react";
import { View, Text, StyleSheet, Dimensions } from "react-native";
import { TabView, SceneMap, TabBar } from "react-native-tab-view";
import LogsScreen from "./LogsScreen";
import AnalysisHistoryScreen from "./AnalysisHistoryScreen";

const initialLayout = { width: Dimensions.get("window").width };

export default function HistoryScreen() {
  const [index, setIndex] = useState(0);
  const [routes] = useState([
    { key: "logs", title: "Señales LITE" },
    { key: "analysis", title: "Análisis PRO" },
  ]);

  const renderScene = SceneMap({
    logs: LogsScreen,
    analysis: AnalysisHistoryScreen,
  });

  return (
    <TabView
      navigationState={{ index, routes }}
      renderScene={renderScene}
      onIndexChange={setIndex}
      initialLayout={initialLayout}
      renderTabBar={(props) => (
        <TabBar
          {...props}
          indicatorStyle={{ backgroundColor: "#007aff" }}
          style={{ backgroundColor: "#fdfdfd" }}
          activeColor="#007aff"
          inactiveColor="#999"
          labelStyle={{ fontWeight: "bold" }}
        />
      )}
    />
  );
}
