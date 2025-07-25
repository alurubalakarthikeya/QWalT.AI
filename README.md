# 🔧 KneadQuality-AI

**Your Intelligent Quality Management Assistant**

A conversational AI system that provides quality management expertise, tool recommendations, and document analysis capabilities. Works completely free with built-in knowledge and optional cloud hosting.

## 🚀 Quick Start

### Option 1: Local Usage
```bash
streamlit run app_cloud.py --server.port 8503
```
Access at: http://localhost:8503

### Option 2: Network Sharing (WiFi)
```bash
start_simple_sharing.bat
```
Share the provided URL with anyone on your network!

### Option 3: Cloud Hosting
Follow `FREE_HOSTING_GUIDE.md` for permanent online deployment.

## 💬 What You Can Ask

- **Conversation**: "Hello!", "How are you?", "What can you do?"
- **Quality Tools**: "What are the 7QC tools?", "Explain Six Sigma"
- **Process Improvement**: "How to reduce defects?", "PDCA cycle guide"
- **General Help**: Any quality management or process questions

## ✨ Features

- 🤖 **Natural Conversation** - Chat naturally about any topic
- 🔧 **Quality Expertise** - 7QC tools, Six Sigma, PDCA, and more
- 📚 **Document Analysis** - Search through your quality documents
- 🛠️ **Tool Recommendations** - Smart suggestions for quality improvement
- 🆓 **Completely Free** - No API costs, works offline
- 🌐 **Easy Sharing** - Local network or cloud deployment ready

## 📁 Project Structure

```
KneadQuality-AI/
├── app_cloud.py              # Main application (cloud-ready)
├── app_with_ngrok.py         # Enhanced version with hosting options
├── config.py                 # Configuration settings
├── requirements.txt          # Dependencies
├── utils/                    # AI system components
│   ├── conversation.py       # Natural conversation system
│   ├── quality_knowledge.py  # Built-in quality expertise
│   ├── rag.py               # Document search system
│   ├── tool_recommender.py  # Quality tool recommendations
│   └── vector_store.py      # Vector database
├── data/raw/                # Your PDF documents
├── vectorStore/             # Built knowledge base
└── FREE_HOSTING_GUIDE.md    # Complete hosting instructions
```

## 🎯 Current Status

✅ **Knowledge Base**: 199 document chunks from quality PDFs  
✅ **Free Mode**: No API costs required  
✅ **Conversation Ready**: Natural chat capabilities  
✅ **Quality Tools**: Expert recommendations available  
✅ **Network Sharing**: Ready for local network access  
✅ **Cloud Ready**: Streamlit Cloud deployment ready  

## 🌐 Hosting Options

1. **Immediate**: Use network sharing for WiFi access
2. **Permanent**: Deploy to Streamlit Cloud (free)
3. **Advanced**: Use Railway, Render, or Replit

See `FREE_HOSTING_GUIDE.md` for detailed instructions.

## 🤝 Usage Examples

**Getting Started:**
- "Hello, what can you help me with?"

**Quality Management:**
- "What are the Seven Quality Control tools?"
- "How do I implement Six Sigma in my company?"
- "Explain the PDCA cycle with examples"

**Problem Solving:**
- "How can I reduce manufacturing defects?"
- "What tools help with process improvement?"
- "Recommend methods for quality control"

**General Conversation:**
- "How are you doing today?"
- "Thank you for the help!"
- "Can you explain statistical process control?"

## 🆘 Support

Your AI is designed to be helpful and conversational. If you encounter issues:

1. Try rephrasing your question
2. Use the sample questions as examples
3. Check that the app is running properly
4. Restart the application if needed

**Start chatting with your Quality Management AI today! 🎯**
