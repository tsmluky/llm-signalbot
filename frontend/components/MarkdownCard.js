// components/MarkdownCard.js
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Markdown from 'react-native-markdown-display';

const MarkdownCard = ({ content, timestamp }) => {
  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

  return (
    <View style={styles.card}>
      {formattedTime && (
        <Text style={styles.timestamp}>📅 {formattedTime}</Text>
      )}
      <Markdown style={markdownStyles}>
        {content || ""}
      </Markdown>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fffef5',
    borderRadius: 16,
    padding: 16,
    marginVertical: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 1,
  },
  timestamp: {
    fontSize: 12,
    color: '#777',
    marginBottom: 10,
    textAlign: 'right',
    fontStyle: 'italic',
  },
});

const markdownStyles = {
  body: {
    fontSize: 14,
    lineHeight: 20,
    color: '#222',
  },
  heading1: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007aff',
    marginBottom: 8,
  },
  heading2: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007aff',
    marginVertical: 6,
  },
  paragraph: {
    marginVertical: 4,
  },
  list_item: {
    flexDirection: 'row',
    justifyContent: 'flex-start',
    alignItems: 'flex-start',
    marginVertical: 2,
  },
  bullet_list_icon: {
    color: '#666',
    marginRight: 6,
  },
  strong: {
    fontWeight: 'bold',
    color: '#000',
  },
  code_block: {
    backgroundColor: '#f6f8fa',
    padding: 10,
    borderRadius: 6,
    fontFamily: 'monospace',
  },
};

export default MarkdownCard;
