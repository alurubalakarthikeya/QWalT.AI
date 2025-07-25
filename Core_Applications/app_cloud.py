# KneadQuality-AI - Simple Cloud Version
import streamlit as st
import sys
from pathlib import Path

# Add project root to path BEFORE any imports
current_dir = Path(__file__).absolute().parent
project_root = current_dir.parent  # Go up one level from Core_Applications
sys.path.insert(0, str(project_root))

try:
    from AI_Systems.utils.rag import RAGSystem
    from AI_Systems.utils.tool_recommender import QualityToolRecommender
    from AI_Systems.utils.quality_knowledge import QualityKnowledgeBase
    from AI_Systems.utils.conversation import BasicConversation
except ImportError as e:
    st.error(f"Some modules not available: {e}")
    RAGSystem = None
    QualityToolRecommender = None
    QualityKnowledgeBase = None
    BasicConversation = None

st.set_page_config(page_title="KneadQuality-AI", page_icon="🔧", layout="wide")

# Initialize systems
@st.cache_resource
def initialize_systems():
    """Initialize available AI systems."""
    systems = {}
    
    st.info("🆓 **FREE MODE** - No API costs, works completely offline!")
    
    # Initialize conversation system (always works)
    if BasicConversation:
        systems['conversation'] = BasicConversation()
        st.success("✅ Conversation system loaded")
    
    # Initialize knowledge base (always works)
    if QualityKnowledgeBase:
        systems['knowledge'] = QualityKnowledgeBase()
        st.success("✅ Quality Knowledge Base loaded")
    else:
        systems['knowledge'] = None
    
    # Try to initialize document systems
    if RAGSystem:
        try:
            systems['rag'] = RAGSystem()
            st.success("✅ RAG System initialized")
        except Exception as e:
            st.warning(f"⚠️ Document system not available (normal for cloud hosting): {str(e)[:100]}")
            systems['rag'] = None
    else:
        systems['rag'] = None
    
    if QualityToolRecommender:
        try:
            systems['tools'] = QualityToolRecommender()
            st.success("✅ Tool Recommender initialized")
        except Exception as e:
            st.warning(f"⚠️ Tool recommender limited: {str(e)[:100]}")
            systems['tools'] = None
    else:
        systems['tools'] = None
    
    return systems

def process_simple_query(user_input, systems):
    """Simple query processing for cloud deployment."""
    responses = []
    
    # Handle conversational queries
    if systems.get('conversation'):
        try:
            # Check if it's a greeting or simple conversation
            conv_keywords = ['hello', 'hi', 'how are you', 'thank', 'bye', 'goodbye', 'what can you do']
            if any(keyword in user_input.lower() for keyword in conv_keywords):
                conv_response = systems['conversation'].get_response(user_input)
                responses.append({
                    'title': '💬 AI Assistant',
                    'content': conv_response,
                    'sources': []
                })
                return responses
        except Exception as e:
            st.error(f"Conversation error: {e}")
    
    # Handle quality management queries with knowledge base
    if systems.get('knowledge'):
        try:
            smart_response = systems['knowledge'].get_smart_response(user_input)
            if smart_response and smart_response.strip():
                responses.append({
                    'title': '🧠 Quality Management Expert',
                    'content': smart_response + "\n\n💡 *Response from built-in quality management knowledge base.*",
                    'sources': []
                })
        except Exception as e:
            st.error(f"Knowledge base error: {e}")
    
    # Try document system if available
    if systems.get('rag'):
        try:
            rag_result = systems['rag'].query(user_input)
            if rag_result.get('response') and rag_result['response'].strip():
                responses.append({
                    'title': '📚 Document Knowledge',
                    'content': rag_result['response'],
                    'sources': rag_result.get('sources', [])
                })
        except Exception:
            pass  # Silently fail for cloud deployment
    
    # Fallback response
    if not responses:
        if systems.get('conversation'):
            try:
                fallback = systems['conversation'].get_response(user_input)
                responses.append({
                    'title': '🤖 General Assistant',
                    'content': fallback,
                    'sources': []
                })
            except:
                pass
    
    # Final fallback
    if not responses:
        responses.append({
            'title': '🤖 KneadQuality-AI',
            'content': f"""I understand you're asking about: '{user_input}'

**I'm your Quality Management AI Assistant!**

🔧 **What I can help with:**
• Quality control methods and tools
• Process improvement strategies  
• Six Sigma and PDCA methodologies
• General conversation and guidance
• Problem-solving approaches

💬 **Try asking:**
• "Hello, how are you?"
• "What are the 7QC tools?"
• "How do I improve quality in my process?"
• "Tell me about Six Sigma"
• "What's the PDCA cycle?"

I'm here to help with quality management and general questions! 🎯""",
            'sources': []
        })
    
    return responses

