// frontend/components/MarkdownCard.js
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import Markdown from "react-native-markdown-display";

const MarkdownCard = ({ content, timestamp, price }) => {
  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleString("es-ES", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  const safeContent = content?.trim() || "*⚠️ No se pudo generar contenido.*";

  return (
    <View style={styles.card}>
      {formattedTime && (
        <Text style={styles.timestamp}>
          🗓️ <Text style={{ fontStyle: "italic" }}>{formattedTime}</Text>
        </Text>
      )}
      {price && (
        <Text style={styles.price}>
          💰 <Text style={{ fontWeight: "bold" }}>Precio actual:</Text>{" "}
          ${parseFloat(price).toFixed(2)}
        </Text>
      )}
      <Markdown style={markdownStyles}>{safeContent}</Markdown>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#fefefe",
    borderRadius: 16,
    padding: 18,
    marginVertical: 6,
    borderWidth: 1,
    borderColor: "#eee",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  timestamp: {
    fontSize: 12,
    color: "#888",
    marginBottom: 4,
    textAlign: "right",
  },
  price: {
    fontSize: 14,
    color: "#333",
    marginBottom: 10,
    textAlign: "right",
  },
});

const markdownStyles = {
  body: {
    fontSize: 14,
    lineHeight: 22,
    color: "#222",
  },
  heading1: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#005bbb",
    marginBottom: 10,
    marginTop: 16,
    borderBottomWidth: 1,
    borderColor: "#ddd",
    paddingBottom: 4,
  },
  heading2: {
    fontSize: 17,
    fontWeight: "600",
    color: "#007aff",
    marginTop: 12,
    marginBottom: 6,
  },
  paragraph: {
    marginVertical: 4,
  },
  list_item: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginVertical: 2,
  },
  bullet_list_icon: {
    color: "#666",
    marginRight: 8,
  },
  strong: {
    fontWeight: "bold",
    color: "#000",
  },
  code_block: {
    backgroundColor: "#f6f8fa",
    padding: 12,
    borderRadius: 6,
    fontFamily: "monospace",
    color: "#444",
  },
  blockquote: {
    backgroundColor: "#f4f4f4",
    padding: 10,
    borderLeftWidth: 4,
    borderColor: "#ccc",
    marginVertical: 8,
  },
};

export default MarkdownCard;
