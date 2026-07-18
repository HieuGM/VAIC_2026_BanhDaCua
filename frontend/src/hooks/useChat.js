// hooks/useChat.js
// Custom hook quản lý toàn bộ state của chatbot

import { useState, useCallback, useEffect } from 'react';
import { createConversation, createMessage } from '../types/chat';
import { chatStorage } from '../services/chatStorage';
import { sendMessageToAI } from '../services/chatAI';

export const useChat = () => {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // --- Khởi tạo từ localStorage ---
  useEffect(() => {
    const saved = chatStorage.getAll();
    const savedActiveId = chatStorage.getActiveId();
    if (saved.length > 0) {
      setConversations(saved);
      setActiveId(savedActiveId || saved[0].id);
    }
  }, []);

  // --- Sync conversations xuống localStorage ---
  useEffect(() => {
    if (conversations.length > 0) {
      chatStorage.saveAll(conversations);
    }
  }, [conversations]);

  // --- Sync activeId xuống localStorage ---
  useEffect(() => {
    chatStorage.saveActiveId(activeId);
  }, [activeId]);

  /** Conversation đang được chọn */
  const activeConversation = conversations.find((c) => c.id === activeId) || null;

  /** Tạo conversation mới */
  const createNewConversation = useCallback(() => {
    const conv = createConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveId(conv.id);
    return conv;
  }, []);

  /** Chọn conversation */
  const selectConversation = useCallback((id) => {
    setActiveId(id);
  }, []);

  /** Xóa conversation */
  const deleteConversation = useCallback(
    (id) => {
      setConversations((prev) => {
        const next = prev.filter((c) => c.id !== id);
        // Nếu xóa conversation đang active, chọn cái đầu tiên
        if (id === activeId) {
          setActiveId(next.length > 0 ? next[0].id : null);
        }
        if (next.length === 0) {
          chatStorage.clearAll();
        }
        return next;
      });
    },
    [activeId]
  );

  /** Xóa toàn bộ lịch sử */
  const clearAllConversations = useCallback(() => {
    chatStorage.clearAll();
    setConversations([]);
    setActiveId(null);
  }, []);

  /** Gửi tin nhắn */
  const sendMessage = useCallback(
    async (content) => {
      if (!content.trim() || isLoading) return;

      // Nếu chưa có conversation nào, tạo mới
      let currentId = activeId;
      let isNew = false;
      if (!currentId) {
        const conv = createConversation();
        setConversations((prev) => [conv, ...prev]);
        setActiveId(conv.id);
        currentId = conv.id;
        isNew = true;
      }

      const userMsg = createMessage('user', content.trim());

      // Cập nhật tên cuộc trò chuyện từ tin nhắn đầu tiên
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== currentId) return c;
          const isFirstMsg = c.messages.length === 0;
          return {
            ...c,
            title: isFirstMsg ? content.trim().slice(0, 50) : c.title,
            messages: [...c.messages, userMsg],
            updatedAt: new Date().toISOString(),
          };
        })
      );

      setIsLoading(true);

      try {
        const aiReply = await sendMessageToAI(content);
        const assistantMsg = createMessage('assistant', aiReply);

        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== currentId) return c;
            return {
              ...c,
              messages: [...c.messages, assistantMsg],
              updatedAt: new Date().toISOString(),
            };
          })
        );
      } catch (err) {
        const errMsg = createMessage(
          'assistant',
          'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau hoặc gọi hotline **1900 1082**.'
        );
        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== currentId) return c;
            return {
              ...c,
              messages: [...c.messages, errMsg],
              updatedAt: new Date().toISOString(),
            };
          })
        );
      } finally {
        setIsLoading(false);
      }
    },
    [activeId, isLoading]
  );

  return {
    conversations,
    activeConversation,
    activeId,
    isLoading,
    createNewConversation,
    selectConversation,
    deleteConversation,
    clearAllConversations,
    sendMessage,
  };
};
