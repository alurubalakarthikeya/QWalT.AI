# app_with_ngrok.py
import streamlit as st
import sys
from pathlib import Path
import os

# Add project root to path BEFORE any imports
current_dir = Path(__file__).absolute().parent
project_root = current_dir.parent  # Go up one level from Core_Applications
sys.path.insert(0, str(project_root))

try:
    from AI_Systems.utils.rag import RAGSystem
    from AI_Systems.utils.tool_recommender import QualityToolRecommender
    from AI_Systems.utils.quality_knowledge import QualityKnowledgeBase
    from AI_Systems.utils.conversation import BasicConversation
    from pyngrok import ngrok
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    RAGSystem = None
    QualityToolRecommender = None
    QualityKnowledgeBase = None
    BasicConversation = None

st.set_page_config(page_title="KneadQuality-AI", page_icon="🔧", layout="wide")

# Check if running in free mode
try:
    from config import USE_OPENAI
    free_mode = not USE_OPENAI
except:
    free_mode = True

# Ngrok setup (optional)
def setup_ngrok():
    """Setup ngrok tunnel for online access - requires free ngrok account."""
    try:
        # Check if ngrok is properly configured
        import subprocess
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return "ngrok_not_installed"
        
        # Close any existing tunnels
        ngrok.kill()
        
        # Create tunnel on port 8503
        public_url = ngrok.connect(8503)
        return public_url
    except subprocess.TimeoutExpired:
        return "ngrok_timeout"
    except FileNotFoundError:
        return "ngrok_not_found"
    except Exception as e:
        if "authentication failed" in str(e).lower() or "authtoken" in str(e).lower():
            return "ngrok_auth_required"
        return f"ngrok_error: {str(e)}"

