import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import Markdown from "react-native-markdown-display";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getLLMResponse } from "../services/llmService";

const STORAGE_KEY = "advisor_chat_history";

const AdvisorChatScreen = () => {
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef();

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
    saveHistory();
  }, [history]);

  const loadHistory = async () => {
    try {
      const saved = await AsyncStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) setHistory(parsed);
      }
    } catch (err) {
      console.error("❌ Error cargando historial:", err);
    }
  };

  const saveHistory = async () => {
    try {
      const limited = history.slice(-50); // Máximo 50 mensajes
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(limited));
    } catch (err) {
      console.error("❌ Error guardando historial:", err);
    }
  };

  const scrollToBottom = () => {
    scrollRef.current?.scrollToEnd({ animated: true });
  };

  const handleSend = async () => {
    const trimmed = prompt.trim();
    if (!trimmed) return;

    const userMessage = {
      sender: "user",
      text: trimmed,
      timestamp: new Date().toISOString(),
    };

    setHistory((prev) => [...prev, userMessage]);
    setPrompt("");
    setLoading(true);

    try {
      const response = await getLLMResponse(trimmed, "BTC", "advisor");
      const botMessage = {
        sender: "bot",
        text: response || "⚠️ Sin respuesta del modelo.",
        timestamp: new Date().toISOString(),
      };
      setHistory((prev) => [...prev, botMessage]);
    } catch (err) {
      setHistory((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "❌ Error al obtener respuesta.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <Text style={styles.header}>👨‍🏫 Consejo Financiero</Text>

      <ScrollView
        style={styles.history}
        ref={scrollRef}
        keyboardShouldPersistTaps="handled"
      >
        {history.map((msg, index) => (
          <View
            key={index}
            style={[
              styles.messageBubble,
              msg.sender === "user" ? styles.userBubble : styles.botBubble,
            ]}
          >
            <Text style={styles.modeTag}>
              {msg.sender === "user" ? "Tú" : "🤖 elbot"}
            </Text>
            {msg.sender === "user" ? (
              <Text style={styles.userText}>{msg.text}</Text>
            ) : (
              <Markdown style={markdownStyles}>{msg.text}</Markdown>
            )}
          </View>
        ))}
        {loading && (
          <ActivityIndicator
            size="small"
            color="#007aff"
            style={{ marginVertical: 10 }}
          />
        )}
      </ScrollView>

      <TextInput
        style={styles.promptInput}
        placeholder="Escribe tu consulta libre..."
        value={prompt}
        onChangeText={setPrompt}
        multiline
      />

      <TouchableOpacity
        style={[
          styles.sendButton,
          { backgroundColor: loading || !prompt.trim() ? "#ccc" : "#007aff" },
        ]}
        onPress={handleSend}
        disabled={loading || !prompt.trim()}
      >
        <Text style={styles.sendButtonText}>
          {loading ? "Enviando..." : "Enviar"}
        </Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
};

export default AdvisorChatScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#fdfdfd",
  },
  header: {
    fontSize: 20,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10,
  },
  history: {
    flex: 1,
    marginTop: 10,
  },
  messageBubble: {
    padding: 10,
    marginVertical: 6,
    borderRadius: 8,
    maxWidth: "90%",
  },
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: "#e1f5fe",
  },
  botBubble: {
    alignSelf: "flex-start",
    backgroundColor: "#f0f4c3",
  },
  userText: {
    color: "#333",
  },
  modeTag: {
    fontSize: 12,
    color: "#666",
    marginBottom: 4,
    fontStyle: "italic",
  },
  promptInput: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 10,
    minHeight: 60,
    textAlignVertical: "top",
    marginTop: 10,
  },
  sendButton: {
    marginTop: 10,
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  sendButtonText: {
    color: "#fff",
    fontWeight: "600",
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
