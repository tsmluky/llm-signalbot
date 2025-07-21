// components/MessageBubble.js
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import Markdown from "react-native-markdown-display";
import SignalCard from "./SignalCard";

const MessageBubble = ({ sender, mode, text }) => {
  const isUser = sender === "user";
  const isSignal =
    typeof text === "string" &&
    text.includes("#SIGNAL_START") &&
    text.includes("#SIGNAL_END");

  const extractTimestamp = (text) => {
    const match = text.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/);
    if (!match) return "";
    const date = new Date(match[0]);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })}`;
  };

  return (
    <View style={[styles.bubble, isUser ? styles.user : styles.bot]}>
      <Text style={styles.meta}>
        {isUser ? "Tú" : "elBot"} | Modo: {mode?.toUpperCase()}
      </Text>

      {isSignal && !isUser ? (
        <SignalCard content={text} timestamp={extractTimestamp(text)} />
      ) : isUser ? (
        <Text style={styles.text}>{text}</Text>
      ) : (
        <Markdown style={markdownStyles}>{text}</Markdown>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  bubble: {
    marginVertical: 6,
    padding: 10,
    borderRadius: 12,
    maxWidth: "90%",
  },
  user: {
    alignSelf: "flex-end",
    backgroundColor: "#e1f5fe",
  },
  bot: {
    alignSelf: "flex-start",
    backgroundColor: "#f0f4c3",
  },
  meta: {
    fontSize: 12,
    color: "#666",
    marginBottom: 4,
    fontStyle: "italic",
  },
  text: {
    color: "#333",
  },
});

const markdownStyles = {
  body: { color: "#333", fontSize: 14 },
  strong: { fontWeight: "bold" },
};

export default MessageBubble;
