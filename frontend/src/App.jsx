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
    const [uploadedFileName, setUploadedFileName] = useState("");
    const [showModal, setShowModal] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const chatEndRef = useRef(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isBotTyping]);

    useEffect(() => {
        if (uploadProgress === 100) {
            const timeout = setTimeout(() => setShowModal(false), 1500);
            return () => clearTimeout(timeout);
        }
    }, [uploadProgress]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post(
                "http://localhost:8000/upload",
                formData,
                {
                    headers: { "Content-Type": "multipart/form-data" },
                    onUploadProgress: (progressEvent) => {
                        const percent = Math.round(
                            (progressEvent.loaded * 100) / progressEvent.total
                        );
                        setUploadProgress(percent);
                    },
                }
            );

            const data = res.data;
            setUploadedFileName(data.filename);
            setMessages((prev) => [
                ...prev,
                {
                    from: "bot",
                    text: `📄 ${data.filename} uploaded and ready for questions.`,
                },
            ]);
            setUploadProgress(0);
        } catch (err) {
            console.error("Upload failed:", err);
            setMessages((prev) => [
                ...prev,
                { from: "bot", text: "❌ File upload failed." },
            ]);
            setShowModal(false);
            setUploadProgress(0);
        }
    };

    const sendMessage = async (msg = input) => {
        if (!msg.trim()) return;
        setMessages((prev) => [...prev, { from: "user", text: msg }]);
        setInput("");
        setIsBotTyping(true);

        const formData = new FormData();
        formData.append("query", msg);
        formData.append("file_name", uploadedFileName);

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

            <div className="chat-body">
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
                        setShowModal(true);
                        setUploadProgress(0);
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
                        className="upload-modal"
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
                        <h2>Upload File</h2>

                        <div className="drag-drop-zone">
                            <p>Drag & drop a file here</p>
                            <p>or</p>
                            <label
                                htmlFor="hiddenFileInput"
                                className="custom-file-btn"
                            >
                                Choose File
                            </label>
                            <input
                                id="hiddenFileInput"
                                type="file"
                                accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg,.gif,.webp"
                                onChange={handleFileUpload}
                            />
                        </div>

                        {uploadProgress > 0 && (
                            <div className="concentric-loader">
                                <div className="circle-ring ring1"></div>
                                <div className="circle-ring ring2"></div>
                                <div className="circle-ring ring3"></div>
                                <div className="percent-text">
                                    {uploadProgress}%
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
