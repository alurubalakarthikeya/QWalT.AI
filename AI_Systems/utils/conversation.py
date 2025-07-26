# utils/conversation.py
import re
import random
from typing import Dict, List, Any, Optional

class BasicConversation:
    """
    Enhanced conversation handler for natural chat capabilities.
    Provides intelligent, context-aware responses with personality.
    """
    
    def __init__(self):
        self.conversation_patterns = {
            # Greetings - More variety and engaging
            r'\b(hi|hello|hey|good morning|good afternoon|good evening|greetings|howdy)\b': [
                "👋 Hello! I'm your Quality Management AI assistant. Ready to help you achieve excellence!",
                "🌟 Hi there! I'm here to help with quality management, process improvement, and much more!",
                "💫 Hello! Welcome to KneadQuality-AI. What exciting challenge can we tackle together today?",
                "🚀 Hey! Great to see you! How can I help you improve your processes today?",
                "✨ Hello and welcome! I'm your AI companion for all things quality and process improvement!"
            ],
            
            # How are you - More engaging responses
            r'\b(how are you|how\'s it going|what\'s up|how do you feel)\b': [
                "🤖 I'm running at peak performance! Excited to help you with quality management challenges!",
                "⚡ All systems are go! I'm energized and ready to tackle any quality questions you have!",
                "🎯 I'm doing fantastic! My databases are fresh and I'm ready to help optimize your processes!",
                "🔥 I'm in excellent condition! Ready to dive into some quality improvement discussions!",
                "💪 Operating at 100% efficiency! What quality challenges shall we solve together?"
            ],
            
            # What can you do - Comprehensive capabilities
            r'\b(what can you do|what are your capabilities|help me|what do you know|features)\b': [
                """🚀 **I'm your comprehensive Quality Management AI!** Here's what I can do:

🔧 **Quality Management Expertise:**
• 7QC Tools (Pareto, Fishbone, Control Charts, etc.)
• Six Sigma methodologies (DMAIC, DMADV)
• Lean Manufacturing principles
• PDCA cycle implementation
• Statistical Process Control (SPC)
• Quality auditing and compliance

📊 **Process Improvement:**
• Root cause analysis techniques
• Process mapping and optimization
• Performance measurement systems
• Waste reduction strategies
• Continuous improvement frameworks

💬 **Smart Conversations:**
• Natural language understanding
• Context-aware responses
• Multi-turn conversations
• Personalized recommendations

📚 **Document Intelligence:**
• Search through your documents
• Extract key quality insights
• Summarize complex procedures
• Cross-reference standards

🛠️ **Tool Recommendations:**
• Suggest appropriate quality tools
• Guide implementation strategies
• Provide templates and examples

Ask me anything about quality, processes, or just chat! I'm here to help! 😊"""
            ],
            
            # Thank you responses
            r'\b(thank you|thanks|thx|appreciate|grateful)\b': [
                "🙏 You're very welcome! I'm always happy to help with quality improvement!",
                "😊 My pleasure! Feel free to ask if you need anything else!",
                "✨ Glad I could help! Quality improvement is what I live for!",
                "🎉 You're welcome! Together we can achieve amazing quality results!",
                "💫 Anytime! I'm here whenever you need quality guidance!"
            ],
            
            # Goodbye responses
            r'\b(bye|goodbye|see you|farewell|talk later|gotta go)\b': [
                "👋 Goodbye! Keep striving for quality excellence!",
                "🌟 See you later! Remember: quality is a journey, not a destination!",
                "✨ Farewell! Come back anytime for quality insights!",
                "🚀 Take care! May your processes be ever-improving!",
                "💫 Bye for now! Keep pushing those quality boundaries!"
            ],
            
            # Quality specific responses
            r'\b(quality|improvement|process|six sigma|lean)\b.*\b(help|need|want|looking)\b': [
                "🎯 Excellent! Quality improvement is my specialty! What specific area would you like to focus on?",
                "🔧 Perfect! I love discussing quality topics. What's your current challenge?",
                "📊 Great question! Let's dive into some quality excellence together. What's on your mind?",
                "⚡ Quality improvement - my favorite topic! How can I help optimize your processes?"
            ],
            
            # Personal questions
            r'\b(who are you|what are you|tell me about yourself)\b': [
                """🤖 **I'm KneadQuality-AI!** 

I'm an advanced AI assistant specialized in quality management and process improvement. Think of me as your dedicated quality consultant who:

• Never sleeps (24/7 availability!) ⏰
• Has vast knowledge of quality methodologies 📚
• Loves solving complex process challenges 🧩
• Speaks in plain English (no jargon overload!) 💬
• Gets excited about continuous improvement 🚀

I was created to democratize quality knowledge and make world-class process improvement accessible to everyone. Whether you're a seasoned quality professional or just starting your improvement journey, I'm here to guide you!

What would you like to achieve together? 🎯"""
            ]
        }
        
        # Context tracking for better conversations
        self.last_topics = []
        self.conversation_flow = []
        
        # Response enhancers
        self.encouragement_phrases = [
            "Great question!",
            "Excellent point!",
            "That's a smart approach!",
            "You're on the right track!",
            "Fantastic thinking!"
        ]
        
        self.follow_up_questions = [
            "What else would you like to explore?",
            "How can we dive deeper into this?",
            "What's your next quality challenge?",
            "Would you like to explore related topics?"
        ]
        
        # Default responses for unmatched patterns
        self.default_responses = [
            "That's an interesting question! While I specialize in quality management, I'll do my best to help. Can you provide more context?",
            "I'd love to help you with that! Could you tell me more about what you're looking for?",
            "Great question! I'm here to assist. What specific aspect would you like to explore?"
        ]

    def get_response(self, user_input: str) -> str:
        """Generate an appropriate response based on user input."""
        user_input_lower = user_input.lower()
        
        # Track conversation topics
        self.conversation_flow.append(user_input_lower)
        if len(self.conversation_flow) > 10:
            self.conversation_flow = self.conversation_flow[-10:]
        
        # Check for patterns and generate response
        for pattern, responses in self.conversation_patterns.items():
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                base_response = random.choice(responses)
                return base_response
        
        # If no pattern matches, use default response
        return random.choice(self.default_responses)

    def is_conversational(self, user_input: str) -> bool:
        """Determine if the input is conversational vs. technical query."""
        conversational_indicators = [
            r'\b(hi|hello|hey|how are you|what\'s up|thanks|bye)\b',
            r'\b(who are you|what are you|tell me about)\b',
            r'\b(good|great|excellent|amazing|awesome)\b.*\b(job|work|answer)\b'
        ]
        
        user_input_lower = user_input.lower()
        
        for pattern in conversational_indicators:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                return True
        
        # Check for simple greetings or short social inputs
        if len(user_input.split()) <= 3 and any(word in user_input_lower for word in 
                                                ['hi', 'hello', 'hey', 'thanks', 'bye']):
            return True
            
        return False

    def enhance_response(self, base_response: str, user_input: str) -> str:
        """Enhance responses with personality and follow-ups."""
        enhanced_response = base_response
        
        # Add follow-up questions for engagement
        if len(enhanced_response) > 100 and not enhanced_response.endswith('?'):
            follow_up = random.choice(self.follow_up_questions)
            enhanced_response += f"\n\n{follow_up}"
        
        return enhanced_response

    def get_conversation_context(self) -> List[str]:
        """Get recent conversation context for continuity."""
        return self.conversation_flow[-5:] if self.conversation_flow else []

    def reset_context(self):
        """Reset conversation context for a fresh start."""
        self.conversation_flow = []
        self.last_topics = []
