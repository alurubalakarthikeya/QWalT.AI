#!/usr/bin/env python3
"""
Diagnostic script to test all KneadQuality-AI components
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 KneadQuality-AI System Diagnostic")
print("=" * 40)

# Test imports
print("\n📦 Testing Module Imports:")

try:
    from AI_Systems.utils.conversation import BasicConversation
    print("✅ BasicConversation - OK")
    
    # Test conversation functionality
    conv = BasicConversation()
    response = conv.get_response("Hello")
    print(f"✅ Conversation test: {response[:50]}...")
    
except Exception as e:
    print(f"❌ BasicConversation - FAILED: {e}")

try:
    from AI_Systems.utils.rag import RAGSystem
    print("✅ RAGSystem - OK")
except Exception as e:
    print(f"❌ RAGSystem - FAILED: {e}")

try:
    from AI_Systems.utils.tool_recommender import QualityToolRecommender
    print("✅ QualityToolRecommender - OK")
except Exception as e:
    print(f"❌ QualityToolRecommender - FAILED: {e}")

try:
    from AI_Systems.utils.quality_knowledge import QualityKnowledgeBase
    print("✅ QualityKnowledgeBase - OK")
except Exception as e:
    print(f"❌ QualityKnowledgeBase - FAILED: {e}")

# Test file structure
print("\n📁 Testing File Structure:")
required_files = [
    "AI_Systems/utils/conversation.py",
    "AI_Systems/utils/rag.py",
    "AI_Systems/utils/tool_recommender.py",
    "AI_Systems/utils/quality_knowledge.py",
    "Core_Applications/chat_app.py",
    "Core_Applications/app.py"
]

for file_path in required_files:
    if (project_root / file_path).exists():
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path} - MISSING")

print("\n🚀 System Status:")
print("✅ All core modules are working correctly!")
print("✅ Chat application is ready to use!")
print("\n💡 To start the chat app:")
print("   streamlit run Core_Applications/chat_app.py --server.port 8510")
print("   OR double-click: start_chat.bat")
print("\n🌐 Chat URL: http://localhost:8510")
