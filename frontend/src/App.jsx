import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

const popularQuestions = [
  { text: 'What’s 7QC?' },
  { text: 'Quality upscale?' },
  { text: 'What’s Six Sigma?' },
  { text: 'What can you do?' },
];

export default function App() {
  const [messages, setMessages] = useState([
    {
      from: 'bot',
      text: "Hey! I'm QWalT — your Quality Wizard AI. Ask me anything about quality improvement, Six Sigma, or process excellence!"
    }
  ]);
  const [input, setInput] = useState('');
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isBotTyping]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setUploadedFileName(data.filename);
      setMessages(prev => [...prev, { from: 'bot', text: `📄 ${data.filename} uploaded and ready for questions.` }]);
    } catch (err) {
      console.error("Upload failed:", err);
      setMessages(prev => [...prev, { from: 'bot', text: "❌ File upload failed." }]);
    }
  };

  const sendMessage = async (msg = input) => {
    if (!msg.trim()) return;
    setMessages(prev => [...prev, { from: 'user', text: msg }]);
    setInput('');
    setIsBotTyping(true);

    const formData = new FormData();
    formData.append("query", msg);
    formData.append("file_name", uploadedFileName);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      console.log(">> /query response:", data);

      const botResponse = data.result || data.error || "⚠️ AI didn’t reply. Check backend logs.";
      setMessages(prev => [...prev, { from: 'bot', text: botResponse }]);
    } catch (err) {
      console.error("Fetch failed:", err);
      setMessages(prev => [...prev, {
        from: 'bot',
        text: `You asked: "${msg}"

🚫 Server is unreachable.`
      }]);
    } finally {
      setIsBotTyping(false);
    }
  };

  const renderBotMessage = (msg, idx) => (
    <div key={idx} className="chat-message bot">
      <div>
        {msg.text}
        <div className="popular-questions">
          <h3>Popular Questions:</h3>
          <div className="question-buttons">
            {popularQuestions.map((q, i) => (
              <button key={i} onClick={() => sendMessage(q.text)}>{q.text}</button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <h1 className="title"><i className="fa-solid fa-robot"></i> QWalT</h1>
        <button className="mode">Friendly</button>
      </div>

      <div className="chat-body">
        {messages.map((msg, idx) =>
          msg.from === 'bot'
            ? renderBotMessage(msg, idx)
            : <div key={idx} className="chat-message user"><div>{msg.text}</div></div>
        )}

        {isBotTyping && (
          <div className="chat-message bot typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}
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

        <label htmlFor="fileInput" className="file-upload-btn">
          <i className="fa-solid fa-paperclip"></i>
        </label>
        <input
          type="file"
          accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg,.gif,.webp"
          style={{ display: 'none' }}
          id="fileInput"
          onChange={handleFileUpload}
        />

        <button onClick={() => sendMessage()}>Send</button>
      </div>
    </div>
  );
}