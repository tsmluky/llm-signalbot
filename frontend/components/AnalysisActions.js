import React from 'react';
import { View, TouchableOpacity, StyleSheet, Alert, Share } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { Feather } from '@expo/vector-icons';

const AnalysisActions = ({ content }) => {
  const copyToClipboard = async () => {
    await Clipboard.setStringAsync(content);
    Alert.alert("✅ Copiado", "Análisis copiado al portapapeles.");
  };

  const shareAnalysis = async () => {
    try {
      await Share.share({ message: content });
    } catch (error) {
      Alert.alert("❌ Error al compartir", error.message);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={copyToClipboard} style={styles.iconButton}>
        <Feather name="copy" size={20} color="#1a73e8" />
      </TouchableOpacity>
      <TouchableOpacity onPress={shareAnalysis} style={styles.iconButton}>
        <Feather name="share" size={20} color="#1a73e8" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 16,
    marginBottom: 12,
    marginRight: 12,
    marginTop: -6,
  },
  iconButton: {
    backgroundColor: '#E8F0FE',
    padding: 8,
    borderRadius: 8,
  },
});

export default AnalysisActions;
