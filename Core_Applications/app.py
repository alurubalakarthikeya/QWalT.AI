import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title="KneadQuality-AI", page_icon="🔧", layout="wide")

# Add project root to path BEFORE any imports
current_dir = Path(__file__).absolute().parent
project_root = current_dir.parent  # Go up one level from Core_Applications
sys.path.insert(0, str(project_root))

# Import modules with detailed error handling
import_success = True
import_errors = []

try:
    from AI_Systems.utils.rag import RAGSystem
except ImportError as e:
    import_errors.append(f"RAGSystem: {e}")
    RAGSystem = None
    import_success = False

try:
    from AI_Systems.utils.tool_recommender import QualityToolRecommender
except ImportError as e:
    import_errors.append(f"QualityToolRecommender: {e}")
    QualityToolRecommender = None
    import_success = False

try:
    from AI_Systems.utils.quality_knowledge import QualityKnowledgeBase
except ImportError as e:
    import_errors.append(f"QualityKnowledgeBase: {e}")
    QualityKnowledgeBase = None
    import_success = False

try:
    from AI_Systems.utils.conversation import BasicConversation
except ImportError as e:
    import_errors.append(f"BasicConversation: {e}")
    BasicConversation = None
    import_success = False

# Display import status
if not import_success:
    st.error("⚠️ Some modules failed to import:")
    for error in import_errors:
        st.error(f"• {error}")
    st.info("💡 The application will run in limited mode using available modules only.")
else:
    # Only show success message briefly, then hide it
    if "show_import_success" not in st.session_state:
        st.session_state.show_import_success = True
    
    if st.session_state.show_import_success:
        success_placeholder = st.empty()
        success_placeholder.success("✅ All modules imported successfully!")
        # Auto-hide after first load
        st.session_state.show_import_success = False

# Check if running in free mode
try:
    from config import USE_OPENAI
    free_mode = not USE_OPENAI
except:
    free_mode = True

# Initialize systems
@st.cache_resource
def initialize_systems():
    """Initialize RAG and Tool Recommender systems."""
    systems = {}
    
    if free_mode:
        st.info("🆓 **Running in FREE mode** - Using local document search and built-in knowledge base (no API costs!)")
    
    # Always initialize knowledge base (no dependencies)
    if QualityKnowledgeBase:
        systems['knowledge'] = QualityKnowledgeBase()
        st.success("✅ Quality Knowledge Base loaded")
    else:
        systems['knowledge'] = None
    
    if RAGSystem:
        try:
            systems['rag'] = RAGSystem()
            st.success("✅ RAG System initialized")
        except Exception as e:
            st.warning(f"⚠️ RAG System failed to initialize: {e}")
            systems['rag'] = None
    else:
        systems['rag'] = None
    
    if QualityToolRecommender:
        try:
            systems['tools'] = QualityToolRecommender()
            st.success("✅ Tool Recommender initialized")
        except Exception as e:
            st.warning(f"⚠️ Tool Recommender failed to initialize: {e}")
            systems['tools'] = None
    else:
        systems['tools'] = None
    
    return systems

def process_query(user_input, systems):
    """Process user query with enhanced RAG, tool recommendation, and smart fallback."""
    responses = []
    
    # Detect if user is asking for tool recommendations
    tool_keywords = ['tool', 'recommend', 'suggest', 'help with', 'how to', 'what should', 'which method']
    is_tool_query = any(keyword in user_input.lower() for keyword in tool_keywords)
    
    # RAG System Response
    if systems['rag']:
        try:
            rag_result = systems['rag'].query(user_input)
            if rag_result['response'] and rag_result['response'].strip():
                responses.append({
                    'title': '📚 Knowledge Base Response',
                    'content': rag_result['response'],
                    'sources': rag_result.get('sources', [])
                })
        except Exception as e:
            responses.append({
                'title': '❌ RAG System Error',
                'content': f"Error querying knowledge base: {e}",
                'sources': []
            })
    
    # Tool Recommendation
    if systems['tools'] and is_tool_query:
        try:
            tool_result = systems['tools'].recommend_tools(user_input, top_k=3)
            if tool_result['recommendations']:
                tool_content = "Based on your query, I recommend these quality tools:\n\n"
                
                for i, rec in enumerate(tool_result['recommendations'], 1):
                    tool_content += f"**{i}. {rec['name']}** (Score: {rec['relevance_score']}/10)\n"
                    tool_content += f"- *Category*: {rec['category']}\n"
                    tool_content += f"- *Complexity*: {rec['complexity']}\n"
                    tool_content += f"- *Implementation Time*: {rec['implementation_time']}\n"
                    tool_content += f"- *Description*: {rec['description']}\n"
                    
                    if 'reasoning' in rec:
                        tool_content += f"- *Why recommended*: {rec['reasoning'][:200]}...\n"
                    
                    tool_content += "\n"
                
                responses.append({
                    'title': '🔧 Tool Recommendations',
                    'content': tool_content,
                    'sources': []
                })
        except Exception as e:
            responses.append({
                'title': '❌ Tool Recommender Error',
                'content': f"Error getting tool recommendations: {e}",
                'sources': []
            })
    
    # Enhanced fallback with Quality Knowledge Base
    if not responses and systems.get('knowledge'):
        try:
            smart_response = systems['knowledge'].get_smart_response(user_input)
            if smart_response and smart_response.strip():
                responses.append({
                    'title': '🧠 Quality Management Insights',
                    'content': smart_response + "\n\n💡 *This response is from our built-in quality management knowledge base.*",
                    'sources': []
                })
        except Exception as e:
            responses.append({
                'title': '❌ Knowledge Base Error',
                'content': f"Error accessing quality knowledge: {e}",
                'sources': []
            })
    
    # Final fallback if no responses
    if not responses:
        responses.append({
            'title': '🤖 Smart Assistant',
            'content': f"I understand you're asking about: '{user_input}'\n\n**What I can help you with:**\n\n🔧 **Quality Tools & Methods:**\n- Seven Quality Control Tools (7QC)\n- Six Sigma methodologies\n- PDCA cycle implementation\n- Statistical process control\n- Root cause analysis\n\n📋 **Process Improvement:**\n- Workflow optimization\n- Defect reduction strategies\n- Performance measurement\n- Continuous improvement\n\n📊 **Data & Analytics:**\n- Quality metrics and KPIs\n- Statistical analysis methods\n- Data visualization techniques\n- Compliance reporting\n\n**Try asking:**\n• 'What quality tools help reduce defects?'\n• 'How do I implement Six Sigma?'\n• 'Explain the PDCA cycle'\n• 'What are the 7QC tools?'\n• 'How to measure process quality?'",
            'sources': []
        })
    
    return responses

