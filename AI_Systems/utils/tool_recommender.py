"""
AI-Powered Tool Recommender System for Quality Management

This module provides intelligent tool recommendations based on:
1. Document analysis from your knowledge base
2. Quality management standards (7QC tools)
3. Context-aware suggestions for specific scenarios
4. Integration with the RAG system for knowledge-driven recommendations
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from AI_Systems.utils.rag import RAGSystem
    from config import *
except ImportError as e:
    logging.error(f"Failed to import dependencies: {e}")
    RAGSystem = None


class QualityToolRecommender:
    """
    Intelligent tool recommender for quality management based on 7QC tools
    and document knowledge base analysis.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the tool recommender."""
        self.config = config or self._load_default_config()
        
        # Initialize RAG system if available
        self.rag_system = None
        if RAGSystem:
            try:
                self.rag_system = RAGSystem(config)
                logging.info("RAG system initialized for tool recommender")
            except Exception as e:
                logging.warning(f"Failed to initialize RAG system: {e}")
        
        # Quality tools database
        self.quality_tools = self._initialize_quality_tools()
        
        # Keywords for different quality scenarios
        self.scenario_keywords = self._initialize_scenario_keywords()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        try:
            return {
                'VECTOR_DIR': VECTOR_DIR,
                'EMBED_MODEL': EMBED_MODEL,
                'LLM_MODEL': LLM_MODEL,
                'TOP_K': TOP_K,
                'OPENAI_API_KEY': OPENAI_API_KEY
            }
        except:
            return {}
    
    def _initialize_quality_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the 7QC tools and additional quality management tools."""
        return {
            # 7 Quality Control Tools
            "check_sheet": {
                "name": "Check Sheet (Data Collection Sheet)",
                "category": "7QC",
                "description": "Systematic data collection tool for tracking defects, frequencies, or observations",
                "use_cases": [
                    "Defect tracking",
                    "Data collection",
                    "Frequency analysis",
                    "Process monitoring",
                    "Compliance checking"
                ],
                "keywords": ["data collection", "tracking", "defects", "frequency", "monitoring", "checklist"],
                "complexity": "Low",
                "implementation_time": "1-2 days",
                "benefits": ["Standardized data collection", "Error reduction", "Trend identification"]
            },
            
            "histogram": {
                "name": "Histogram",
                "category": "7QC",
                "description": "Bar chart showing frequency distribution of data to understand process variation",
                "use_cases": [
                    "Distribution analysis",
                    "Process capability assessment",
                    "Variation patterns",
                    "Quality characteristics analysis"
                ],
                "keywords": ["distribution", "variation", "frequency", "process capability", "patterns"],
                "complexity": "Low",
                "implementation_time": "1 day",
                "benefits": ["Visual data representation", "Pattern recognition", "Process understanding"]
            },
            
            "pareto_chart": {
                "name": "Pareto Chart",
                "category": "7QC",
                "description": "Bar chart identifying the most significant factors (80/20 rule application)",
                "use_cases": [
                    "Problem prioritization",
                    "Root cause analysis",
                    "Resource allocation",
                    "Defect analysis",
                    "Cost reduction focus"
                ],
                "keywords": ["prioritization", "80/20", "significant factors", "root cause", "cost reduction"],
                "complexity": "Low",
                "implementation_time": "1-2 days",
                "benefits": ["Priority identification", "Resource optimization", "Focus on vital few"]
            },
            
            "cause_effect_diagram": {
                "name": "Cause & Effect Diagram (Fishbone/Ishikawa)",
                "category": "7QC",
                "description": "Visual tool for identifying potential root causes of problems",
                "use_cases": [
                    "Root cause analysis",
                    "Brainstorming sessions",
                    "Problem solving",
                    "Process improvement",
                    "Team collaboration"
                ],
                "keywords": ["root cause", "fishbone", "ishikawa", "brainstorming", "problem solving"],
                "complexity": "Medium",
                "implementation_time": "2-3 days",
                "benefits": ["Systematic problem analysis", "Team engagement", "Comprehensive cause identification"]
            },
            
            "scatter_diagram": {
                "name": "Scatter Diagram",
                "category": "7QC",
                "description": "Plot showing relationship between two variables to identify correlations",
                "use_cases": [
                    "Correlation analysis",
                    "Variable relationships",
                    "Process parameter optimization",
                    "Predictive analysis"
                ],
                "keywords": ["correlation", "relationship", "variables", "optimization", "prediction"],
                "complexity": "Medium",
                "implementation_time": "1-2 days",
                "benefits": ["Relationship identification", "Data-driven decisions", "Process optimization"]
            },
            
            "control_chart": {
                "name": "Control Chart",
                "category": "7QC",
                "description": "Time-series chart for monitoring process stability and detecting variations",
                "use_cases": [
                    "Process control",
                    "Stability monitoring",
                    "Variation detection",
                    "Quality assurance",
                    "Continuous improvement"
                ],
                "keywords": ["process control", "stability", "monitoring", "SPC", "variation", "limits"],
                "complexity": "High",
                "implementation_time": "1-2 weeks",
                "benefits": ["Process stability", "Early warning system", "Continuous monitoring"]
            },
            
            "stratification": {
                "name": "Stratification",
                "category": "7QC",
                "description": "Data segmentation technique to identify patterns in different groups",
                "use_cases": [
                    "Data segmentation",
                    "Pattern identification",
                    "Group comparisons",
                    "Targeted improvements"
                ],
                "keywords": ["segmentation", "groups", "patterns", "comparison", "targeted"],
                "complexity": "Medium",
                "implementation_time": "2-3 days",
                "benefits": ["Detailed insights", "Targeted actions", "Pattern recognition"]
            },
            
            # Additional Quality Management Tools
            "5_whys": {
                "name": "5 Whys Analysis",
                "category": "Problem Solving",
                "description": "Iterative questioning technique to explore cause-and-effect relationships",
                "use_cases": [
                    "Root cause analysis",
                    "Simple problem solving",
                    "Quick investigation",
                    "Process improvement"
                ],
                "keywords": ["why", "root cause", "investigation", "simple", "quick"],
                "complexity": "Low",
                "implementation_time": "1 day",
                "benefits": ["Simple methodology", "Quick results", "Team engagement"]
            },
            
            "pdca_cycle": {
                "name": "PDCA Cycle (Plan-Do-Check-Act)",
                "category": "Process Improvement",
                "description": "Continuous improvement methodology for systematic problem solving",
                "use_cases": [
                    "Continuous improvement",
                    "Process optimization",
                    "Change management",
                    "Quality improvement"
                ],
                "keywords": ["PDCA", "continuous improvement", "plan", "do", "check", "act", "cycle"],
                "complexity": "Medium",
                "implementation_time": "Ongoing",
                "benefits": ["Systematic approach", "Continuous learning", "Sustainable improvement"]
            },
            
            "poka_yoke": {
                "name": "Poka-Yoke (Error Proofing)",
                "category": "Error Prevention",
                "description": "Techniques to prevent or detect errors before they cause defects",
                "use_cases": [
                    "Error prevention",
                    "Process design",
                    "Quality assurance",
                    "Mistake proofing"
                ],
                "keywords": ["error proofing", "mistake", "prevention", "design", "fool proof"],
                "complexity": "Medium",
                "implementation_time": "1-2 weeks",
                "benefits": ["Error reduction", "Quality improvement", "Cost savings"]
            },
            
            "6_sigma": {
                "name": "Six Sigma DMAIC",
                "category": "Process Improvement",
                "description": "Data-driven methodology for eliminating defects (Define-Measure-Analyze-Improve-Control)",
                "use_cases": [
                    "Major process improvement",
                    "Defect reduction",
                    "Data-driven decisions",
                    "Large-scale projects"
                ],
                "keywords": ["six sigma", "DMAIC", "defect reduction", "data driven", "statistical"],
                "complexity": "High",
                "implementation_time": "3-6 months",
                "benefits": ["Significant improvements", "Data-driven approach", "Standardized methodology"]
            }
        }
    
    def _initialize_scenario_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for different quality scenarios."""
        return {
            "data_collection": ["collect", "gather", "track", "record", "monitor", "measure"],
            "problem_solving": ["problem", "issue", "defect", "error", "failure", "nonconformance"],
            "process_improvement": ["improve", "optimize", "enhance", "efficiency", "performance"],
            "root_cause": ["root cause", "why", "reason", "source", "origin", "cause"],
            "prevention": ["prevent", "avoid", "proofing", "mistake", "error prevention"],
            "analysis": ["analyze", "examine", "investigate", "study", "evaluate"],
            "control": ["control", "monitor", "stability", "consistency", "regulation"],
            "correlation": ["relationship", "correlation", "connection", "association", "link"]
        }
    
    def recommend_tools(self, 
                       query: str, 
                       context: str = None, 
                       top_k: int = 3,
                       include_reasoning: bool = True) -> Dict[str, Any]:
        """
        Recommend quality tools based on query and context.
        
        Args:
            query: User's question or problem description
            context: Additional context (optional)
            top_k: Number of tools to recommend
            include_reasoning: Whether to include detailed reasoning
            
        Returns:
            Dictionary with recommendations and explanations
        """
        try:
            # Get additional context from RAG system if available
            rag_context = ""
            if self.rag_system:
                try:
                    rag_result = self.rag_system.query(query, top_k=3, include_sources=False)
                    rag_context = rag_result.get('response', '')
                except Exception as e:
                    self.logger.warning(f"RAG system query failed: {e}")
            
            # Combine all context
            full_context = f"{query}\n{context or ''}\n{rag_context}".lower()
            
            # Score tools based on relevance
            tool_scores = self._score_tools(full_context)
            
            # Get top recommendations
            top_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            # Prepare recommendations
            recommendations = []
            for tool_id, score in top_tools:
                tool_info = self.quality_tools[tool_id].copy()
                tool_info['relevance_score'] = round(score, 2)
                tool_info['tool_id'] = tool_id
                
                if include_reasoning:
                    tool_info['reasoning'] = self._generate_reasoning(tool_id, full_context, rag_context)
                
                recommendations.append(tool_info)
            
            return {
                'query': query,
                'recommendations': recommendations,
                'total_tools_evaluated': len(self.quality_tools),
                'rag_enhanced': bool(rag_context),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in tool recommendation: {e}")
            return {
                'query': query,
                'recommendations': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _score_tools(self, context: str) -> Dict[str, float]:
        """Score tools based on context relevance."""
        scores = {}
        
        for tool_id, tool_info in self.quality_tools.items():
            score = 0.0
            
            # Check keywords
            for keyword in tool_info['keywords']:
                if keyword in context:
                    score += 2.0
            
            # Check use cases
            for use_case in tool_info['use_cases']:
                if use_case.lower() in context:
                    score += 1.5
            
            # Check description
            description_words = tool_info['description'].lower().split()
            for word in description_words:
                if len(word) > 3 and word in context:
                    score += 0.5
            
            # Scenario-based scoring
            for scenario, keywords in self.scenario_keywords.items():
                for keyword in keywords:
                    if keyword in context:
                        if scenario == "data_collection" and tool_id in ["check_sheet", "histogram"]:
                            score += 1.0
                        elif scenario == "problem_solving" and tool_id in ["cause_effect_diagram", "5_whys", "pareto_chart"]:
                            score += 1.0
                        elif scenario == "process_improvement" and tool_id in ["pdca_cycle", "6_sigma", "control_chart"]:
                            score += 1.0
                        elif scenario == "prevention" and tool_id == "poka_yoke":
                            score += 1.0
                        elif scenario == "control" and tool_id == "control_chart":
                            score += 1.0
                        elif scenario == "correlation" and tool_id == "scatter_diagram":
                            score += 1.0
            
            scores[tool_id] = score
        
        return scores
    
    def _generate_reasoning(self, tool_id: str, context: str, rag_context: str) -> str:
        """Generate reasoning for why a tool was recommended."""
        tool_info = self.quality_tools[tool_id]
        
        reasoning_parts = []
        
        # Why this tool fits
        reasoning_parts.append(f"This tool is recommended because:")
        
        # Check for specific matches
        matched_keywords = [kw for kw in tool_info['keywords'] if kw in context]
        if matched_keywords:
            reasoning_parts.append(f"- Keywords match: {', '.join(matched_keywords[:3])}")
        
        matched_use_cases = [uc for uc in tool_info['use_cases'] if uc.lower() in context]
        if matched_use_cases:
            reasoning_parts.append(f"- Applicable use cases: {', '.join(matched_use_cases[:2])}")
        
        # Implementation considerations
        reasoning_parts.append(f"- Complexity: {tool_info['complexity']}")
        reasoning_parts.append(f"- Implementation time: {tool_info['implementation_time']}")
        
        # Benefits
        if tool_info['benefits']:
            reasoning_parts.append(f"- Key benefits: {', '.join(tool_info['benefits'][:2])}")
        
        # RAG-enhanced reasoning
        if rag_context and len(rag_context) > 50:
            reasoning_parts.append("- Enhanced by knowledge base analysis")
        
        return "\n".join(reasoning_parts)
    
    def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific tool."""
        if tool_id not in self.quality_tools:
            return {"error": f"Tool '{tool_id}' not found"}
        
        return self.quality_tools[tool_id].copy()
    
    def list_all_tools(self, category: str = None) -> List[Dict[str, Any]]:
        """List all available tools, optionally filtered by category."""
        tools = []
        
        for tool_id, tool_info in self.quality_tools.items():
            if category is None or tool_info['category'] == category:
                tool_data = tool_info.copy()
                tool_data['tool_id'] = tool_id
                tools.append(tool_data)
        
        return sorted(tools, key=lambda x: x['name'])
    
    def get_categories(self) -> List[str]:
        """Get all available tool categories."""
        categories = set(tool['category'] for tool in self.quality_tools.values())
        return sorted(list(categories))
    
    def search_tools(self, search_term: str) -> List[Dict[str, Any]]:
        """Search tools by name, description, or keywords."""
        results = []
        search_term = search_term.lower()
        
        for tool_id, tool_info in self.quality_tools.items():
            # Search in name, description, keywords, and use cases
            searchable_text = (
                tool_info['name'].lower() + " " +
                tool_info['description'].lower() + " " +
                " ".join(tool_info['keywords']) + " " +
                " ".join(tool_info['use_cases'])
            )
            
            if search_term in searchable_text:
                tool_data = tool_info.copy()
                tool_data['tool_id'] = tool_id
                results.append(tool_data)
        
        return results
    
    def generate_implementation_plan(self, tool_ids: List[str]) -> Dict[str, Any]:
        """Generate an implementation plan for selected tools."""
        if not tool_ids:
            return {"error": "No tools specified"}
        
        plan = {
            "tools": [],
            "total_implementation_time": "",
            "complexity_levels": {},
            "recommended_sequence": [],
            "considerations": []
        }
        
        complexity_order = {"Low": 1, "Medium": 2, "High": 3}
        
        for tool_id in tool_ids:
            if tool_id in self.quality_tools:
                tool_info = self.quality_tools[tool_id]
                plan["tools"].append({
                    "tool_id": tool_id,
                    "name": tool_info["name"],
                    "complexity": tool_info["complexity"],
                    "implementation_time": tool_info["implementation_time"],
                    "benefits": tool_info["benefits"]
                })
        
        # Sort by complexity for recommended sequence
        plan["recommended_sequence"] = sorted(
            plan["tools"], 
            key=lambda x: complexity_order.get(x["complexity"], 0)
        )
        
        # Count complexity levels
        for tool in plan["tools"]:
            complexity = tool["complexity"]
            plan["complexity_levels"][complexity] = plan["complexity_levels"].get(complexity, 0) + 1
        
        # Add implementation considerations
        plan["considerations"] = [
            "Start with low-complexity tools to build momentum",
            "Ensure proper training for team members",
            "Collect baseline data before implementation",
            "Plan for change management and communication",
            "Set up measurement systems to track progress"
        ]
        
        return plan