def main():
    """Main application for cloud deployment."""
    
    st.title("🔧 KneadQuality-AI")
    st.markdown("### 🤖 Your AI Assistant for Quality Management")
    st.markdown("**🌐 Now available online! 🆓 Completely free to use!**")
    
    # Initialize systems
    systems = initialize_systems()
    
    # Main interface
    st.markdown("---")
    
    # Show capabilities
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **💬 Smart Conversation**
        - Natural chat interaction
        - Quality management expertise
        - Helpful guidance
        """)
    
    with col2:
        st.markdown("""
        **🔧 Quality Tools**
        - 7QC Tools guidance
        - Six Sigma methodologies
        - Process improvement
        """)
    
    with col3:
        st.markdown("""
        **🧠 Built-in Knowledge**
        - Quality standards
        - Best practices
        - Implementation guides
        """)
    
    # Chat interface
    user_input = st.text_area(
        "💬 **Ask me anything about quality management or just chat:**",
        placeholder="Try: 'Hello!', 'What are the 7QC tools?', 'How to improve quality?', or any question!",
        height=100
    )
    
    if st.button("🚀 Ask", type="primary"):
        if user_input.strip():
            # Process query
            responses = process_simple_query(user_input, systems)
            
            # Display responses
            for response in responses:
                with st.expander(response['title'], expanded=True):
                    st.write(response['content'])
                    
                    # Show sources if available
                    if response['sources']:
                        st.markdown("**📖 Sources:**")
                        for i, source in enumerate(response['sources'], 1):
                            if isinstance(source, dict):
                                st.write(f"{i}. {source.get('source_file', 'Unknown')}")
                            else:
                                st.write(f"{i}. {source}")
        else:
            st.warning("Please enter a question!")
    
    # Sample questions
    st.markdown("---")
    st.markdown("### 💡 Popular Questions:")
    
    example_cols = st.columns(2)
    
    with example_cols[0]:
        if st.button("👋 Hello there!"):
            st.session_state.sample_query = "Hello there!"
        if st.button("🔧 What are the 7QC tools?"):
            st.session_state.sample_query = "What are the 7QC tools?"
        if st.button("📈 How to improve quality?"):
            st.session_state.sample_query = "How can I improve quality in my processes?"
    
    with example_cols[1]:
        if st.button("⚙️ Tell me about Six Sigma"):
            st.session_state.sample_query = "Tell me about Six Sigma methodology"
        if st.button("🔄 Explain PDCA cycle"):
            st.session_state.sample_query = "Explain the PDCA cycle"
        if st.button("❓ What can you do?"):
            st.session_state.sample_query = "What can you help me with?"
    
    # Handle sample queries
    if hasattr(st.session_state, 'sample_query'):
        query = st.session_state.sample_query
        st.write(f"**You asked:** {query}")
        responses = process_simple_query(query, systems)
        
        for response in responses:
            with st.expander(response['title'], expanded=True):
                st.write(response['content'])
        
        del st.session_state.sample_query
    
    # Footer
    st.markdown("---")
    st.markdown("**🎯 KneadQuality-AI** - Your intelligent quality management assistant")
    st.markdown("💡 *Tip: This AI works completely offline and is free to use!*")

if __name__ == "__main__":
    main()
