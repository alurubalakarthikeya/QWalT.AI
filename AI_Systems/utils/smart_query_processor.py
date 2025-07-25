"""
Smart Query Processor for enhanced search and response capabilities.
This module provides intelligent query understanding and response generation.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import difflib


class SmartQueryProcessor:
    """Advanced query processing and response generation system."""
    
    def __init__(self):
        self.query_patterns = self._initialize_query_patterns()
        self.intent_classifier = self._initialize_intent_classifier()
        self.semantic_enhancer = self._initialize_semantic_enhancer()
        self.response_templates = self._initialize_response_templates()
    
    def _initialize_query_patterns(self) -> Dict[str, List[str]]:
        """Initialize query patterns for better understanding."""
        return {
            "7qc_tools": [
                r"7\s*qc?\s*tools?",
                r"seven\s*quality\s*control\s*tools?",
                r"basic\s*quality\s*tools?",
                r"fundamental\s*quality\s*tools?",
                r"statistical\s*quality\s*tools?",
                r"quality\s*control\s*techniques",
                r"7\s*basic\s*tools",
                r"check\s*sheet|histogram|pareto|fishbone|scatter|control\s*chart|stratification"
            ],
            "defect_reduction": [
                r"reduce\s*defects?",
                r"defect\s*reduction",
                r"minimize\s*defects?",
                r"eliminate\s*defects?",
                r"quality\s*issues?",
                r"manufacturing\s*problems?",
                r"product\s*defects?",
                r"process\s*problems?",
                r"improve\s*quality"
            ],
            "process_improvement": [
                r"process\s*improvement",
                r"improve\s*process",
                r"optimize\s*process",
                r"enhance\s*process",
                r"process\s*optimization",
                r"business\s*process",
                r"workflow\s*improvement",
                r"operational\s*excellence"
            ],
            "pdca_cycle": [
                r"pdca\s*cycle",
                r"plan\s*do\s*check\s*act",
                r"deming\s*cycle",
                r"continuous\s*improvement\s*cycle",
                r"improvement\s*methodology"
            ],
            "six_sigma": [
                r"six\s*sigma",
                r"6\s*sigma",
                r"dmaic",
                r"define\s*measure\s*analyze",
                r"statistical\s*quality\s*control",
                r"process\s*capability"
            ],
            "root_cause": [
                r"root\s*cause\s*analysis",
                r"5\s*whys?",
                r"fishbone\s*diagram",
                r"cause\s*and\s*effect",
                r"ishikawa\s*diagram",
                r"problem\s*solving",
                r"investigation"
            ],
            "lean_manufacturing": [
                r"lean\s*manufacturing",
                r"lean\s*principles",
                r"waste\s*reduction",
                r"5s\s*methodology",
                r"kaizen",
                r"continuous\s*improvement",
                r"value\s*stream\s*mapping"
            ],
            "customer_satisfaction": [
                r"customer\s*satisfaction",
                r"customer\s*complaints?",
                r"customer\s*feedback",
                r"customer\s*experience",
                r"service\s*quality",
                r"customer\s*retention"
            ]
        }
    
    def _initialize_intent_classifier(self) -> Dict[str, Dict]:
        """Initialize intent classification system."""
        return {
            "definition": {
                "patterns": [r"what\s*is", r"define", r"explain", r"meaning", r"definition"],
                "confidence_boost": 0.2
            },
            "how_to": {
                "patterns": [r"how\s*to", r"how\s*can", r"how\s*do", r"steps", r"process", r"implement"],
                "confidence_boost": 0.3
            },
            "benefits": {
                "patterns": [r"benefits", r"advantages", r"why\s*use", r"help", r"useful"],
                "confidence_boost": 0.15
            },
            "examples": {
                "patterns": [r"examples?", r"sample", r"instance", r"case\s*study"],
                "confidence_boost": 0.1
            },
            "comparison": {
                "patterns": [r"difference", r"compare", r"vs", r"versus", r"better"],
                "confidence_boost": 0.1
            }
        }
    
    def _initialize_semantic_enhancer(self) -> Dict[str, List[str]]:
        """Initialize semantic enhancement for better matching."""
        return {
            "quality": ["excellence", "standard", "grade", "caliber", "superiority"],
            "defect": ["flaw", "error", "mistake", "fault", "problem", "issue"],
            "improve": ["enhance", "better", "upgrade", "optimize", "refine"],
            "process": ["procedure", "method", "workflow", "operation", "system"],
            "control": ["manage", "monitor", "supervise", "regulate", "govern"],
            "analysis": ["examination", "study", "review", "assessment", "evaluation"],
            "customer": ["client", "consumer", "buyer", "user", "patron"],
            "manufacturing": ["production", "fabrication", "assembly", "making"]
        }
    
    def _initialize_response_templates(self) -> Dict[str, str]:
        """Initialize response templates for different query types."""
        return {
            "definition": "## {title}\n\n**Definition:** {definition}\n\n{detailed_content}",
            "how_to": "## How to {title}\n\n**Step-by-step Guide:**\n\n{steps}\n\n**Key Points:**\n{key_points}",
            "benefits": "## Benefits of {title}\n\n{benefits_list}\n\n{additional_info}",
            "examples": "## Examples of {title}\n\n{examples}\n\n{context}",
            "default": "## {title}\n\n{content}\n\n**Quick Tips:**\n{tips}"
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Comprehensive query analysis."""
        query_lower = query.lower().strip()
        
        # Step 1: Intent detection
        intent = self._detect_intent(query_lower)
        
        # Step 2: Topic matching with confidence scoring
        topic_scores = self._calculate_topic_scores(query_lower)
        
        # Step 3: Semantic enhancement
        enhanced_query = self._enhance_semantically(query_lower)
        
        # Step 4: Extract keywords
        keywords = self._extract_keywords(query_lower)
        
        # Step 5: Determine response type
        response_type = self._determine_response_type(intent, topic_scores)
        
        return {
            "original_query": query,
            "intent": intent,
            "topic_scores": topic_scores,
            "best_topic": max(topic_scores, key=topic_scores.get) if topic_scores else None,
            "best_score": max(topic_scores.values()) if topic_scores else 0,
            "enhanced_query": enhanced_query,
            "keywords": keywords,
            "response_type": response_type,
            "confidence": self._calculate_confidence(topic_scores, intent)
        }
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query."""
        for intent, config in self.intent_classifier.items():
            for pattern in config["patterns"]:
                if re.search(pattern, query):
                    return intent
        return "general"
    
    def _calculate_topic_scores(self, query: str) -> Dict[str, float]:
        """Calculate confidence scores for each topic."""
        scores = defaultdict(float)
        
        for topic, patterns in self.query_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, query))
                if matches > 0:
                    # Base score from pattern matches
                    base_score = min(matches * 0.3, 1.0)
                    
                    # Boost for exact matches
                    if re.search(rf"\b{pattern}\b", query):
                        base_score += 0.2
                    
                    scores[topic] = max(scores[topic], base_score)
        
        return dict(scores)
    
    def _enhance_semantically(self, query: str) -> str:
        """Enhance query with semantic alternatives."""
        enhanced = query
        
        for base_word, synonyms in self.semantic_enhancer.items():
            if base_word in query:
                # Add synonyms to search space
                for synonym in synonyms:
                    if synonym not in enhanced:
                        enhanced += f" {synonym}"
        
        return enhanced
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query."""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "how", "what", "when", "where", "why", "is", "are", "can", "do", "does"}
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _determine_response_type(self, intent: str, topic_scores: Dict[str, float]) -> str:
        """Determine the best response type."""
        if not topic_scores:
            return "general_help"
        
        max_score = max(topic_scores.values())
        
        if max_score > 0.7:
            return "specific_answer"
        elif max_score > 0.4:
            return "guided_answer"
        else:
            return "exploratory"
    
    def _calculate_confidence(self, topic_scores: Dict[str, float], intent: str) -> float:
        """Calculate overall confidence in understanding the query."""
        if not topic_scores:
            return 0.1
        
        max_score = max(topic_scores.values())
        intent_boost = self.intent_classifier.get(intent, {}).get("confidence_boost", 0)
        
        return min(max_score + intent_boost, 1.0)
    
    def suggest_related_queries(self, query: str, topic: str = None) -> List[str]:
        """Suggest related queries based on current query."""
        if not topic:
            analysis = self.analyze_query(query)
            topic = analysis["best_topic"]
        
        suggestions = {
            "7qc_tools": [
                "What is a Pareto chart and how to use it?",
                "How to create a control chart?",
                "When to use cause and effect diagram?",
                "Steps to implement check sheet method"
            ],
            "defect_reduction": [
                "Root cause analysis for defects",
                "How to implement poka-yoke?",
                "Statistical process control for quality",
                "Cost of quality calculation"
            ],
            "process_improvement": [
                "How to map value stream?",
                "What is kaizen methodology?",
                "Lean manufacturing principles",
                "How to measure process efficiency?"
            ],
            "pdca_cycle": [
                "PDCA implementation examples",
                "How to plan improvement projects?",
                "Continuous improvement best practices",
                "PDCA vs DMAIC comparison"
            ]
        }
        
        return suggestions.get(topic, [
            "What are the 7QC tools?",
            "How to reduce manufacturing defects?",
            "Process improvement methodologies",
            "Customer satisfaction improvement"
        ])
    
    def get_smart_fallback(self, query: str) -> str:
        """Generate intelligent fallback response when no specific match found."""
        analysis = self.analyze_query(query)
        
        if analysis["confidence"] > 0.3:
            # Partial understanding
            return f"""
## I understand you're asking about: {analysis["best_topic"].replace("_", " ").title()}

While I don't have a complete answer for your specific question, here's what I can help with:

**Related Topics I Know About:**
{self._format_related_topics(analysis["best_topic"])}

**Try asking:**
{self._format_suggestions(self.suggest_related_queries(query, analysis["best_topic"]))}

**Keywords I detected:** {", ".join(analysis["keywords"][:5])}

Would you like me to explain any of these related topics in detail?
            """
        else:
            # Low understanding - general help
            return """
## I'm here to help with Quality Management! 🔧

I specialize in:

**🎯 Core Topics:**
- **7QC Tools** - Fundamental quality control techniques
- **Process Improvement** - Systematic enhancement methods
- **Defect Reduction** - Strategies to minimize quality issues
- **Six Sigma & Lean** - Advanced methodologies
- **Root Cause Analysis** - Problem-solving techniques

**💡 Try asking:**
- "What are the 7QC tools and how to use them?"
- "How can I reduce defects in my process?"
- "Explain the PDCA cycle step by step"
- "What is Six Sigma methodology?"

**🚀 I can provide:**
- Step-by-step implementation guides
- Real-world examples and case studies
- Tool recommendations for specific problems
- Best practices and tips

What specific quality topic would you like to explore?
            """
    
    def _format_related_topics(self, topic: str) -> str:
        """Format related topics for display."""
        topic_relations = {
            "7qc_tools": "Check sheets, Pareto charts, Control charts, Fishbone diagrams",
            "defect_reduction": "Root cause analysis, Statistical process control, Poka-yoke",
            "process_improvement": "Lean manufacturing, Kaizen, Value stream mapping",
            "pdca_cycle": "Continuous improvement, Project planning, Quality cycles"
        }
        return f"- {topic_relations.get(topic, 'Quality management fundamentals')}"
    
    def _format_suggestions(self, suggestions: List[str]) -> str:
        """Format suggestions for display."""
        return "\n".join([f"- \"{suggestion}\"" for suggestion in suggestions[:4]])


class EnhancedQueryMatcher:
    """Enhanced matching for better query understanding."""
    
    def __init__(self):
        self.fuzzy_threshold = 0.6
    
    def fuzzy_match(self, query: str, candidates: List[str]) -> List[Tuple[str, float]]:
        """Perform fuzzy matching against candidates."""
        matches = []
        query_lower = query.lower()
        
        for candidate in candidates:
            # Use difflib for sequence matching
            ratio = difflib.SequenceMatcher(None, query_lower, candidate.lower()).ratio()
            if ratio >= self.fuzzy_threshold:
                matches.append((candidate, ratio))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def partial_match(self, query: str, text: str) -> float:
        """Calculate partial match score."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        return len(intersection) / len(query_words)
