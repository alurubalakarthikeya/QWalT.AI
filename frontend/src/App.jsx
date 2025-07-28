import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

const popularQuestions = [
  { text: 'Whats 7QC?' },
  { text: 'Quality improvement?' },
  { text: 'Whats Six Sigma' },
  { text: 'What can you do?' }
];

export default function App() {
  const [messages, setMessages] = useState([
    { from: 'bot', text: "Hey! I'm QWalT. What do you want to know?" }
  ]);
  const [input, setInput] = useState('');
  const [isBotTyping, setIsBotTyping] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isBotTyping]);

  const sendMessage = (msg = input) => {
    if (!msg.trim()) return;

    setMessages(prev => [...prev, { from: 'user', text: msg }]);
    setIsBotTyping(true);
    setInput('');

    setTimeout(() => {
      setIsBotTyping(false);
      setMessages(prev => [
        ...prev,
        {
          from: 'bot',
          text: `You asked: "${msg}"\n\nSorry, I'm currently offline. Try again later.`
        }
      ]);
    }, 1500);
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <h1 className="title"><i className="fa-solid fa-robot"></i> QWalT</h1>
        <button className="mode">Friendly</button>
      </div>

      <div className="chat-body">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.from}`}>
            <div>
              {msg.text}
              {msg.from === 'bot' && (
                <div className="popular-questions">
                  <h3>💡 Popular Questions:</h3>
                  <div className="question-buttons">
                    {popularQuestions.map((q, i) => (
                      <button key={i} onClick={() => sendMessage(q.text)}>
                        {q.text}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isBotTyping && (
          <div className="chat-message bot typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}

        {/* Scroll Anchor */}
        <div ref={chatEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          placeholder="Ask something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
        <button onClick={() => sendMessage()}>Send</button>
      </div>
    </div>
  );
}
