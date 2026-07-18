// types/chat.js
// Data types cho hệ thống chatbot

/**
 * @typedef {Object} Message
 * @property {string} id
 * @property {'user'|'assistant'} role
 * @property {string} content
 * @property {Date} timestamp
 */

/**
 * @typedef {Object} Conversation
 * @property {string} id
 * @property {string} title
 * @property {Date} createdAt
 * @property {Date} updatedAt
 * @property {Message[]} messages
 */

export const createMessage = (role, content) => ({
  id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  role,
  content,
  timestamp: new Date().toISOString(),
});

export const createConversation = () => ({
  id: `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
  title: 'Cuộc trò chuyện mới',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  messages: [],
});