def main():
    """Main function for testing the tool recommender."""
    recommender = QualityToolRecommender()
    
    print("🔧 Quality Tool Recommender System")
    print("=" * 50)
    
    # Interactive mode
    while True:
        try:
            print("\nOptions:")
            print("1. Get tool recommendations")
            print("2. List all tools")
            print("3. Search tools")
            print("4. Get tool details")
            print("5. Generate implementation plan")
            print("6. Quit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                query = input("Describe your quality challenge or goal: ").strip()
                if query:
                    result = recommender.recommend_tools(query, top_k=3)
                    
                    print(f"\n📋 Recommendations for: '{query}'")
                    print("-" * 50)
                    
                    for i, rec in enumerate(result['recommendations'], 1):
                        print(f"\n{i}. {rec['name']}")
                        print(f"   Category: {rec['category']}")
                        print(f"   Relevance: {rec['relevance_score']}/10")
                        print(f"   Complexity: {rec['complexity']}")
                        print(f"   Time: {rec['implementation_time']}")
                        print(f"   Description: {rec['description']}")
                        if 'reasoning' in rec:
                            print(f"   {rec['reasoning']}")
            
            elif choice == "2":
                categories = recommender.get_categories()
                print(f"\nCategories: {', '.join(categories)}")
                category = input("Enter category (or press Enter for all): ").strip()
                
                tools = recommender.list_all_tools(category if category else None)
                print(f"\n📚 Available Tools ({len(tools)}):")
                print("-" * 50)
                
                for tool in tools:
                    print(f"• {tool['name']} ({tool['category']}) - {tool['complexity']} complexity")
            
            elif choice == "3":
                search_term = input("Enter search term: ").strip()
                if search_term:
                    results = recommender.search_tools(search_term)
                    print(f"\n🔍 Search Results for '{search_term}' ({len(results)} found):")
                    print("-" * 50)
                    
                    for tool in results:
                        print(f"• {tool['name']} - {tool['description'][:100]}...")
            
            elif choice == "4":
                tool_id = input("Enter tool ID: ").strip()
                details = recommender.get_tool_details(tool_id)
                
                if "error" in details:
                    print(f"❌ {details['error']}")
                else:
                    print(f"\n📖 {details['name']}")
                    print("-" * 50)
                    print(f"Category: {details['category']}")
                    print(f"Description: {details['description']}")
                    print(f"Complexity: {details['complexity']}")
                    print(f"Implementation Time: {details['implementation_time']}")
                    print(f"Use Cases: {', '.join(details['use_cases'])}")
                    print(f"Benefits: {', '.join(details['benefits'])}")
            
            elif choice == "5":
                tool_ids = input("Enter tool IDs (comma-separated): ").strip().split(',')
                tool_ids = [tid.strip() for tid in tool_ids if tid.strip()]
                
                if tool_ids:
                    plan = recommender.generate_implementation_plan(tool_ids)
                    
                    if "error" in plan:
                        print(f"❌ {plan['error']}")
                    else:
                        print(f"\n📋 Implementation Plan")
                        print("-" * 50)
                        print(f"Tools to implement: {len(plan['tools'])}")
                        
                        print("\nRecommended Sequence:")
                        for i, tool in enumerate(plan['recommended_sequence'], 1):
                            print(f"{i}. {tool['name']} ({tool['complexity']}) - {tool['implementation_time']}")
                        
                        print(f"\nConsiderations:")
                        for consideration in plan['considerations']:
                            print(f"• {consideration}")
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
