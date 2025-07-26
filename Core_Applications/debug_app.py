import streamlit as st
import sys
import os
from pathlib import Path

st.set_page_config(page_title="KneadQuality-AI - Debug", page_icon="🔧", layout="wide")

# Debug Information
st.title("🔧 KneadQuality-AI - Import Debug")

# Add project root to path BEFORE any imports
current_dir = Path(__file__).absolute().parent
project_root = current_dir.parent  # Go up one level from Core_Applications
sys.path.insert(0, str(project_root))

st.subheader("Debug Information")
st.write(f"**Current file:** {__file__}")
st.write(f"**Project root:** {project_root}")
st.write(f"**Project root exists:** {project_root.exists()}")
st.write(f"**Project root absolute:** {project_root.absolute()}")
st.write(f"**Python path includes project root:** {str(project_root) in sys.path}")

# Check if AI_Systems folder exists
ai_systems_path = project_root / "AI_Systems"
st.write(f"**AI_Systems path:** {ai_systems_path}")
st.write(f"**AI_Systems exists:** {ai_systems_path.exists()}")

if ai_systems_path.exists():
    utils_path = ai_systems_path / "utils"
    st.write(f"**Utils path:** {utils_path}")
    st.write(f"**Utils exists:** {utils_path.exists()}")
    
    if utils_path.exists():
        st.write("**Files in utils:**")
        for file in utils_path.iterdir():
            st.write(f"  - {file.name}")

st.subheader("Import Testing")

# Test imports one by one
modules_to_test = [
    ("AI_Systems.utils.rag", "RAGSystem"),
    ("AI_Systems.utils.tool_recommender", "QualityToolRecommender"),
    ("AI_Systems.utils.quality_knowledge", "QualityKnowledgeBase"),
    ("AI_Systems.utils.conversation", "BasicConversation")
]

import_results = {}

for module_name, class_name in modules_to_test:
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        import_results[module_name] = f"✅ Successfully imported {class_name}"
        st.success(f"✅ {module_name}.{class_name} imported successfully")
    except ImportError as e:
        import_results[module_name] = f"❌ Import failed: {e}"
        st.error(f"❌ Failed to import {module_name}.{class_name}: {e}")
    except Exception as e:
        import_results[module_name] = f"❌ Error: {e}"
        st.error(f"❌ Error with {module_name}.{class_name}: {e}")

# Final status
all_successful = all("✅" in result for result in import_results.values())

if all_successful:
    st.success("🎉 All imports successful! The application should work correctly.")
    
    # Try to run a simple instance
    try:
        from AI_Systems.utils.rag import RAGSystem
        from AI_Systems.utils.conversation import BasicConversation
        
        st.subheader("Quick Functionality Test")
        
        # Test conversation system
        conversation = BasicConversation()
        test_response = conversation.get_response("Hello")
        st.write(f"**Conversation test:** {test_response}")
        
        st.info("✅ All systems are working correctly!")
        
    except Exception as e:
        st.error(f"Error during functionality test: {e}")

else:
    st.error("❌ Some imports failed. Please check the errors above.")

st.subheader("System Information")
st.write(f"**Python version:** {sys.version}")
st.write(f"**Working directory:** {os.getcwd()}")
st.write(f"**Python executable:** {sys.executable}")
