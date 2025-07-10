// screens/ChatScreen.js
import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  ScrollView,
  StyleSheet,
} from "react-native";
import Markdown from "react-native-markdown-display";
import { getLLMResponse } from "../services/llmService";

const ChatScreen = ({ route }) => {
  const initialToken = route?.params?.token || "BTC";
  const [token, setToken] = useState(initialToken);
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!prompt.trim() || !token.trim()) return;

    const newUserMessage = { sender: "user", text: prompt };
    setHistory((prev) => [...prev, newUserMessage]);
    setPrompt("");
    setLoading(true);

    try {
      const response = await getLLMResponse(prompt, token);
      const botMessage = { sender: "bot", text: response };
      setHistory((prev) => [...prev, botMessage]);
    } catch (err) {
      setHistory((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Error en la respuesta" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>LLM SignalBot Chat</Text>

      <TextInput
        style={styles.tokenInput}
        placeholder="Token (ej. BTC, ETH)"
        value={token}
        onChangeText={setToken}
      />

      <TextInput
        style={styles.promptInput}
        placeholder="¿Qué deseas preguntar?"
        value={prompt}
        onChangeText={setPrompt}
        multiline
      />

      <Button
        title={loading ? "Enviando..." : "Enviar"}
        onPress={handleSend}
        disabled={loading}
      />

      <ScrollView style={styles.history}>
        {history.map((msg, index) =>
          msg.sender === "user" ? (
            <Text key={index} style={styles.userMsg}>
              Tú: {msg.text}
            </Text>
          ) : (
            <View key={index} style={styles.botMsg}>
              <Markdown style={markdownStyles}>{msg.text}</Markdown>
            </View>
          )
        )}
      </ScrollView>
    </View>
  );
};

export default ChatScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#fff",
  },
  header: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 15,
  },
  tokenInput: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
  },
  promptInput: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 10,
    minHeight: 60,
    textAlignVertical: "top",
    marginBottom: 10,
  },
  history: {
    marginTop: 20,
  },
  userMsg: {
    alignSelf: "flex-end",
    backgroundColor: "#e0f7fa",
    borderRadius: 10,
    padding: 8,
    marginVertical: 4,
    maxWidth: "80%",
  },
  botMsg: {
    alignSelf: "flex-start",
    backgroundColor: "#f1f8e9",
    borderRadius: 10,
    padding: 10,
    marginVertical: 4,
    maxWidth: "90%",
  },
});

const markdownStyles = {
  body: {
    color: "#333",
    fontSize: 14,
  },
  heading1: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 8,
  },
  heading2: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 6,
  },
  strong: {
    fontWeight: "bold",
  },
  bullet_list: {
    marginVertical: 4,
  },
};
