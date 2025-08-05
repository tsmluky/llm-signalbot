import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Switch,
  ActivityIndicator,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  FlatList,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { getLLMResponse } from "../services/llmService";
import DropdownTokenSelector from "../components/DropdownTokenSelector";
import MessageBubble from "../components/MessageBubble";
import MarkdownCard from "../components/MarkdownCard";
import SignalCard from "../components/SignalCard";
import AnalysisActions from "../components/AnalysisActions";

const MAX_MESSAGES = 50;
const AVAILABLE_TOKENS = ["BTC", "ETH", "SOL", "MATIC", "ADA", "BNB"];

const parseSignal = (raw) => {
  const extract = (label) => {
    const match = raw?.match(new RegExp(`\\[${label}\\]:\\s*(.+)`));
    return match ? match[1].trim() : "N/A";
  };

  return {
    price: extract("PRICE"),
    action: extract("ACTION"),
    confidence: extract("CONFIDENCE"),
    risk: extract("RISK"),
    timeframe: extract("TIMEFRAME"),
  };
};

const ChatScreen = () => {
  const [token, setToken] = useState(null);
  const [isProMode, setIsProMode] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);

  const flatListRef = useRef();
  const mode = isProMode ? "pro" : "lite";
  const STORAGE_KEY = `chat_history_${token?.toUpperCase()}`;

  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const savedToken = await AsyncStorage.getItem("favorite_token");
        const savedMode = await AsyncStorage.getItem("default_mode");
        setToken(savedToken || null);
        setIsProMode(savedMode === "pro");
      } catch (e) {
        console.warn("❌ Error cargando preferencias:", e);
      } finally {
        setInitializing(false);
      }
    };
    loadPreferences();
  }, []);

  useEffect(() => {
    if (!token || initializing) return;
    const loadHistory = async () => {
      try {
        const saved = await AsyncStorage.getItem(STORAGE_KEY);
        setHistory(saved ? JSON.parse(saved) : []);
      } catch (e) {
        console.warn("❌ Error cargando historial:", e);
      }
    };
    loadHistory();
  }, [token]);

  useEffect(() => {
    flatListRef.current?.scrollToEnd({ animated: true });
  }, [history]);

  const saveHistory = async (data) => {
    try {
      const sliced = data.slice(-MAX_MESSAGES);
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(sliced));
    } catch (e) {
      console.warn("❌ Error guardando historial:", e);
    }
  };

  const handleSend = async () => {
    if (!prompt.trim() || !token?.trim()) return;

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
      const res = await getLLMResponse(prompt, token, mode);
      console.log("📨 RESPUESTA RAW:", res);
      console.log("📨 ANALYSIS:", res.analysis);

      const analysis = res.analysis || "❌ No se pudo generar el análisis.";

      let botMessage = {
        sender: "bot",
        text: analysis,
        mode,
        price: res.price || null,
        timestamp: new Date().toISOString(),
      };

      // Si es modo LITE, parseamos la señal y la pasamos como señal estructurada
      if (mode === "lite") {
        const parsed = parseSignal(analysis);
        botMessage = {
          ...botMessage,
          ...parsed,
          token,
        };
      }

      const finalHistory = [...updatedHistory, botMessage];
      setHistory(finalHistory);
      await saveHistory(finalHistory);
    } catch (err) {
      console.warn("❌ Error al generar respuesta:", err);
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

  const renderItem = ({ item }) => {
    const isUser = item.sender === "user";
    const isBot = item.sender === "bot";
    const isLite = item.mode === "lite";
    const isPro = item.mode === "pro";

    return (
      <View style={{ marginVertical: 4, marginHorizontal: 12 }}>
        {isUser && (
          <MessageBubble sender="user" mode={item.mode} text={item.text} />
        )}

        {isBot && isPro && (
          <>
            <MarkdownCard
              content={(item.text || "")
                .replace("#ANALYSIS_START", "")
                .replace("#ANALYSIS_END", "")
                .trim()}
              timestamp={item.timestamp}
              price={item.price}
            />
            <AnalysisActions content={item.text || ""} />
          </>
        )}

        {isBot && isLite && (
          <SignalCard
            signal={{
              token: item.token,
              timestamp: item.timestamp,
              price: item.price,
              action: item.action,
              confidence: item.confidence,
              risk: item.risk,
              timeframe: item.timeframe,
            }}
          />
        )}
      </View>
    );
  };

  if (initializing) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007aff" />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={100}
    >
      <View style={{ flex: 1 }}>
        <View style={styles.headerContainer}>
          <Text style={styles.header}>LLM SignalBot</Text>
          <View
            style={[
              styles.modeToggle,
              { backgroundColor: isProMode ? "#007aff22" : "#ccc3" },
            ]}
          >
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

        <DropdownTokenSelector
          token={token}
          setToken={setToken}
          tokens={AVAILABLE_TOKENS}
        />

        <FlatList
          ref={flatListRef}
          data={history}
          keyExtractor={(item, index) => index.toString()}
          renderItem={renderItem}
          keyboardShouldPersistTaps="handled"
          onContentSizeChange={() =>
            flatListRef.current?.scrollToEnd({ animated: true })
          }
        />

        {loading && (
          <ActivityIndicator
            size="small"
            color="#007aff"
            style={{ marginTop: 10 }}
          />
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={[
              styles.promptInput,
              { backgroundColor: token ? "#fff" : "#eee" },
            ]}
            placeholder={
              token
                ? "¿Qué deseas preguntar?"
                : "Selecciona un token para comenzar"
            }
            value={prompt}
            onChangeText={setPrompt}
            editable={!!token}
            multiline
            onFocus={() => flatListRef.current?.scrollToEnd({ animated: true })}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              {
                backgroundColor:
                  loading || !prompt.trim() || !token ? "#ccc" : "#007aff",
              },
            ]}
            onPress={handleSend}
            disabled={loading || !prompt.trim() || !token}
          >
            <Text style={styles.sendButtonText}>
              {loading ? "..." : "➤"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

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
    padding: 6,
    paddingRight: 10,
    borderRadius: 10,
  },
  modeText: {
    marginRight: 8,
    fontSize: 14,
    fontWeight: "500",
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    padding: 10,
    paddingHorizontal: 16,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderColor: "#eee",
  },
  promptInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 8,
    padding: 10,
    maxHeight: 100,
    textAlignVertical: "top",
  },
  sendButton: {
    marginLeft: 10,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  sendButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
});

export default ChatScreen;
