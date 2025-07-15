// screens/AdvisorHistoryScreen.js
import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';

export default function AdvisorHistoryScreen() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://signalbot-api.onrender.com/session_history')
      .then(res => res.json())
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Historial de Sesiones (Advisor)</Text>
      {history.map((item, idx) => (
        <View key={idx} style={styles.card}>
          <Text style={styles.token}>🪙 Token: {item.token}</Text>
          <Text style={styles.label}>🗨️ Usuario:</Text>
          <Text style={styles.content}>{item.user_message}</Text>
          <Text style={styles.label}>🤖 Respuesta:</Text>
          <Text style={styles.content}>{item.advisor_response}</Text>
          <Text style={styles.date}>🕒 {item.timestamp}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  container: { padding: 10, backgroundColor: '#fff' },
  title: { fontSize: 22, fontWeight: 'bold', marginBottom: 10, textAlign: 'center' },
  card: { marginBottom: 15, padding: 10, backgroundColor: '#f0f0f0', borderRadius: 10 },
  token: { fontWeight: 'bold', fontSize: 16, marginBottom: 5 },
  label: { fontWeight: '600', marginTop: 5 },
  content: { marginLeft: 5, marginTop: 2 },
  date: { fontStyle: 'italic', fontSize: 12, marginTop: 5, textAlign: 'right' },
});
