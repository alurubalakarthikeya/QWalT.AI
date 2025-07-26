import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime

st.set_page_config(
    page_title="KneadQuality-AI Chat", 
    page_icon="💬", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path BEFORE any imports
current_dir = Path(__file__).absolute().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Import modules with error handling
try:
    from AI_Systems.utils.rag import RAGSystem
    from AI_Systems.utils.tool_recommender import QualityToolRecommender
    from AI_Systems.utils.quality_knowledge import QualityKnowledgeBase
    from AI_Systems.utils.conversation import BasicConversation
    MODULES_LOADED = True
except ImportError as e:
    st.error(f"⚠️ Some modules failed to load: {e}")
    MODULES_LOADED = False

# Custom CSS for better chat interface
st.markdown("""
<style>
/* Main chat container */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
}

/* User message styling */
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px 20%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* AI message styling */
.ai-message {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 20% 8px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* System message styling */
.system-message {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 10%;
    text-align: center;
    font-size: 0.9em;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Typing indicator */
.typing-indicator {
    background: #f0f0f0;
    padding: 8px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 20% 8px 0;
    font-style: italic;
    color: #666;
}

/* Chat input styling */
.chat-input {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 800px;
    z-index: 1000;
}

/* Hide streamlit default elements */
.stTextInput > div > div > input {
    border-radius: 25px;
    padding: 12px 20px;
    border: 2px solid #e0e0e0;
    font-size: 16px;
}

/* Quick action buttons */
.quick-action {
    display: inline-block;
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    color: #333;
    padding: 8px 16px;
    border-radius: 20px;
    margin: 4px;
    cursor: pointer;
    border: none;
    font-size: 14px;
    transition: all 0.3s ease;
}

.quick-action:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* Sidebar styling */
.sidebar-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm your **KneadQuality-AI** assistant. I'm here to help you with quality management, process improvement, and answer any questions you have. How can I assist you today?",
        "timestamp": datetime.now()
    })

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = []

# Initialize systems
if MODULES_LOADED:
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = RAGSystem()
    if "tool_recommender" not in st.session_state:
        st.session_state.tool_recommender = QualityToolRecommender()
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = QualityKnowledgeBase()
    if "conversation" not in st.session_state:
        st.session_state.conversation = BasicConversation()

# Sidebar with features
with st.sidebar:
    st.markdown("### 💬 KneadQuality-AI Chat")
    st.markdown("---")
    
    # Chat features
    st.markdown("#### 🚀 Features")
    st.markdown("""
    - **Smart Conversations** 🧠
    - **Quality Management** 🔧
    - **Document Search** 📄
    - **Tool Recommendations** 🛠️
    - **Process Guidance** 📊
    """)
    
    # Quick actions
    st.markdown("#### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔧 Quality Tools", key="quality_tools"):
            st.session_state.quick_question = "What are the 7QC tools and how can they help improve quality?"
        if st.button("📊 PDCA Cycle", key="pdca"):
            st.session_state.quick_question = "Explain the PDCA cycle and how to implement it"
    
    with col2:
        if st.button("🎯 Six Sigma", key="six_sigma"):
            st.session_state.quick_question = "Tell me about Six Sigma methodology"
        if st.button("📈 Process Improvement", key="process"):
            st.session_state.quick_question = "How can I improve my business processes?"
    
    # Chat settings
    st.markdown("#### ⚙️ Settings")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.conversation_context = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Chat cleared! How can I help you today?",
            "timestamp": datetime.now()
        })
        st.rerun()
    
    # Export chat
    if st.button("📥 Export Chat"):
        chat_export = ""
        for msg in st.session_state.messages:
            role = "🧑‍💼 You" if msg["role"] == "user" else "🤖 AI"
            timestamp = msg["timestamp"].strftime("%H:%M")
            chat_export += f"{role} ({timestamp}): {msg['content']}\n\n"
        
        st.download_button(
            label="💾 Download Chat",
            data=chat_export,
            file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    # Statistics
    st.markdown("#### 📊 Chat Stats")
    user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    st.metric("Your Messages", user_messages)
    st.metric("AI Responses", ai_messages)

# Main chat interface
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Chat header
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1>💬 KneadQuality-AI Chat Assistant</h1>
    <p style="color: #666; font-size: 18px;">Your intelligent companion for quality management and process improvement</p>
</div>
""", unsafe_allow_html=True)

# Display chat messages
chat_placeholder = st.container()

with chat_placeholder:
    for i, message in enumerate(st.session_state.messages):
        timestamp = message["timestamp"].strftime("%H:%M")
        
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>🧑‍💼 You</strong> <small>({timestamp})</small><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-message">
                <strong>🤖 KneadQuality-AI</strong> <small>({timestamp})</small><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Handle quick questions
if "quick_question" in st.session_state:
    prompt = st.session_state.quick_question
    del st.session_state.quick_question
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now()
    })
    
    # Process the question
    if MODULES_LOADED:
        # Show typing indicator
        with st.empty():
            st.markdown('<div class="typing-indicator">🤖 AI is typing...</div>', unsafe_allow_html=True)
            time.sleep(1)
        
        # Get response
        try:
            # Check if it's a conversational query
            if st.session_state.conversation.is_conversational(prompt):
                response = st.session_state.conversation.get_response(prompt)
            else:
                # Try RAG system first
                rag_result = st.session_state.rag_system.query(prompt, top_k=3)
                
                # Extract response from RAG result (it returns a dict)
                if rag_result and isinstance(rag_result, dict) and 'response' in rag_result:
                    rag_response = rag_result['response']
                    relevance_score = rag_result.get('relevance_score', 0)
                    
                    # Check if RAG found meaningful content
                    if (rag_response and 
                        len(rag_response.strip()) > 50 and 
                        not rag_response.startswith("I don't have relevant documents") and
                        not rag_response.startswith("I couldn't find any relevant information")):
                        
                        response = rag_response
                        
                        # Add enhanced source information
                        if 'sources' in rag_result and rag_result['sources']:
                            source_info = "\n\n📚 **Sources Used:**"
                            for i, source in enumerate(rag_result['sources'][:3], 1):
                                source_file = source.get('source_file', 'Unknown')
                                match_quality = source.get('match_quality', 'Unknown')
                                source_info += f"\n{i}. {source_file} ({match_quality} match)"
                            response += source_info
                    else:
                        response = None
                else:
                    response = None
                
                # If RAG didn't provide a good response, fall back to knowledge base
                if not response:
                    kb_response = st.session_state.knowledge_base.get_smart_response(prompt)
                    if kb_response:
                        response = kb_response
                    else:
                        response = st.session_state.conversation.get_response(prompt)
            
            # Enhance response with context
            response = st.session_state.conversation.enhance_response(response, prompt)
            
        except Exception as e:
            response = f"I apologize, but I encountered an error while processing your question: {str(e)}"
    else:
        response = "I'm currently in limited mode due to module loading issues. Please try restarting the application."
    
    # Add AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now()
    })
    
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Chat input at the bottom
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)  # Spacer

