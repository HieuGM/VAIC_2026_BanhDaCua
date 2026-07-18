// components/chat/ChatSidebar.jsx
import React from 'react';
import { FaCommentMedical, FaPlus, FaComment, FaTrash, FaTimes } from 'react-icons/fa';

const formatTime = (isoString) => {
  const d = new Date(isoString);
  const now = new Date();
  const diff = now - d;
  if (diff < 60000) return 'Vừa xong';
  if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
  return d.toLocaleDateString('vi-VN');
};

const ChatSidebar = ({
  conversations,
  activeId,
  onNew,
  onSelect,
  onDelete,
  onClearAll,
}) => {
  return (
    <div className="chat-sidebar">
      {/* Header */}
      <div className="chat-sidebar__header">
        <div className="chat-sidebar__title">
          <FaCommentMedical className="chat-sidebar__title-icon" />
          Lịch sử chat
        </div>
        <button
          className="chat-sidebar__new-btn"
          onClick={onNew}
          title="Cuộc trò chuyện mới"
        >
          <FaPlus />
        </button>
      </div>

      {/* Conversation List */}
      <div className="chat-sidebar__list">
        {conversations.length === 0 ? (
          <div className="chat-sidebar__empty">
            <span className="chat-sidebar__empty-icon">💬</span>
            Chưa có cuộc trò chuyện nào. Hãy bắt đầu!
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`chat-conv-item ${activeId === conv.id ? 'chat-conv-item--active' : ''}`}
              onClick={() => onSelect(conv.id)}
            >
              <FaComment className="chat-conv-item__icon" />
              <div className="chat-conv-item__info">
                <div className="chat-conv-item__title">{conv.title}</div>
                <div className="chat-conv-item__meta">
                  {conv.messages.length} tin • {formatTime(conv.updatedAt)}
                </div>
              </div>
              <button
                className="chat-conv-item__del"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(conv.id);
                }}
                title="Xóa"
              >
                <FaTimes />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      {conversations.length > 0 && (
        <div className="chat-sidebar__footer">
          <button className="chat-sidebar__clear-btn" onClick={onClearAll}>
            <FaTrash />
            Xóa tất cả lịch sử
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatSidebar;
