import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  ScrollView,
  StyleSheet,
  Switch,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import Markdown from "react-native-markdown-display";
import { getLLMResponse } from "../services/llmService";

const ChatScreen = ({ route }) => {
  const initialToken = route?.params?.token || "BTC";
  const [token, setToken] = useState(initialToken);
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isProMode, setIsProMode] = useState(false);

  const scrollRef = useRef();
  const mode = isProMode ? "pro" : "lite";

  const handleSend = async () => {
    if (!prompt.trim() || !token.trim()) return;

    const newUserMessage = { sender: "user", text: prompt };
    setHistory((prev) => [...prev, newUserMessage]);
    setPrompt("");
    setLoading(true);

    try {
      const response = await getLLMResponse(prompt, token, mode);
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

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollToEnd({ animated: true });
    }
  }, [history]);

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Text style={styles.header}>LLM SignalBot</Text>
        <View style={styles.modeToggle}>
          <Text style={styles.modeText}>
            {isProMode ? "PRO" : "LITE"} Mode
          </Text>
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
            {msg.sender === "user" ? (
              <Text style={styles.userText}>Tú: {msg.text}</Text>
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
  );
};

export default ChatScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#fdfdfd",
  },
  headerContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
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
    marginBottom: 10,
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
  history: {
    flex: 1,
    marginTop: 10,
  },
  messageBubble: {
    padding: 10,
    marginVertical: 4,
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