# Initialize systems
@st.cache_resource
def initialize_systems():
    """Initialize all AI systems."""
    systems = {}
    
    if free_mode:
        st.info("🆓 **Running in FREE mode** - Using local document search and built-in knowledge base (no API costs!)")
    
    # Initialize conversation system
    if BasicConversation:
        systems['conversation'] = BasicConversation()
        st.success("✅ Conversation system loaded")
    
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
    """Process user query with enhanced conversation, RAG, and tool recommendation."""
    responses = []
    
    # Check if it's a conversational query first
    is_conversational = systems.get('conversation') and systems['conversation'].is_conversational(user_input)
    
    # Detect if user is asking for tool recommendations
    tool_keywords = ['tool', 'recommend', 'suggest', 'help with', 'how to', 'what should', 'which method']
    is_tool_query = any(keyword in user_input.lower() for keyword in tool_keywords)
    
    # Handle pure conversational queries
    if is_conversational and systems.get('conversation'):
        try:
            conv_response = systems['conversation'].get_response(user_input)
            responses.append({
                'title': '💬 Conversation',
                'content': conv_response,
                'sources': []
            })
            return responses
        except Exception as e:
            st.error(f"Conversation error: {e}")
    
    # RAG System Response
    if systems['rag']:
        try:
            rag_result = systems['rag'].query(user_input)
            if rag_result['response'] and rag_result['response'].strip():
                # Enhance with conversational tone
                enhanced_response = rag_result['response']
                if systems.get('conversation'):
                    enhanced_response = systems['conversation'].enhance_response(rag_result['response'], user_input)
                
                responses.append({
                    'title': '📚 Knowledge Base Response',
                    'content': enhanced_response,
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
                
                # Enhance with conversational tone
                if systems.get('conversation'):
                    tool_content = systems['conversation'].enhance_response(tool_content, user_input)
                
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
                # Enhance with conversational tone
                if systems.get('conversation'):
                    smart_response = systems['conversation'].enhance_response(smart_response, user_input)
                
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
    
    # Conversational fallback
    if not responses and systems.get('conversation'):
        try:
            conv_response = systems['conversation'].get_response(user_input)
            responses.append({
                'title': '💬 General Response',
                'content': conv_response,
                'sources': []
            })
        except Exception as e:
            st.error(f"Conversation error: {e}")
    
    # Final fallback if no responses
    if not responses:
        responses.append({
            'title': '🤖 Smart Assistant',
            'content': f"""I understand you're asking about: '{user_input}'

**What I can help you with:**

🔧 **Quality Tools & Methods:**
- Seven Quality Control Tools (7QC)
- Six Sigma methodologies
- PDCA cycle implementation
- Statistical process control
- Root cause analysis

📋 **Process Improvement:**
- Workflow optimization
- Defect reduction strategies
- Performance measurement
- Continuous improvement

💬 **General Conversation:**
- Chat about any topic
- Answer questions and provide guidance
- Help with problem-solving approaches

📊 **Data & Analytics:**
- Quality metrics and KPIs
- Statistical analysis methods
- Data visualization techniques
- Compliance reporting

**Try asking:**
• 'Hello, how are you?'
• 'What quality tools help reduce defects?'
• 'How do I implement Six Sigma?'
• 'Tell me about the PDCA cycle'
• 'What are the 7QC tools?'
• Or just chat with me about anything!""",
            'sources': []
        })
    
    return responses

def main():
    """Main application."""
    
    # Sidebar for hosting options
    with st.sidebar:
        st.title("🌐 Make Your AI Available Online")
        
        # Method 1: Ngrok (requires account)
        st.markdown("### 🚀 Method 1: Ngrok (Instant)")
        if st.button("🌐 Try Ngrok Setup"):
            with st.spinner("Setting up ngrok tunnel..."):
                result = setup_ngrok()
                
                if result == "ngrok_auth_required":
                    st.warning("⚠️ **Ngrok Authentication Required**")
                    st.markdown("""
                    **To use ngrok (free):**
                    1. Sign up: [ngrok.com/signup](https://dashboard.ngrok.com/signup)
                    2. Get your token: [Your Authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)
                    3. Run: `ngrok config add-authtoken YOUR_TOKEN`
                    4. Try the button again!
                    """)
                elif result == "ngrok_not_found":
                    st.error("❌ Ngrok not installed")
                    st.info("Download ngrok from: https://ngrok.com/download")
                elif isinstance(result, str) and result.startswith("ngrok_"):
                    st.error(f"❌ Ngrok issue: {result}")
                else:
                    st.success("🎉 Your app is now online!")
                    st.write(f"**Public URL:** {result}")
                    st.write("Share this link with anyone!")
        
        st.markdown("---")
        
        # Method 2: Alternative hosting options
        st.markdown("### 🔄 Method 2: Alternative Hosting")
        
        # Network sharing
        if st.button("📱 Enable Network Sharing"):
            st.success("✅ **Network sharing enabled!**")
            st.markdown("""
            **Your AI is accessible on your local network:**
            
            🏠 **Local Network URL:** 
            `http://192.168.29.51:8503`
            
            **Anyone on the same WiFi can access it using this URL**
            """)
        
        # Show hosting alternatives
        with st.expander("🌍 Other Free Hosting Options"):
            st.markdown("""
            **🆓 Free Cloud Hosting:**
            
            1. **Streamlit Cloud** (Recommended)
               - Upload your code to GitHub
               - Connect at: share.streamlit.io
               - Free hosting for public repos
            
            2. **Replit**
               - Import from GitHub
               - Free hosting with public link
               - Visit: replit.com
            
            3. **Railway**
               - Deploy from GitHub
               - Free tier available
               - Visit: railway.app
            
            4. **Render**
               - Free web service hosting
               - Visit: render.com
            """)
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        if free_mode:
            st.success("🆓 FREE Mode Active")
        else:
            st.info("💰 API Mode Active")
    
    # Main app
    st.title("🔧 KneadQuality-AI")
    st.markdown("### 🤖 Your AI Assistant for Quality Management & General Conversation")
    
    # Initialize systems
    systems = initialize_systems()
    
    # Chat interface
    st.markdown("---")
    
    # Display capabilities
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **💬 Conversation**
        - General chat & questions
        - Friendly interaction
        - Help & guidance
        """)
    
    with col2:
        st.markdown("""
        **📚 Document Analysis**
        - Search your PDFs
        - Extract information
        - Context-aware responses
        """)
    
    with col3:
        st.markdown("""
        **🔧 Quality Tools**
        - Tool recommendations
        - Implementation guidance
        - Best practices
        """)
    
    # Chat input
    user_input = st.text_area(
        "💬 **Ask me anything or chat with me:**",
        placeholder="Try: 'Hello!', 'What are the 7QC tools?', 'How can I improve quality?', or just chat with me!",
        height=100
    )
    
    if st.button("🚀 Send", type="primary"):
        if user_input.strip():
            # Process query
            responses = process_query(user_input, systems)
            
            # Display responses
            for response in responses:
                with st.expander(response['title'], expanded=True):
                    st.write(response['content'])
                    
                    # Show sources if available
                    if response['sources']:
                        st.markdown("**📖 Sources:**")
                        for i, source in enumerate(response['sources'], 1):
                            if isinstance(source, dict):
                                st.write(f"{i}. {source.get('source_file', 'Unknown')} (Score: {source.get('score', 0):.3f})")
                            else:
                                st.write(f"{i}. {source}")
        else:
            st.warning("Please enter a question or message!")
    
    # Sample questions
    st.markdown("---")
    st.markdown("### 💡 Try These Sample Questions:")
    
    sample_cols = st.columns(2)
    
    with sample_cols[0]:
        st.markdown("""
        **💬 Conversational:**
        - "Hello, how are you?"
        - "What can you help me with?"
        - "Thank you for your help!"
        
        **🔧 Quality Management:**
        - "What are the 7QC tools?"
        - "How do I implement Six Sigma?"
        - "Explain the PDCA cycle"
        """)
    
    with sample_cols[1]:
        st.markdown("""
        **🛠️ Tool Recommendations:**
        - "What tools help reduce defects?"
        - "Recommend tools for process improvement"
        - "How to measure quality performance?"
        
        **📊 Business & Process:**
        - "How to improve efficiency?"
        - "What is statistical process control?"
        - "Data protection compliance tips"
        """)

if __name__ == "__main__":
    main()
