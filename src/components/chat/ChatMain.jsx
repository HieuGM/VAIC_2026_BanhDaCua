// components/chat/ChatMain.jsx
// Phần chat chính: header + messages + input

import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  FaRobot,
  FaPaperPlane,
  FaExpand,
  FaCompress,
} from 'react-icons/fa';
import ChatMessage from './ChatMessage';

const SUGGESTIONS = [
  { emoji: '📅', text: 'Đặt lịch khám như thế nào?' },
  { emoji: '📍', text: 'Địa chỉ bệnh viện ở đâu?' },
  { emoji: '💳', text: 'Thanh toán bảo hiểm y tế?' },
  { emoji: '⏰', text: 'Giờ làm việc của bệnh viện?' },
];

const TypingIndicator = () => (
  <div className="chat-typing">
    <div className="chat-typing__avatar">
      <FaRobot />
    </div>
    <div className="chat-typing__bubble">
      <div className="chat-typing__dot" />
      <div className="chat-typing__dot" />
      <div className="chat-typing__dot" />
    </div>
  </div>
);

const ChatMain = ({
  conversation,
  isLoading,
  onSend,
  isMaximized,
  onToggleMaximize,
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll khi có tin nhắn mới
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages, isLoading]);

  // Auto-resize textarea
  const adjustTextarea = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
  }, []);

  useEffect(() => {
    adjustTextarea();
  }, [inputValue, adjustTextarea]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    onSend(inputValue);
    setInputValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestion = (text) => {
    onSend(text);
  };

  const messages = conversation?.messages || [];
  const showWelcome = messages.length === 0;

  return (
    <div className="chat-main">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header__info">
          <div className="chat-header__avatar">
            <FaRobot />
          </div>
          <div className="chat-header__text">
            <h4>Trợ lý AI Bệnh viện Tim Hà Nội</h4>
            <p>
              <span className="chat-header__online" />
              Sẵn sàng hỗ trợ 24/7
            </p>
          </div>
        </div>
        <div className="chat-header__actions">
          <button
            className="chat-header__action-btn"
            onClick={onToggleMaximize}
            title={isMaximized ? "Thu nhỏ" : "Phóng to"}
          >
            {isMaximized ? <FaCompress /> : <FaExpand />}
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {showWelcome ? (
          <div className="chat-welcome">
            <div className="chat-welcome__icon">
              <FaRobot />
            </div>
            <h3>Xin chào! Tôi có thể giúp gì cho bạn?</h3>
            <p>
              Tôi là trợ lý AI của Bệnh viện Tim Hà Nội, sẵn sàng hỗ trợ bạn về thông tin khám bệnh, đặt lịch và các dịch vụ y tế.
            </p>
            <div className="chat-welcome__suggestions">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.text}
                  className="chat-welcome__suggestion-btn"
                  onClick={() => handleSuggestion(s.text)}
                >
                  <span>{s.emoji}</span>
                  <span>{s.text}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <div className="chat-input-area__hint">
          ↵ Enter để gửi &nbsp;•&nbsp; Shift+Enter xuống dòng
        </div>
        <form className="chat-input-form" onSubmit={handleSubmit}>
          <div className="chat-input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-input"
              placeholder="Nhập câu hỏi của bạn..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isLoading}
            />
          </div>
          <button
            className="chat-send-btn"
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            title="Gửi"
          >
            <FaPaperPlane />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatMain;