# CSS Styling
st.markdown("""
<style>
body {
    background-color: white;
}
header[data-testid="stHeader"] {
    background-color: transparent;
}
.main {
    padding-top: 0rem;
    height: 100vh;
}
.top-banner {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #172d43;
    color: #91baf2;
    font-weight: bold;
    font-size: 1.6rem;
    padding: 1.2rem;
    z-index: 999;
    text-align: center;
}

.chat-container {
    height: calc(100vh - 9rem);
    position: fixed;
    bottom: 4.5rem;
}

.chat-bubble {
    padding: 1rem 1.3rem;
    border-radius: 1rem;
    margin: 0.4rem 0;
    max-width: 85%;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.user-msg {
    background-color: #172d43;
    color: white;
    margin-left: auto;
    text-align: right;
    width: fit-content;
}
.bot-msg {
    background-color: #f0f2f6;
    color: #333;
    margin-right: auto;
    width: fit-content;
    border-left: 4px solid #172d43;
}

.input-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: white;
    padding: 1rem;
    box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
    z-index: 998;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="top-banner">🔧 KneadQuality-AI - Quality Management Assistant</div>', unsafe_allow_html=True)

# Initialize systems
systems = initialize_systems()

# Chat Interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown("""
## Welcome to KneadQuality-AI! 🎯

I'm your AI-powered quality management assistant. I can help you with:

- **📚 Knowledge Base Queries**: Ask about quality standards, compliance, and best practices
- **🔧 Tool Recommendations**: Get suggestions for quality improvement tools (7QC tools, Six Sigma, etc.)
- **📊 Document Analysis**: Analyze your quality documents and data
- **🎯 Process Improvement**: Guidance on quality management methodologies

**Example queries:**
- "What tools can help reduce defects in manufacturing?"
- "Tell me about DPDP compliance requirements"
- "How can I improve customer satisfaction?"
- "What is the 7QC methodology?"

Go ahead and ask me anything about quality management!
""")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for entry in st.session_state.chat_history:
    st.markdown(f'<div class="chat-bubble user-msg">**You:** {entry["user"]}</div>', unsafe_allow_html=True)
    
    # Display each response
    for response in entry["bot"]:
        st.markdown(f'<div class="chat-bubble bot-msg"><strong>{response["title"]}</strong><br>{response["content"]}</div>', unsafe_allow_html=True)
        
        # Show sources if available
        if response.get('sources'):
            with st.expander(f"📖 Sources ({len(response['sources'])})"):
                for i, source in enumerate(response['sources'], 1):
                    st.write(f"{i}. **{Path(source['source_file']).name}** (Score: {source['score']:.3f})")
                    if source.get('chunk_preview'):
                        st.write(f"   Preview: {source['chunk_preview'][:150]}...")

st.markdown('</div>', unsafe_allow_html=True)

# Fixed Input Area
st.markdown('<div class="input-fixed">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    col1, col2 = st.columns([9, 1])
    with col1:
        user_input = st.text_input("", placeholder="Ask about quality management, tools, or standards...", label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("Send")
        if submitted and user_input:
            responses = process_query(user_input, systems)
            st.session_state.chat_history.append({"user": user_input, "bot": responses})
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
