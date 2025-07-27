import React, { useState } from 'react';
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
  const sendMessage = (msg = input) => {
    if (!msg.trim()) return;
    setMessages(prev => [...prev, { from: 'user', text: msg }]);
    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        { from: 'bot', text: `You asked: "${msg}"\n\nSorry, I'm currently offline. Try again later.` }
      ]);
    }, 500);

    setInput('');
  };
  

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <h1 className="title"><i className="fa-solid fa-robot"></i> QWalT</h1>
        <i className="fa-solid fa-bars"></i>
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
