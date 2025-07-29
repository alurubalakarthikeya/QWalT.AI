import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";
import "@fortawesome/fontawesome-free/css/all.min.css";

const popularQuestions = [
    { text: "What’s 7QC?" },
    { text: "Quality upscale?" },
    { text: "What’s Six Sigma?" },
    { text: "What can you do?" },
];

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
    const [backToTop, setBackToTop] = useState(false); // ← New toggle state

    const chatEndRef = useRef(null);
    const chatBodyRef = useRef(null); // ← New ref

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
            // At bottom → scroll to top
            scrollToTop();
            setBackToTop(true);
        } else if (el.scrollTop <= 10) {
            // At top → scroll to bottom
            scrollToBottom();
            setBackToTop(false);
        } else {
            // In middle → scroll based on toggle state
            backToTop ? scrollToBottom() : scrollToTop();
            setBackToTop(!backToTop);
        }
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isBotTyping]);

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

            axios
                .post("http://localhost:8000/upload", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                    onUploadProgress: (progressEvent) => {
                        const percent = Math.round(
                            (progressEvent.loaded * 100) / progressEvent.total
                        );
                        setUploadedFiles((prev) =>
                            prev.map((f, idx) =>
                                idx === currentIndex
                                    ? { ...f, progress: percent }
                                    : f
                            )
                        );
                    },
                })
                .then((res) => {
                    const data = res.data;
                    setUploadedFiles((prev) =>
                        prev.map((f, idx) =>
                            idx === currentIndex
                                ? { ...f, progress: 100, status: "done" }
                                : f
                        )
                    );
                    setMessages((prev) => [
                        ...prev,
                        {
                            from: "bot",
                            text: `📄 ${data.filename} uploaded and ready for questions.`,
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
                            text: `❌ Upload failed for ${file.name}`,
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
        if (uploadedFiles.length) {
            formData.append(
                "file_name",
                uploadedFiles[uploadedFiles.length - 1].name
            );
        }

        try {
            const res = await fetch("http://localhost:8000/query", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();
            console.log(">> /query response:", data);

            const botResponse =
                data.result ||
                data.error ||
                "⚠️ AI didn’t reply. Check backend logs.";
            setMessages((prev) => [
                ...prev,
                { from: "bot", text: botResponse },
            ]);
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
            <div>
                {msg.text}
                <div className="popular-questions">
                    <h3>Popular Questions:</h3>
                    <div className="question-buttons">
                        {popularQuestions.map((q, i) => (
                            <button key={i} onClick={() => sendMessage(q.text)}>
                                {q.text}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="chat-wrapper">
            <div className="chat-header">
                <h1 className="title">
                    <i className="fa-solid fa-robot"></i> QWalT
                </h1>
                <button className="mode">Friendly</button>
            </div>

            {/* Back to Top/Bottom Button */}
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

            {showModal && (
                <div
                    className="modal-overlay"
                    onClick={() => setShowModal(false)}
                >
                    <div
                        className="upload-modal new-upload-layout"
                        onClick={(e) => e.stopPropagation()}
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) => {
                            e.preventDefault();
                            if (e.dataTransfer.files.length > 0) {
                                handleFileUpload({
                                    target: { files: e.dataTransfer.files },
                                });
                            }
                        }}
                    >
                        <button
                            className="modal-close-btn"
                            onClick={() => setShowModal(false)}
                        >
                            &times;
                        </button>

                        <div className="modal-content-wrapper">
                            <div className="drop-zone">
                                <img className="upload-img" src="./src/assets/download.png" alt="upload files here" />
                                <p>Drag & drop files here</p>
                                <p>or</p>
                                <label
                                    htmlFor="hiddenFileInput"
                                    className="custom-file-btn"
                                >
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

                            <div className="file-list">
                                {uploadedFiles.map((f, idx) => (
                                    <div className="file-item" key={idx}>
                                        <div className="file-icon">
                                            <i className="fa-solid fa-file-lines"></i>
                                        </div>
                                        <div className="file-info">
                                            <div className="file-name">
                                                {f.name}
                                            </div>
                                            <div className="progress-bar">
                                                <div
                                                    className="progress-fill"
                                                    style={{
                                                        width: `${f.progress}%`,
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                        <div className="file-percent">
                                            {f.progress}%
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
