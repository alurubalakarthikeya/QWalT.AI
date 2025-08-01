import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";
import { getUserId } from './utils';
import "@fortawesome/fontawesome-free/css/all.min.css";
import uploadImg from "./assets/download.png";
import logo from "./assets/logo.png"; // Make sure logo is imported
import ReactMarkdown from "react-markdown";

const API_BASE_URL = 'https://backend-trail-06b6.onrender.com';

export default function App() {
  const [messages, setMessages] = useState([
    {
      from: "bot",
      text: "Hey! I'm QWalT — your Quality Wizard AI. Ask me anything about quality improvement, Six Sigma, or process excellence!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isBotTyping, setIsBotTyping] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [backToTop, setBackToTop] = useState(false);

  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstallBtn, setShowInstallBtn] = useState(false);
  const [botResponseCount, setBotResponseCount] = useState(0);
  const [queryCooldown, setQueryCooldown] = useState(0);
  const [isInstalled, setIsInstalled] = useState(false);

  const chatEndRef = useRef(null);
  const chatBodyRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isBotTyping]);

  useEffect(() => {
    const cooldown = parseInt(localStorage.getItem("queryCooldown")) || 0;
    setQueryCooldown(cooldown);

    if (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    ) {
      setIsInstalled(true);
    }

    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
    });

    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener("beforeinstallprompt", handler);

    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  useEffect(() => {
    localStorage.setItem("queryCooldown", queryCooldown.toString());
  }, [queryCooldown]);

  useEffect(() => {
    const dismissed = localStorage.getItem("installBannerDismissed") === "true";
    if (
      botResponseCount >= 3 &&
      queryCooldown === 0 &&
      deferredPrompt &&
      !dismissed
    ) {
      setShowInstallBtn(true);
    }
  }, [botResponseCount, queryCooldown, deferredPrompt]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToTop = () => {
    chatBodyRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleScrollToggle = () => {
    const el = chatBodyRef.current;
    if (!el) return;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 10) {
      scrollToTop();
      setBackToTop(true);
    } else if (el.scrollTop <= 10) {
      scrollToBottom();
      setBackToTop(false);
    } else {
      backToTop ? scrollToBottom() : scrollToTop();
      setBackToTop(!backToTop);
    }
  };

  const handleInstallClick = () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === "accepted") {
          console.log("User accepted the install prompt");
        } else {
          console.log("User dismissed the install prompt");
        }
        setDeferredPrompt(null);
        setShowInstallBtn(false);
        setQueryCooldown(10);
        localStorage.setItem("queryCooldown", "10");
      });
    }
  };

  const handleCloseBanner = () => {
    setShowInstallBtn(false);
    localStorage.setItem("installBannerDismissed", "true");
    setQueryCooldown(10);
    localStorage.setItem("queryCooldown", "10");
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    const fileObjs = files.map((file) => ({
      name: file.name,
      progress: 0,
      status: "uploading",
    }));
    setUploadedFiles((prev) => [...prev, ...fileObjs]);

    files.forEach((file, i) => {
      const currentIndex = uploadedFiles.length + i;
      const formData = new FormData();
      formData.append("file", file);

      axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadedFiles((prev) =>
            prev.map((f, idx) =>
              idx === currentIndex ? { ...f, progress: percent } : f
            )
          );
        },
      })
      .then((res) => {
        const data = res.data;
        setUploadedFiles((prev) =>
          prev.map((f, idx) =>
            idx === currentIndex ? { ...f, progress: 100, status: "done" } : f
          )
        );

        const suggested = Array.isArray(data.suggested_questions)
          ? data.suggested_questions.map((q) => ({ text: q }))
          : [];

        setMessages((prev) => [
          ...prev,
          {
            from: "bot",
            text: `📄 **${data.filename}** uploaded and ready for questions.`,
            relatedQuestions: suggested,
          },
        ]);
      })
      .catch((err) => {
        console.error("Upload failed:", err);
        setUploadedFiles((prev) =>
          prev.map((f, idx) =>
            idx === currentIndex ? { ...f, status: "error" } : f
          )
        );
        setMessages((prev) => [
          ...prev,
          {
            from: "bot",
            text: `❌ Upload failed for **${file.name}**`,
          },
        ]);
      });
    });
  };

  const sendMessage = async (msg = input) => {
    if (!msg.trim()) return;
    setMessages((prev) => [...prev, { from: "user", text: msg }]);
    setInput("");
    setIsBotTyping(true);

    const formData = new FormData();
    formData.append("query", msg);
    formData.append("user_id", getUserId());
    uploadedFiles.forEach(file => {
      formData.append("file_name", file.name);
    });

    try {
      const res = await fetch(`${API_BASE_URL}/query`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      const botResponse = data.result || data.error || "⚠️ AI didn’t reply. Check backend logs.";

      const suggested = Array.isArray(data.suggested_questions)
        ? data.suggested_questions.map((q) => ({ text: q }))
        : [];

      const quickReplies = Array.isArray(data.suggested_user_replies)
        ? data.suggested_user_replies.map((r) => ({ text: r }))
        : [];

      setMessages((prev) => [
        ...prev,
        {
          from: "bot",
          text: botResponse,
          relatedQuestions: suggested,
          suggestedReplies: quickReplies,
        },
      ]);

      setBotResponseCount((prev) => prev + 1);
      if (queryCooldown > 0) setQueryCooldown(queryCooldown - 1);

    } catch (err) {
      console.error("Fetch failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          from: "bot",
          text: `You asked: "${msg}"\n\n🚫 Server is unreachable.`,
        },
      ]);
    } finally {
      setIsBotTyping(false);
    }
  };

  const renderBotMessage = (msg, idx) => (
    <div key={idx} className="chat-message bot">
      <ReactMarkdown>{msg.text}</ReactMarkdown>
      {msg.relatedQuestions?.length > 0 && (
        <div className="popular-questions">
          <h3>Related Questions:</h3>
          <div className="question-buttons">
            {msg.relatedQuestions.map((q, i) => (
              <button key={i} onClick={() => sendMessage(q.text)}>
                {q.text}
              </button>
            ))}
          </div>
        </div>
      )}
      {msg.suggestedReplies?.length > 0 && (
        <div className="suggested-replies">
          <h4>Quick Replies:</h4>
          <div className="reply-buttons">
            {msg.suggestedReplies.map((r, i) => (
              <button key={i} onClick={() => sendMessage(r.text)}>
                {r.text}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <h1 className="title">
          <i className="fa-solid fa-robot"></i> QWalT
        </h1>
        {isInstalled || (!deferredPrompt && !showInstallBtn) ? (
          <button className="mode">Friendly</button>
        ) : (
          <button className="mode" onClick={handleInstallClick}>
            Install
          </button>
        )}
      </div>

      <button
        className="scroll-toggle-btn"
        onClick={handleScrollToggle}
        title={backToTop ? "Scroll to Bottom" : "Scroll to Top"}
      >
        <i className={`fa-solid ${backToTop ? "fa-arrow-down" : "fa-arrow-up"}`}></i>
      </button>

      <div className="chat-body" ref={chatBodyRef}>
        {messages.map((msg, idx) =>
          msg.from === "bot" ? (
            renderBotMessage(msg, idx)
          ) : (
            <div key={idx} className="chat-message user">
              <div>{msg.text}</div>
            </div>
          )
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
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          className="file-upload-btn"
          onClick={() => {
            setUploadedFiles([]);
            setShowModal(true);
          }}
        >
          <i className="fa-solid fa-paperclip"></i>
        </button>
        <button onClick={() => sendMessage()}>Send</button>
      </div>

      {showInstallBtn && (
        <>
          <div className="blur-backdrop" onClick={handleCloseBanner}></div>
          <div className="install-banner">
            <button className="modal-close-btn" onClick={handleCloseBanner}>✕</button>
            <div className="install-content">
              <div className="install-icon">
                <img className="log-img" src={logo} alt="QWalT.AI Logo" />
              </div>
              <div className="install-text">
                <p>Install <strong>QWalT.AI</strong> App now for a better experience!</p>
                <button className="mode full" onClick={handleInstallClick}>Install</button>
              </div>
            </div>
          </div>
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div
            className="upload-modal new-upload-layout"
            onClick={(e) => e.stopPropagation()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              if (e.dataTransfer.files.length > 0) {
                handleFileUpload({ target: { files: e.dataTransfer.files } });
              }
            }}
          >
            <button className="modal-close-btn" onClick={() => setShowModal(false)}>
              <i className="fa-solid fa-xmark"></i>
            </button>
            <div className={`modal-content-wrapper ${uploadedFiles.length === 0 ? 'compact-modal' : ''}`}>
              <div className="drop-zone">
                <img className="upload-img" src={uploadImg} alt="upload files here" />
                <p>Drag & drop files here</p>
                <p>or</p>
                <label htmlFor="hiddenFileInput" className="custom-file-btn">
                  Choose Files
                </label>
                <input
                  id="hiddenFileInput"
                  type="file"
                  onChange={handleFileUpload}
                  multiple
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.webp"
                />
              </div>
              {uploadedFiles.length > 0 && (
                <div className="file-list">
                  {uploadedFiles.map((f, idx) => (
                    <div className="file-item" key={idx}>
                      <div className="file-icon">
                        <i className="fa-solid fa-file-lines"></i>
                      </div>
                      <div className="file-info">
                        <div className="file-name">{f.name}</div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${f.progress}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="file-percent">{f.progress}%</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
