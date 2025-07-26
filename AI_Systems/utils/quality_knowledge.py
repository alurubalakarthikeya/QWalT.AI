"""
Enhanced quality management knowledge base for intelligent responses
without requiring OpenAI API for basic functionality.
"""

from typing import Dict, List, Any, Optional
import re
import os
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from smart_query_processor import SmartQueryProcessor, EnhancedQueryMatcher
    SMART_PROCESSOR_AVAILABLE = True
except ImportError:
    SMART_PROCESSOR_AVAILABLE = False


class QualityKnowledgeBase:
    """Built-in quality management knowledge for smart responses."""
    
    def __init__(self):
        self.knowledge = self._initialize_knowledge()
        self.patterns = self._initialize_patterns()
        
        # Initialize smart query processor if available
        if SMART_PROCESSOR_AVAILABLE:
            self.smart_processor = SmartQueryProcessor()
            self.query_matcher = EnhancedQueryMatcher()
            self.smart_mode = True
        else:
            self.smart_processor = None
            self.query_matcher = None
            self.smart_mode = False
    
    def _initialize_knowledge(self) -> Dict[str, Dict]:
        """Initialize comprehensive quality management knowledge."""
        return {
            "7qc_tools": {
                "title": "7 Quality Control (7QC) Tools",
                "content": """
The 7QC tools are fundamental statistical tools for quality improvement:

**1. Check Sheet**
- Purpose: Systematic data collection and defect tracking
- Use when: You need to collect and organize data
- Benefits: Standardized data collection, trend identification

**2. Histogram**
- Purpose: Shows frequency distribution of data
- Use when: Understanding process variation and capability
- Benefits: Visual representation of data patterns

**3. Pareto Chart**
- Purpose: Identifies vital few problems (80/20 rule)
- Use when: Prioritizing improvement efforts
- Benefits: Focuses resources on most impactful issues

**4. Cause & Effect Diagram (Fishbone/Ishikawa)**
- Purpose: Systematic root cause analysis
- Use when: Investigating problem causes
- Benefits: Comprehensive cause identification, team engagement

**5. Scatter Diagram**
- Purpose: Shows relationships between variables
- Use when: Testing correlations between factors
- Benefits: Identifies cause-effect relationships

**6. Control Chart**
- Purpose: Monitors process stability over time
- Use when: Ongoing process monitoring and control
- Benefits: Early detection of process changes

**7. Stratification**
- Purpose: Analyzes data by grouping similar items
- Use when: Comparing different groups or categories
- Benefits: Reveals hidden patterns in data
                """,
                "keywords": ["7qc", "quality control", "tools", "statistical", "basic tools"]
            },
            
            "defect_reduction": {
                "title": "Defect Reduction Strategy",
                "content": """
**Systematic Approach to Reduce Manufacturing Defects:**

**Phase 1: Data Collection (Week 1-2)**
- Use Check Sheets to track defect types, frequency, and location
- Collect data for at least 2 weeks to establish baseline
- Categories: Material, Machine, Method, Measurement, Environment, People

**Phase 2: Analysis (Week 3)**
- Create Pareto Chart to identify top 3-5 defect types
- Focus on defects causing 80% of problems
- Use Histograms to understand defect distribution patterns

**Phase 3: Root Cause Analysis (Week 4)**
- Cause & Effect Diagram for major defects
- 5 Whys technique for deeper investigation
- Scatter Diagrams to test relationships

**Phase 4: Solution Implementation (Week 5-8)**
- PDCA Cycle for systematic improvement
- Poka-Yoke (error proofing) techniques
- Standard Operating Procedures (SOPs)

**Phase 5: Control & Monitoring (Ongoing)**
- Control Charts for process monitoring
- Regular audits and reviews
- Continuous improvement culture

**Expected Results:** 40-60% defect reduction within 3 months
                """,
                "keywords": ["defect", "defects", "manufacturing", "reduce", "quality issues", "problems"]
            },
            
            "customer_satisfaction": {
                "title": "Customer Satisfaction Improvement",
                "content": """
**Customer Satisfaction Enhancement Strategy:**

**1. Voice of Customer (VoC) Collection**
- Surveys, interviews, focus groups
- Complaint analysis and feedback systems
- Social media monitoring
- Customer journey mapping

**2. Data Analysis Tools**
- Pareto Chart: Prioritize top customer issues
- Check Sheets: Track complaint categories
- Stratification: Analyze by customer segments
- Scatter Diagrams: Link satisfaction to specific factors

**3. Root Cause Analysis**
- Cause & Effect Diagram for major complaints
- 5 Whys for service failures
- Process mapping to identify pain points

**4. Improvement Actions**
- Service level agreements (SLAs)
- Employee training programs
- Process standardization
- Customer communication protocols

**5. Monitoring & Control**
- Customer satisfaction metrics (CSAT, NPS)
- Control Charts for key performance indicators
- Regular customer feedback loops
- Continuous improvement initiatives

**Key Metrics:**
- Customer Satisfaction Score (CSAT): Target >85%
- Net Promoter Score (NPS): Target >50
- Customer Retention Rate: Target >90%
- First Call Resolution: Target >80%
                """,
                "keywords": ["customer", "satisfaction", "service", "feedback", "complaints", "nps", "csat"]
            },
            
            "process_improvement": {
                "title": "Process Improvement Methodology",
                "content": """
**PDCA Cycle for Process Improvement:**

**PLAN (25% of effort)**
- Define problem clearly with data
- Set SMART objectives
- Analyze root causes using quality tools
- Develop improvement plan with timelines

**DO (25% of effort)**
- Implement on small scale (pilot)
- Train team members
- Execute according to plan
- Document all activities

**CHECK (25% of effort)**
- Measure results against objectives
- Use Control Charts for monitoring
- Analyze data for improvement verification
- Compare before/after performance

**ACT (25% of effort)**
- Standardize successful improvements
- Update procedures and training
- Share lessons learned
- Plan next improvement cycle

**Supporting Tools:**
- Kaizen events for rapid improvement
- Value Stream Mapping for workflow optimization
- Lean principles for waste elimination
- Six Sigma for data-driven improvements

**Success Factors:**
- Leadership commitment
- Employee engagement
- Data-driven decisions
- Continuous learning culture
                """,
                "keywords": ["process", "improvement", "pdca", "kaizen", "lean", "optimize", "efficiency"]
            },
            
            "dpdp_compliance": {
                "title": "DPDP (Data Protection) Compliance",
                "content": """
**Digital Personal Data Protection (DPDP) Compliance for Organizations:**

**Key Requirements:**
1. **Data Minimization**: Collect only necessary personal data
2. **Purpose Limitation**: Use data only for stated purposes
3. **Consent Management**: Obtain clear, informed consent
4. **Data Security**: Implement appropriate security measures
5. **Data Subject Rights**: Respect individual privacy rights

**Implementation Steps:**

**Phase 1: Assessment (Month 1)**
- Data mapping and inventory
- Privacy impact assessments
- Gap analysis against DPDP requirements
- Risk identification and evaluation

**Phase 2: Policy Development (Month 2)**
- Privacy policy creation
- Data handling procedures
- Consent management processes
- Incident response plans

**Phase 3: Technical Implementation (Month 3-4)**
- Security controls implementation
- Data encryption and access controls
- Monitoring and audit systems
- Staff training programs

**Phase 4: Ongoing Compliance (Ongoing)**
- Regular audits and assessments
- Policy updates and reviews
- Incident management
- Continuous improvement

**For Startups & MSMEs:**
- Start with basic compliance framework
- Use simplified templates and checklists
- Focus on high-risk data processing activities
- Leverage technology solutions for automation
                """,
                "keywords": ["dpdp", "data protection", "privacy", "compliance", "gdpr", "personal data"]
            },
            
            "six_sigma": {
                "title": "Six Sigma Methodology",
                "content": """
**Six Sigma DMAIC Process:**

**DEFINE (Month 1)**
- Project charter and scope
- Voice of Customer (VoC)
- Critical-to-Quality (CTQ) characteristics
- Project team formation

**MEASURE (Month 2)**
- Data collection plan
- Baseline performance measurement
- Measurement system analysis
- Process capability assessment

**ANALYZE (Month 3)**
- Root cause analysis
- Statistical analysis of data
- Process mapping and value stream analysis
- Hypothesis testing

**IMPROVE (Month 4-5)**
- Solution generation and selection
- Pilot implementation
- Design of Experiments (DOE)
- Risk assessment

**CONTROL (Month 6)**
- Control plan development
- Process monitoring systems
- Documentation and training
- Handover to process owner

**Benefits:**
- 99.99966% defect-free performance
- 3.4 defects per million opportunities
- Significant cost savings (typically 1-3% of revenue)
- Cultural transformation toward quality

**When to Use:**
- Complex, high-impact problems
- Data-rich environments
- Strategic improvement initiatives
- When statistical analysis is needed
                """,
                "keywords": ["six sigma", "dmaic", "statistical", "defects per million", "process capability"]
            },
            
            "root_cause_analysis": {
                "title": "Root Cause Analysis Techniques",
                "content": """
**Root Cause Analysis Toolkit:**

**1. 5 Whys Technique**
- Start with problem statement
- Ask "Why?" five times
- Dig deeper with each question
- Stop when you reach actionable root cause
- Example: Defect → Why? → Machine settings → Why? → No calibration → Why? → No schedule → Why? → No procedure → Why? → No training

**2. Cause & Effect Diagram (Fishbone)**
- Categories: Man, Machine, Material, Method, Environment, Measurement
- Brainstorm all potential causes
- Use team-based approach
- Verify causes with data

**3. Fault Tree Analysis**
- Top-down logical analysis
- Start with undesired event
- Work backward to find causes
- Use boolean logic (AND/OR gates)

**4. Current Reality Tree**
- Systems thinking approach
- Identify core problems
- Map cause-effect relationships
- Find leverage points for improvement

**Best Practices:**
- Use multiple techniques together
- Involve cross-functional teams
- Support with data and evidence
- Focus on process, not people
- Document lessons learned
- Implement permanent solutions

**Common Mistakes to Avoid:**
- Stopping at symptoms
- Blaming individuals
- Not validating root causes
- Implementing quick fixes only
                """,
                "keywords": ["root cause", "analysis", "5 whys", "fishbone", "investigate", "problem solving"]
            }
        }
    
    def _initialize_patterns(self) -> List[Dict]:
        """Initialize pattern matching for query understanding."""
        return [
            {
                "patterns": [r"7qc", r"seven.*quality", r"basic.*tools", r"quality.*control.*tools"],
                "topic": "7qc_tools"
            },
            {
                "patterns": [r"defect", r"manufacturing.*problem", r"quality.*issue", r"reduce.*defect"],
                "topic": "defect_reduction"
            },
            {
                "patterns": [r"customer.*satisfaction", r"customer.*feedback", r"service.*quality", r"nps", r"csat"],
                "topic": "customer_satisfaction"
            },
            {
                "patterns": [r"process.*improve", r"pdca", r"kaizen", r"lean", r"optimize.*process"],
                "topic": "process_improvement"
            },
            {
                "patterns": [r"dpdp", r"data.*protection", r"privacy", r"compliance", r"gdpr"],
                "topic": "dpdp_compliance"
            },
            {
                "patterns": [r"six.*sigma", r"dmaic", r"statistical.*quality", r"process.*capability"],
                "topic": "six_sigma"
            },
            {
                "patterns": [r"root.*cause", r"5.*whys", r"fishbone", r"investigate", r"problem.*solving"],
                "topic": "root_cause_analysis"
            }
        ]
    
    def get_smart_response(self, query: str) -> str:
        """Get intelligent response using smart query processing."""
        if self.smart_mode and self.smart_processor:
            return self._get_enhanced_response(query)
        else:
            return self._get_basic_response(query)
    
    def _get_enhanced_response(self, query: str) -> str:
        """Enhanced response using smart query processor."""
        # Analyze the query
        analysis = self.smart_processor.analyze_query(query)
        
        # High confidence - return specific answer
        if analysis["confidence"] > 0.7 and analysis["best_topic"]:
            topic_key = analysis["best_topic"]
            if topic_key in self.knowledge:
                content = self.knowledge[topic_key]
                return self._format_enhanced_response(content, analysis)
        
        # Medium confidence - try fuzzy matching
        elif analysis["confidence"] > 0.4:
            fuzzy_result = self._try_fuzzy_matching(query, analysis)
            if fuzzy_result:
                return fuzzy_result
        
        # Low confidence - return smart fallback
        return self.smart_processor.get_smart_fallback(query)
    
    def _get_basic_response(self, query: str) -> str:
        """Basic response using pattern matching (fallback)."""
        query_lower = query.lower()
        
        # Find matching topic
        for pattern_group in self.patterns:
            for pattern in pattern_group["patterns"]:
                if re.search(pattern, query_lower):
                    topic = pattern_group["topic"]
                    if topic in self.knowledge:
                        return f"## {self.knowledge[topic]['title']}\n\n{self.knowledge[topic]['content']}"
        
        # Default comprehensive response
        return self._get_default_response(query)
    
    def _format_enhanced_response(self, content: Dict, analysis: Dict) -> str:
        """Format response based on intent and content."""
        intent = analysis["intent"]
        title = content["title"]
        base_content = content["content"]
        
        if intent == "definition":
            return f"""## {title}

**Definition & Overview:**
{self._extract_definition(base_content)}

**Detailed Information:**
{base_content}

💡 **Quick Tips:**
{self._generate_tips(content)}

🔗 **Related Topics:**
{self._get_related_suggestions(analysis["best_topic"])}
            """
        
        elif intent == "how_to":
            return f"""## How to Implement {title}

**Step-by-Step Guide:**
{self._extract_steps(base_content)}

**Implementation Details:**
{base_content}

⚠️ **Key Considerations:**
{self._generate_considerations(content)}

📚 **Next Steps:**
{self._get_related_suggestions(analysis["best_topic"])}
            """
        
        elif intent == "benefits":
            return f"""## Benefits of {title}

**Key Advantages:**
{self._extract_benefits(base_content)}

**Complete Information:**
{base_content}

💡 **Implementation Tips:**
{self._generate_tips(content)}
            """
        
        else:
            # Default enhanced format
            return f"""## {title}

{base_content}

**🎯 Key Takeaways:**
{self._generate_key_points(content)}

**🚀 Quick Actions:**
{self._generate_quick_actions(analysis["best_topic"])}

**🔗 Related Questions:**
{self._get_related_suggestions(analysis["best_topic"])}
            """
    
    def _try_fuzzy_matching(self, query: str, analysis: Dict) -> Optional[str]:
        """Try fuzzy matching against knowledge base."""
        if not self.query_matcher:
            return None
        
        # Get all knowledge titles and keywords
        candidates = []
        for topic_key, content in self.knowledge.items():
            candidates.append(content["title"])
            candidates.extend(content.get("keywords", []))
        
        # Perform fuzzy matching
        matches = self.query_matcher.fuzzy_match(query, candidates)
        
        if matches and matches[0][1] > 0.6:  # Good match found
            # Find corresponding topic
            best_match = matches[0][0]
            for topic_key, content in self.knowledge.items():
                if (best_match == content["title"] or 
                    best_match in content.get("keywords", [])):
                    return f"""## {content['title']} (Matched: "{best_match}")

{content['content']}

💡 **Note:** I found this based on similarity to your query. If this isn't what you were looking for, try asking:
{self._get_related_suggestions(topic_key)}
                    """
        
        return None
    
    def _extract_definition(self, content: str) -> str:
        """Extract definition from content."""
        lines = content.strip().split('\n')
        definition_lines = []
        
        for line in lines[:5]:  # First few lines usually contain definition
            if line.strip() and not line.startswith('**') and not line.startswith('#'):
                definition_lines.append(line.strip())
        
        return "\n".join(definition_lines) if definition_lines else "Key quality management concept for process improvement."
    
    def _extract_steps(self, content: str) -> str:
        """Extract steps from content."""
        steps = []
        lines = content.split('\n')
        
        for line in lines:
            if re.match(r'^\*?\*?\s*\d+\.|\*?\*?\s*Step\s*\d+|^\*?\*?\s*Phase\s*\d+', line):
                steps.append(line.strip())
        
        if steps:
            return "\n".join(steps)
        else:
            return "1. Analyze current situation\n2. Identify improvement opportunities\n3. Implement changes\n4. Monitor results"
    
    def _extract_benefits(self, content: str) -> str:
        """Extract benefits from content."""
        benefits = []
        lines = content.split('\n')
        
        for line in lines:
            if 'benefit' in line.lower() or 'advantage' in line.lower() or line.strip().startswith('- '):
                benefits.append(line.strip())
        
        if benefits:
            return "\n".join(benefits[:5])  # Top 5 benefits
        else:
            return "- Improved quality and efficiency\n- Reduced costs and waste\n- Enhanced customer satisfaction\n- Better process control"
    
    def _generate_tips(self, content: Dict) -> str:
        """Generate practical tips."""
        topic_tips = {
            "7qc_tools": [
                "Start with check sheets for data collection",
                "Use Pareto charts to prioritize problems",
                "Implement control charts for ongoing monitoring"
            ],
            "defect_reduction": [
                "Focus on prevention rather than detection",
                "Engage operators in problem identification",
                "Document all improvements for sustainability"
            ],
            "process_improvement": [
                "Map current state before making changes",
                "Involve stakeholders in the improvement process",
                "Measure results to validate improvements"
            ]
        }
        
        # Try to match topic
        for key, tips in topic_tips.items():
            if key in content.get("title", "").lower():
                return "\n".join([f"- {tip}" for tip in tips])
        
        return "- Start with small pilot implementations\n- Measure before and after results\n- Get stakeholder buy-in early"
    
    def _generate_considerations(self, content: Dict) -> str:
        """Generate key considerations."""
        return """- Ensure adequate training for team members
- Allocate sufficient time for proper implementation
- Have management support and commitment
- Plan for resistance to change management"""
    
    def _generate_key_points(self, content: Dict) -> str:
        """Generate key takeaway points."""
        return """- Focus on data-driven decision making
- Implement systematic approaches
- Ensure continuous monitoring and improvement
- Engage all stakeholders in the process"""
    
    def _generate_quick_actions(self, topic: str) -> str:
        """Generate quick actionable items."""
        actions = {
            "7qc_tools": [
                "Download check sheet templates",
                "Practice creating Pareto charts",
                "Set up basic control charts"
            ],
            "defect_reduction": [
                "Start collecting defect data",
                "Identify top 3 defect types",
                "Form improvement team"
            ],
            "process_improvement": [
                "Map your current process",
                "Identify bottlenecks",
                "Plan improvement pilot"
            ]
        }
        
        topic_actions = actions.get(topic, [
            "Assess current situation",
            "Define improvement goals",
            "Create action plan"
        ])
        
        return "\n".join([f"- {action}" for action in topic_actions])
    
    def _get_related_suggestions(self, topic: str) -> str:
        """Get related question suggestions."""
        if self.smart_processor:
            suggestions = self.smart_processor.suggest_related_queries("", topic)
            return "\n".join([f"- \"{suggestion}\"" for suggestion in suggestions[:3]])
        
        # Fallback suggestions
        return """- "What are the implementation steps?"
- "What tools do I need?"
- "How do I measure success?\""""
    
    def _get_default_response(self, query: str) -> str:
        """Provide comprehensive default response."""
        return f"""
## Quality Management Guidance

Based on your query: "{query}"

**I can help you with:**

🔧 **Quality Tools & Techniques:**
- 7QC Tools (Check Sheet, Pareto Chart, Control Chart, etc.)
- Six Sigma DMAIC methodology
- Root cause analysis techniques
- Process improvement methods

📊 **Specific Applications:**
- Defect reduction strategies
- Customer satisfaction improvement
- Process optimization
- Data analysis and monitoring

📋 **Compliance & Standards:**
- DPDP data protection compliance
- Quality management systems
- Best practices implementation

**Popular Topics:**
- "What are the 7QC tools?" - Learn about fundamental quality tools
- "How to reduce defects?" - Get systematic defect reduction strategy
- "Improve customer satisfaction" - Customer-focused improvement approach
- "DPDP compliance guide" - Data protection implementation

**Try asking more specific questions like:**
- "What tools help with root cause analysis?"
- "How to implement process improvement?"
- "Steps for DPDP compliance?"

Would you like me to explain any of these topics in detail?
        """
    
    def search_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query."""
        query_lower = query.lower()
        found_keywords = []
        
        for topic, content in self.knowledge.items():
            for keyword in content["keywords"]:
                if keyword in query_lower:
                    found_keywords.append(keyword)
        
        return found_keywords
