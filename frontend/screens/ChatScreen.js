import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  Switch,
  ActivityIndicator,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import Markdown from "react-native-markdown-display";
import { getLLMResponse } from "../services/llmService";

const MAX_MESSAGES = 50; // puedes ajustar el límite aquí

const ChatScreen = ({ route }) => {
  const initialToken = route?.params?.token || "BTC";
  const initialMode = route?.params?.mode || "lite";
  const [token, setToken] = useState(initialToken);
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isProMode, setIsProMode] = useState(initialMode === "pro");

  const scrollRef = useRef();
  const mode = isProMode ? "pro" : "lite";

  const STORAGE_KEY = `advisor_history_${token.toUpperCase()}`;

  const saveHistory = async (data) => {
    try {
      const sliced = data.slice(-MAX_MESSAGES);
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(sliced));
    } catch (e) {
      console.warn("❌ Error guardando historial:", e);
    }
  };

  const loadHistory = async () => {
    try {
      const saved = await AsyncStorage.getItem(STORAGE_KEY);
      if (saved) setHistory(JSON.parse(saved));
    } catch (e) {
      console.warn("❌ Error cargando historial:", e);
    }
  };

  const handleSend = async () => {
    if (!prompt.trim() || !token.trim()) return;

    const newUserMessage = {
      sender: "user",
      text: prompt,
      mode,
      timestamp: new Date().toISOString(),
    };

    const updatedHistory = [...history, newUserMessage];
    setHistory(updatedHistory);
    setPrompt("");
    setLoading(true);

    try {
      const response = await getLLMResponse(prompt, token, mode);
      const botMessage = {
        sender: "bot",
        text: response,
        mode,
        timestamp: new Date().toISOString(),
      };

      const finalHistory = [...updatedHistory, botMessage];
      setHistory(finalHistory);

      if (mode === "advisor") {
        await saveHistory(finalHistory);
      }
    } catch (err) {
      setHistory((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "❌ Error en la respuesta",
          mode,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollToEnd({ animated: true });
    }
  }, [history]);

  useEffect(() => {
    if (mode === "advisor") {
      loadHistory();
    }
  }, [mode, token]);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={100}
    >
      <View style={{ flex: 1 }}>
        <View style={styles.headerContainer}>
          <Text style={styles.header}>LLM SignalBot</Text>
          <View style={styles.modeToggle}>
            <Text style={styles.modeText}>{isProMode ? "PRO" : "LITE"} Mode</Text>
            <Switch
              value={isProMode}
              onValueChange={setIsProMode}
              trackColor={{ false: "#ccc", true: "#81d4fa" }}
              thumbColor={isProMode ? "#007aff" : "#eee"}
            />
          </View>
        </View>

        <View style={styles.tokenContainer}>
          <Text style={styles.tokenLabel}>Token:</Text>
          <TextInput
            style={styles.tokenInput}
            placeholder="Ej: BTC, ETH"
            value={token}
            onChangeText={setToken}
          />
        </View>

        <ScrollView style={styles.history} ref={scrollRef}>
          {history.map((msg, index) => (
            <View
              key={index}
              style={[
                styles.messageBubble,
                msg.sender === "user"
                  ? styles.userBubble
                  : styles.botBubble,
              ]}
            >
              <Text style={styles.modeTag}>
                {msg.sender === "user" ? "Tú" : "elBot"} | Modo:{" "}
                {msg.mode.toUpperCase()}
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
              style={{ marginTop: 10 }}
            />
          )}
        </ScrollView>

        <TextInput
          style={styles.promptInput}
          placeholder="¿Qué deseas preguntar?"
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
      </View>
    </KeyboardAvoidingView>
  );
};

export default ChatScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fdfdfd",
  },
  headerContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
  },
  header: {
    fontSize: 22,
    fontWeight: "bold",
  },
  modeToggle: {
    flexDirection: "row",
    alignItems: "center",
  },
  modeText: {
    marginRight: 8,
    fontSize: 14,
    fontWeight: "500",
  },
  tokenContainer: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  tokenLabel: {
    marginRight: 8,
    fontWeight: "600",
  },
  tokenInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 6,
    padding: 8,
  },
  history: {
    flex: 1,
    paddingHorizontal: 16,
  },
  promptInput: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 10,
    minHeight: 60,
    margin: 16,
    textAlignVertical: "top",
  },
  sendButton: {
    marginHorizontal: 16,
    marginBottom: 16,
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  sendButtonText: {
    color: "#fff",
    fontWeight: "600",
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
