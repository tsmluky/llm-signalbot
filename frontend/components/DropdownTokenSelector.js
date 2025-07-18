// components/DropdownTokenSelector.js

import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Picker } from "@react-native-picker/picker";

const DropdownTokenSelector = ({ token, setToken, tokens = [] }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>Token:</Text>
      <View style={styles.pickerWrapper}>
        <Picker
          selectedValue={token}
          onValueChange={setToken}
          style={styles.picker}
        >
          {tokens.map((item) => (
            <Picker.Item label={item} value={item} key={item} />
          ))}
        </Picker>
      </View>
    </View>
  );
};

export default DropdownTokenSelector;

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  label: {
    fontWeight: "600",
    marginRight: 10,
  },
  pickerWrapper: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 6,
    overflow: "hidden",
  },
  picker: {
    height: 40,
    width: "100%",
  },
});
