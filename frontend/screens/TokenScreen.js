// screens/TokenScreen.js
import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';

export default function TokenScreen({ route }) {
  const { token } = route.params;
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');

  const handleSend = async () => {
    try {
      const res = await fetch('http://192.168.1.227:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, message }),
      });
      const data = await res.json();
      setResponse(data.analysis);
    } catch (error) {
      setResponse('Error al conectar con el servidor.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Análisis de {token}</Text>
      <TextInput
        style={styles.input}
        placeholder="¿Qué deseas preguntar?"
        value={message}
        onChangeText={setMessage}
      />
      <Button title="ENVIAR" onPress={handleSend} />
      <Text style={styles.response}>{response}</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 10 },
  input: {
    borderColor: '#ccc',
    borderWidth: 1,
    marginBottom: 10,
    padding: 10,
    borderRadius: 6,
  },
  response: {
    marginTop: 20,
    backgroundColor: '#f0fdf4',
    padding: 10,
    borderRadius: 6,
    fontStyle: 'italic',
  },
});