# Chat input
prompt = st.chat_input("💭 Type your message here... Ask about quality management, processes, or anything else!")

if prompt:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now()
    })
    
    # Add to conversation context
    st.session_state.conversation_context.append(f"User: {prompt}")
    
    if MODULES_LOADED:
        # Process the message
        try:
            # Determine response type based on content
            if st.session_state.conversation.is_conversational(prompt):
                response = st.session_state.conversation.get_response(prompt)
            else:
                # Try RAG system for document-based queries
                rag_result = st.session_state.rag_system.query(prompt, top_k=3)
                
                # Extract response from RAG result (it returns a dict)
                if rag_result and isinstance(rag_result, dict) and 'response' in rag_result:
                    rag_response = rag_result['response']
                    relevance_score = rag_result.get('relevance_score', 0)
                    
                    # Check if RAG found meaningful content
                    if (rag_response and 
                        len(rag_response.strip()) > 50 and 
                        not rag_response.startswith("I don't have relevant documents") and
                        not rag_response.startswith("I couldn't find any relevant information")):
                        
                        response = rag_response
                        
                        # Add enhanced source information
                        if 'sources' in rag_result and rag_result['sources']:
                            source_info = "\n\n📚 **Sources Used:**"
                            for i, source in enumerate(rag_result['sources'][:3], 1):
                                source_file = source.get('source_file', 'Unknown')
                                match_quality = source.get('match_quality', 'Unknown')
                                relevance = source.get('relevance_score', 0)
                                source_info += f"\n{i}. {source_file} (Quality: {match_quality}, Relevance: {relevance:.2f})"
                            response += source_info
                            
                        # Add confidence indicator
                        if relevance_score > 0.7:
                            response += "\n\n✅ **High confidence answer based on documents**"
                        elif relevance_score > 0.4:
                            response += "\n\n⚠️ **Medium confidence - please verify information**"
                    else:
                        response = None
                else:
                    response = None
                
                # If RAG didn't provide a good response, try knowledge base
                if not response:
                    kb_response = st.session_state.knowledge_base.get_smart_response(prompt)
                    
                    if kb_response and kb_response != "I don't have specific information about that topic.":
                        response = kb_response
                    else:
                        # Fall back to conversation system
                        response = st.session_state.conversation.get_response(prompt)
            
            # Enhance response with context and suggestions
            response = st.session_state.conversation.enhance_response(response, prompt)
            
            # Add tool recommendations if relevant
            tool_suggestions = st.session_state.tool_recommender.recommend_tools(prompt)
            if tool_suggestions:
                response += f"\n\n🛠️ **Recommended Tools**: {tool_suggestions}"
            
        except Exception as e:
            response = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
    else:
        response = "I'm currently in limited mode. Please check the system status and try again."
    
    # Add AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now()
    })
    
    # Add to conversation context
    st.session_state.conversation_context.append(f"AI: {response}")
    
    # Keep context manageable (last 10 exchanges)
    if len(st.session_state.conversation_context) > 20:
        st.session_state.conversation_context = st.session_state.conversation_context[-20:]
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>💡 <strong>Tip:</strong> Try asking about quality tools, process improvement, or upload documents for analysis!</p>
    <p>🚀 <strong>KneadQuality-AI</strong> - Your intelligent quality management assistant</p>
</div>
""", unsafe_allow_html=True)
