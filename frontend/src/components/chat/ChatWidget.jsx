// components/chat/ChatWidget.jsx
// Component gốc: FAB button + Chat window tổng hợp

import React, { useState, useEffect, useRef } from 'react';
import { FaCommentDots, FaTimes } from 'react-icons/fa';
import { useChat } from '../../hooks/useChat';
import ChatSidebar from './ChatSidebar';
import ChatMain from './ChatMain';
import './Chat.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [showLabel, setShowLabel] = useState(true);
  const windowRef = useRef(null);

  const {
    conversations,
    activeConversation,
    activeId,
    isLoading,
    createNewConversation,
    selectConversation,
    deleteConversation,
    clearAllConversations,
    sendMessage,
  } = useChat();

  // Ẩn label sau 4 giây
  useEffect(() => {
    const timer = setTimeout(() => setShowLabel(false), 4000);
    return () => clearTimeout(timer);
  }, []);

  // Click outside để đóng
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (isOpen && windowRef.current && !windowRef.current.contains(e.target)) {
        const fabBtn = document.getElementById('chat-fab-btn');
        if (fabBtn && !fabBtn.contains(e.target)) {
          setIsOpen(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const toggleOpen = () => {
    setIsOpen((prev) => !prev);
    setShowLabel(false);
    if (isOpen) {
      setIsMaximized(false); // Reset size when closing
    }
  };

  const handleNewConversation = () => {
    createNewConversation();
  };

  const handleSendMessage = async (content) => {
    await sendMessage(content);
  };

  const handleClearAll = () => {
    if (window.confirm('Bạn có chắc muốn xóa toàn bộ lịch sử trò chuyện?')) {
      clearAllConversations();
    }
  };

  const toggleMaximize = () => {
    setIsMaximized((prev) => !prev);
  };

  return (
    <>
      {/* Chat Window */}
      {isOpen && (
        <div className={`chat-window ${isMaximized ? 'chat-window--maximized' : ''}`} ref={windowRef}>
          <ChatSidebar
            conversations={conversations}
            activeId={activeId}
            onNew={handleNewConversation}
            onSelect={selectConversation}
            onDelete={deleteConversation}
            onClearAll={handleClearAll}
          />
          <ChatMain
            conversation={activeConversation}
            isLoading={isLoading}
            onSend={handleSendMessage}
            isMaximized={isMaximized}
            onToggleMaximize={toggleMaximize}
          />
        </div>
      )}

      {/* FAB Button */}
      <div className="chat-fab">
        {showLabel && !isOpen && (
          <div className="chat-fab__label">Hỏi trợ lý AI 🏥</div>
        )}
        <button
          id="chat-fab-btn"
          className={`chat-fab__btn ${isOpen ? 'chat-fab__btn--open' : ''}`}
          onClick={toggleOpen}
          aria-label={isOpen ? 'Đóng chat' : 'Mở chat'}
        >
          {!isOpen && <span className="chat-fab__pulse" />}
          {isOpen ? (
            <FaTimes className="chat-fab__icon" />
          ) : (
            <FaCommentDots className="chat-fab__icon" />
          )}
        </button>
      </div>
    </>
  );
};

export default ChatWidget;
