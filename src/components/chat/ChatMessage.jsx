// components/chat/ChatMessage.jsx
import React from 'react';
import { FaRobot, FaUser } from 'react-icons/fa';

/**
 * Render nội dung markdown đơn giản:
 * **bold**, *italic*, bullet lists (•), xuống dòng (\n)
 */
const renderContent = (content) => {
  // Tách theo dòng
  const lines = content.split('\n');

  return lines.map((line, i) => {
    // Parse inline: **bold** và *italic*
    const parts = [];
    let remaining = line;
    let key = 0;

    while (remaining.length > 0) {
      const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
      const italicMatch = remaining.match(/\*(.+?)\*/);

      let nextBold = boldMatch ? remaining.indexOf('**') : Infinity;
      let nextItalic = italicMatch ? remaining.indexOf('*') : Infinity;

      if (boldMatch && nextBold <= nextItalic) {
        if (nextBold > 0) {
          parts.push(<span key={key++}>{remaining.slice(0, nextBold)}</span>);
        }
        parts.push(<strong key={key++}>{boldMatch[1]}</strong>);
        remaining = remaining.slice(nextBold + boldMatch[0].length);
      } else if (italicMatch && nextItalic < Infinity) {
        if (nextItalic > 0) {
          parts.push(<span key={key++}>{remaining.slice(0, nextItalic)}</span>);
        }
        parts.push(<em key={key++}>{italicMatch[1]}</em>);
        remaining = remaining.slice(nextItalic + italicMatch[0].length);
      } else {
        parts.push(<span key={key++}>{remaining}</span>);
        break;
      }
    }

    return (
      <React.Fragment key={i}>
        {parts}
        {i < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
};

const formatTime = (isoString) => {
  const d = new Date(isoString);
  return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
};

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message chat-message--${message.role}`}>
      <div className="chat-message__avatar">
        {isUser ? <FaUser /> : <FaRobot />}
      </div>
      <div className="chat-message__body">
        <div className="chat-message__bubble">
          {renderContent(message.content)}
        </div>
        <div className="chat-message__time">{formatTime(message.timestamp)}</div>
      </div>
    </div>
  );
};

export default ChatMessage;
