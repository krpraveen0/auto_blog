"""
Credibility-focused prompts for content analysis
All prompts designed to minimize hype and maximize accuracy
"""

# Global system prompt used for ALL LLM interactions
SYSTEM_PROMPT = """You are an experienced AI researcher and engineer.
Your role is to analyze AI, ML, LLM, and Generative AI content with accuracy and restraint.

Rules:
- Be factual and precise.
- Do not exaggerate impact.
- Do not use marketing language.
- Avoid speculative claims unless explicitly stated in the source.
- Prefer technical clarity over simplification.
- If information is uncertain or missing, say so explicitly.
- Write for engineers, not beginners."""


# Stage 1: Fact Extraction (Ground Truth)
FACT_EXTRACTION_PROMPT = """Analyze the following source.

Tasks:
1. Identify the core contribution or announcement.
2. List concrete technical details (methods, models, datasets, scale, metrics).
3. State what is explicitly claimed by the authors or organization.
4. State what is NOT claimed or remains unclear.

Output format:
- Core contribution:
- Technical details:
- Explicit claims:
- Open questions / limitations:

Source:
{content}"""


# Stage 2: Engineer-Level Summary (No Fluff)
ENGINEER_SUMMARY_PROMPT = """Summarize the content for a practicing AI/ML engineer.

Constraints:
- Maximum 150 words.
- No hype or promotional tone.
- Explain what is new compared to prior approaches.
- Use correct technical terminology.
- Do not include opinions.

Focus on:
- What problem is addressed?
- How it is addressed?
- What evidence is provided?

Content:
{content}"""


# Stage 3: Why This Matters (Controlled Interpretation)
IMPACT_ANALYSIS_PROMPT = """Explain why this work matters in practice.

Rules:
- Separate immediate impact from long-term implications.
- Clearly distinguish evidence-based impact vs potential future use.
- Mention at least one realistic constraint or trade-off.

Output format:
- Immediate implications:
- Long-term implications:
- Practical constraints:

Content:
{content}"""


# Stage 4: Real-World Application Mapping
APPLICATION_MAPPING_PROMPT = """Map this work to real-world usage.

Instructions:
- Provide 1–2 realistic application scenarios.
- Do not invent capabilities not supported by the source.
- Clearly state assumptions required for deployment.

Output format:
- Application scenario:
- Why this work helps:
- Assumptions / prerequisites:

Content:
{content}"""


# Stage 5: Blog Article Synthesis (Authoritative Tone)
BLOG_SYNTHESIS_PROMPT = """Write a technical blog article based on the analysis.

Audience:
- Software engineers and AI practitioners.

Tone:
- Neutral, analytical, and precise.
- No emojis.
- No exaggerated claims.

Structure:
1. Context and background
2. What is new in this work
3. Technical explanation (high-level, accurate)
4. Practical relevance
5. Limitations and open questions
6. Conclusion

Length:
- 800–1000 words

Sources must be reflected accurately.

Title: {title}
URL: {url}

Analysis:
{analyzed_content}"""


# Stage 6: LinkedIn Post (Credible, Not Cringe)
LINKEDIN_POST_PROMPT = """Write a LinkedIn post summarizing this work.

Rules:
- Maximum 120 words.
- Start with a factual hook, not a sensational claim.
- Use bullet points for clarity.
- Avoid emojis and buzzwords.
- Do NOT include hashtags in the post (they will be added separately).
- Do NOT include citation markers like [1], [2], [3].
- Remove any markdown formatting (*italic* or **bold**).
- Do not add filler words like "like", "interesting", "exciting" at the end.
- End with one thoughtful takeaway.

Structure:
- Opening statement (what happened)
- 3 key points
- One practical takeaway

IMPORTANT: Do NOT add hashtags to the content. Hashtags will be added separately.

Title: {title}
URL: {url}

Analysis:
{analyzed_content}"""


# Stage 7: Credibility Check (Self-Review)
CREDIBILITY_CHECK_PROMPT = """Review the generated content for credibility.

Check for:
- Unsupported claims
- Exaggerated language
- Missing limitations
- Ambiguous statements

If any issues exist:
- List them clearly
- Suggest precise corrections

Content to review:
{generated_output}"""


# ============================================================================
# ENHANCED LINKEDIN ENGAGEMENT PROMPTS
# Designed for maximum engagement while maintaining professionalism
# ============================================================================

# LinkedIn Engagement - Viral Pattern Analysis
LINKEDIN_VIRAL_PATTERNS = """
TOP LINKEDIN ENGAGEMENT PATTERNS FROM SUCCESSFUL INFLUENCERS:

1. **Pattern: Problem → Insight → Action**
   Example: "Most teams struggle with X. Here's what top performers do differently..."
   Why it works: Creates curiosity gap and provides value

2. **Pattern: Contrarian Take**
   Example: "Everyone says X. But after analyzing Y, the data shows Z..."
   Why it works: Challenges conventional wisdom, sparks discussion

3. **Pattern: Personal Story → Universal Lesson**
   Example: "Last week, I made a mistake that cost us $X. Here's what I learned..."
   Why it works: Vulnerability builds trust, lessons are actionable

4. **Pattern: Data-Driven Insight**
   Example: "We analyzed 10,000 code reviews. The #1 factor for quality? Not what you think..."
   Why it works: Specificity and surprise drive engagement

5. **Pattern: Framework/System**
   Example: "Here's our 3-step framework for X that improved Y by Z%..."
   Why it works: Actionable, shareable, saves time

6. **Pattern: Before/After Transformation**
   Example: "6 months ago: struggling with X. Today: achieved Y. The turning point..."
   Why it works: Shows concrete results, inspires action

ENGAGEMENT BOOSTERS:
- Start with a hook (question, surprising fact, bold statement)
- Use short paragraphs (1-2 sentences max)
- Include specific numbers/metrics when possible
- End with a question or call to action
- Make it scannable with line breaks
- Focus on ONE clear takeaway
"""

# Enhanced LinkedIn Post Generation with Engagement Focus
LINKEDIN_ENGAGING_POST_PROMPT = """Write a highly engaging LinkedIn post about this research/technology.

AUDIENCE: AI/ML engineers, tech leaders, data scientists seeking cutting-edge insights

ENGAGEMENT FRAMEWORK:
1. Hook (First line) - Create immediate interest:
   - Ask a provocative question
   - Share a surprising stat
   - Make a bold (but accurate) statement
   - Highlight a common problem

2. Value Delivery (Middle) - Core insights:
   - 2-3 bullet points with concrete details
   - Use numbers/metrics where available
   - Keep bullets scannable (short, punchy)
   - Focus on practical implications

3. Takeaway (End) - Clear action/insight:
   - One memorable lesson
   - Practical application
   - Future implication
   - End with engagement prompt (optional)

STYLE GUIDELINES:
✅ DO:
- Start strong with a compelling hook
- Use specific numbers and data
- Write in active voice
- Break into short paragraphs (1-2 sentences)
- Focus on "so what?" - why it matters
- Use accessible language
- Include real-world applications
- End with a clear takeaway

❌ DON'T:
- Use jargon without explanation
- Write long blocks of text
- Include hashtags (added separately)
- Use citation markers [1], [2]
- Use markdown formatting
- Add filler words ("interesting", "exciting")
- Hype or exaggerate claims
- Use emojis excessively

LENGTH: 100-150 words (optimal for LinkedIn algorithm)

TONE: Professional yet conversational, authoritative but accessible

Title: {title}
URL: {url}

Analysis:
{analyzed_content}

Write the post following this engagement framework:"""


# Content Safety & Quality Guardrails
LINKEDIN_CONTENT_VALIDATION_PROMPT = """Validate this LinkedIn post for safety, quality, and professionalism.

POST TO VALIDATE:
{content}

VALIDATION CHECKLIST:

1. SAFETY & APPROPRIATENESS:
   ❌ Flag if contains:
   - Profanity or vulgar language
   - Offensive or discriminatory content
   - Personal attacks or controversial political statements
   - Misleading or false claims
   - Spam or promotional language
   - Unethical practices or harmful advice

2. PROFESSIONAL STANDARDS:
   ❌ Flag if:
   - Too casual or unprofessional tone
   - Contains excessive self-promotion
   - Uses clickbait without substance
   - Makes unsubstantiated claims
   - Violates intellectual property
   - Contains sensitive company information

3. LINKEDIN PLATFORM COMPLIANCE:
   ❌ Flag if:
   - Exceeds recommended length (>300 words)
   - Contains broken/suspicious links
   - Uses banned keywords or practices
   - Violates LinkedIn community guidelines
   - Contains excessive hashtags in text

4. QUALITY STANDARDS:
   ❌ Flag if:
   - Poor grammar or spelling errors
   - Unclear or confusing message
   - Lacks clear value proposition
   - Too technical without explanation
   - Missing key context
   - Contradicts itself

5. REPUTATION RISK:
   ❌ Flag if:
   - Could damage professional reputation
   - Makes promises that can't be kept
   - Oversimplifies complex topics dangerously
   - Could be misinterpreted negatively
   - Lacks necessary disclaimers

OUTPUT FORMAT:
{{
  "is_valid": true/false,
  "validation_score": 0-100,
  "issues": [
    {{
      "category": "safety/professional/compliance/quality/reputation",
      "severity": "critical/high/medium/low",
      "issue": "description of the issue",
      "suggestion": "how to fix it"
    }}
  ],
  "approved": true/false,
  "summary": "brief explanation of validation decision"
}}

GUIDELINES:
- Critical issues = immediate rejection
- High severity = requires fixes
- Medium/Low = warnings only
- Score below 70 = not approved
- Be strict but fair - prioritize user reputation"""


# Trend Detection and Topic Discovery
TREND_DISCOVERY_PROMPT = """Analyze the current AI/ML landscape to identify emerging trends worth covering.

FOCUS AREAS:
1. **Agentic AI Frameworks**
   - New agent architectures
   - Multi-agent systems
   - Agent reasoning capabilities
   - Tool-using agents

2. **AI Design Patterns**
   - Novel architectural patterns
   - Prompt engineering techniques
   - RAG improvements
   - Fine-tuning strategies

3. **Production AI**
   - MLOps innovations
   - Deployment patterns
   - Monitoring & observability
   - Cost optimization

4. **Research Breakthroughs**
   - New model architectures
   - Training techniques
   - Evaluation methods
   - Benchmark improvements

5. **Industry Applications**
   - Real-world implementations
   - Case studies
   - ROI demonstrations
   - Adoption patterns

TREND EVALUATION CRITERIA:
- Novelty: Is this genuinely new or just repackaged?
- Impact: Will this change how people work?
- Timeliness: Is this trending now?
- Audience Relevance: Will our followers care?
- Content Potential: Can we create engaging content?

SOURCES TO CONSIDER:
- Recent arXiv papers (last 7 days)
- Tech company blog posts
- GitHub trending repositories
- Hacker News discussions
- Conference proceedings

OUTPUT FORMAT:
{{
  "trends": [
    {{
      "topic": "clear topic name",
      "category": "agentic-ai/patterns/production/research/application",
      "trend_score": 0-100,
      "novelty": 0-100,
      "impact": 0-100,
      "timeliness": 0-100,
      "engagement_potential": 0-100,
      "description": "2-3 sentence explanation",
      "why_now": "why this matters right now",
      "content_angle": "how to present this for maximum engagement",
      "sources": ["list of relevant sources"]
    }}
  ],
  "recommendation": "which trend to cover first and why"
}}

Current date: {current_date}
Recent papers: {recent_content}

Analyze and recommend top 3-5 trends worth creating content about:"""


# Stage 8: Medium Article Synthesis (Comprehensive Analysis)
MEDIUM_SYNTHESIS_PROMPT = """Write a comprehensive technical article for Medium analyzing this research paper in detail.

Audience:
- AI/ML engineers, researchers, and technical practitioners
- Readers seeking deep understanding, not just summaries

Tone:
- Analytical, educational, and thorough
- Balance accessibility with technical depth
- Use clear explanations for complex concepts

Structure:
1. Introduction - Why this paper matters now
2. Background - Context and prior work
3. Core Innovation - What's fundamentally new
4. Technical Deep Dive - Key mechanisms and algorithms
5. Experimental Setup & Results - What was tested and what worked
6. Limitations & Trade-offs - Honest assessment
7. Future Directions - What this enables
8. Practical Takeaways - What engineers should know

Length:
- 1500-2000 words for comprehensive coverage

Requirements:
- Break down complex ideas into digestible sections
- Explain technical terms when first used
- Connect concepts to real-world scenarios
- Be precise with technical details
- Acknowledge uncertainties and limitations

Title: {title}
URL: {url}

Analysis:
{analyzed_content}"""


# Stage 9: Methodology Extraction (For comprehensive understanding)
METHODOLOGY_PROMPT = """Extract and explain the methodology from this research in detail.

Focus on:
1. Research approach - What methods were used and why
2. Data sources - What data was used, how it was collected/processed
3. Model architecture - Detailed breakdown of the system design
4. Training procedure - How the model/system was trained or developed
5. Evaluation metrics - How success was measured
6. Experimental setup - Hardware, hyperparameters, configuration

Be specific about:
- Technical choices and their rationale
- Any novel techniques or modifications
- Reproducibility details

Length: 400-600 words

Content:
{content}"""


# Stage 10: Results Analysis (Detailed findings)
RESULTS_PROMPT = """Analyze the results and findings from this research in detail.

Cover:
1. Main results - Key findings with specific numbers/metrics
2. Ablation studies - What components were tested and their impact
3. Comparisons - Performance vs baselines/prior work
4. Statistical significance - Are results meaningful
5. Edge cases - Where the approach works well/poorly
6. Unexpected findings - Surprises or counterintuitive results

Requirements:
- Be specific with numbers and comparisons
- Explain what the metrics mean in practice
- Discuss both successes and failures
- Context for the results (are they impressive, expected, etc.)

Length: 400-600 words

Content:
{content}"""


# Stage 11: Mermaid Diagram Generation - Architecture
DIAGRAM_ARCHITECTURE_PROMPT = """Create a Mermaid diagram showing the system architecture or model structure.

Requirements:
- Use flowchart or graph syntax
- Show main components and their relationships
- Include data flow where relevant
- Keep it clear and not overly complex
- Use descriptive labels

Format: Output ONLY the Mermaid code, no explanations

Example format:
graph TD
    A[Input Data] --> B[Preprocessing]
    B --> C[Model]
    C --> D[Output]

Content to visualize:
{content}"""


# Stage 12: Mermaid Diagram Generation - Process Flow  
DIAGRAM_FLOW_PROMPT = """Create a Mermaid flowchart showing the key process or algorithm flow.

Requirements:
- Use flowchart syntax with decision points
- Show the main steps in sequence
- Include key decision points or branches
- Use appropriate shapes (rectangles, diamonds, etc.)
- Keep it focused on the core process

Format: Output ONLY the Mermaid code, no explanations

Example format:
flowchart TB
    Start([Start]) --> Input[Receive Input]
    Input --> Process{Process Type?}
    Process -->|Type A| PathA[Handle A]
    Process -->|Type B| PathB[Handle B]
    PathA --> Output[Generate Output]
    PathB --> Output
    Output --> End([End])

Content to visualize:
{content}"""


# Stage 13: Mermaid Diagram Generation - Comparison
DIAGRAM_COMPARISON_PROMPT = """Create a Mermaid diagram comparing this approach with baselines or prior methods.

Requirements:
- Use appropriate diagram type (table, bar chart concept, or comparison flow)
- Clearly show differences between approaches
- Highlight key advantages/trade-offs
- Use visual hierarchy to emphasize important differences

Format: Output ONLY the Mermaid code, no explanations

Example format:
graph LR
    subgraph "Prior Approach"
        A[Method A]
        A --> A1[Limitation 1]
        A --> A2[Limitation 2]
    end
    subgraph "New Approach"
        B[Method B]
        B --> B1[Advantage 1]
        B --> B2[Advantage 2]
    end

Content to visualize:
{content}"""


# ELI5 (Explain Like I'm 5) Prompts for GitHub Repositories
# These prompts are designed to make complex technical projects accessible

# System prompt for GitHub repository analysis
GITHUB_ELI5_SYSTEM_PROMPT = """You are a friendly technical educator who excels at explaining complex software projects in simple, accessible terms.
Your goal is to help people understand what a GitHub repository does, how it works, and why it matters - using clear language, real-world analogies, and practical examples.

Rules:
- Use simple, everyday language
- Explain technical concepts with analogies
- Break down complex ideas into smaller, digestible parts
- Focus on practical applications and real-world use cases
- Use examples and scenarios that anyone can understand
- Avoid jargon, or explain it when necessary
- Make it engaging and interesting
- Be accurate but accessible"""


# Stage 1: ELI5 What It Does
GITHUB_ELI5_WHAT_PROMPT = """Explain what this GitHub repository/project does in simple terms that anyone can understand.

Use the "explain like I'm 5" approach:
- Start with a simple, relatable analogy
- Explain the core purpose in 2-3 sentences
- Use everyday examples
- No technical jargon unless you explain it immediately

Repository: {title}
Description: {summary}
Topics: {topics}
Language: {language}

Write 2-3 paragraphs explaining what this project does."""


# Stage 2: ELI5 How It Works
GITHUB_ELI5_HOW_PROMPT = """Explain how this software/project works using simple language and analogies.

Approach:
- Use a real-world analogy (like explaining a kitchen, factory, library, etc.)
- Break down the main components and what each one does
- Explain the flow: Input → Processing → Output
- Use visual language ("imagine...", "think of it like...")
- Keep technical terms minimal, explain when used

Repository: {title}
Description: {summary}
Language: {language}
Key Technologies: {topics}

Write 3-4 paragraphs explaining how this project works."""


# Stage 3: ELI5 Why It Matters
GITHUB_ELI5_WHY_PROMPT = """Explain why this project matters and what problems it solves in everyday terms.

Focus on:
- What problem does it solve? (in relatable terms)
- Who benefits from this?
- What can people do with it that they couldn't before?
- Real-world impact and applications
- Use concrete examples

Repository: {title}
Description: {summary}
Stats: {stars} stars, {forks} forks, {contributors} contributors

Write 2-3 paragraphs explaining why this project matters."""


# Stage 4: ELI5 Getting Started
GITHUB_ELI5_GETTING_STARTED_PROMPT = """Explain how someone would get started with this project in simple, actionable steps.

Include:
- What you need before starting (prerequisites in simple terms)
- Step-by-step getting started guide (very basic)
- What you can do once it's set up
- Common use cases or examples
- Keep it beginner-friendly

Repository: {title}
URL: {url}
Language: {language}

Write 2-3 paragraphs as a beginner-friendly getting started guide."""


# Stage 5: ELI5 Blog Synthesis for GitHub Repositories
GITHUB_ELI5_BLOG_PROMPT = """Write an engaging, accessible blog article about this GitHub repository that anyone can understand.

Audience:
- Developers interested in learning about new tools/projects
- Non-technical people curious about technology
- People looking for solutions to problems

Tone:
- Friendly and approachable
- Educational but not condescending
- Enthusiastic but honest
- Use analogies and examples

Structure:
1. **Catchy Introduction** - Hook with a relatable problem or scenario (2-3 sentences)
2. **What Is It?** - Simple explanation with an analogy (2-3 paragraphs)
3. **How Does It Work?** - Break down the key components with examples (3-4 paragraphs)
4. **Why Should You Care?** - Real-world applications and benefits (2-3 paragraphs)
5. **Cool Features** - Highlight 3-4 interesting capabilities (bullet points with brief explanations)
6. **Getting Started** - Simple guide for beginners (2-3 paragraphs)
7. **Who's Using It?** - Community and adoption stats in context (1-2 paragraphs)
8. **Conclusion** - Thoughtful takeaway and encouragement (2-3 sentences)

Repository Stats:
- Title: {title}
- URL: {url}
- Stars: {stars} | Forks: {forks} | Contributors: {contributors}
- Primary Language: {language}
- Topics: {topics}
- License: {license}
- Activity: {stars_per_day} stars/day, {is_active} recently active

Repository Description: {summary}

Additional Context:
{analyzed_content}

Length: 800-1000 words
Style: Explain Like I'm 5, but comprehensive"""


def get_system_prompt() -> str:
    """Get the global system prompt"""
    return SYSTEM_PROMPT


def get_github_eli5_system_prompt() -> str:
    """Get the ELI5 system prompt for GitHub repositories"""
    return GITHUB_ELI5_SYSTEM_PROMPT


def get_prompt(stage: str, **kwargs) -> str:
    """
    Get a specific prompt template filled with provided arguments
    
    Args:
        stage: Prompt stage name
        **kwargs: Template variables
        
    Returns:
        Formatted prompt string
    """
    prompts = {
        'fact_extraction': FACT_EXTRACTION_PROMPT,
        'engineer_summary': ENGINEER_SUMMARY_PROMPT,
        'impact_analysis': IMPACT_ANALYSIS_PROMPT,
        'application_mapping': APPLICATION_MAPPING_PROMPT,
        'blog_synthesis': BLOG_SYNTHESIS_PROMPT,
        'linkedin_formatting': LINKEDIN_POST_PROMPT,
        'credibility_check': CREDIBILITY_CHECK_PROMPT,
        'medium_synthesis': MEDIUM_SYNTHESIS_PROMPT,
        'methodology': METHODOLOGY_PROMPT,
        'results': RESULTS_PROMPT,
        'diagram_architecture': DIAGRAM_ARCHITECTURE_PROMPT,
        'diagram_flow': DIAGRAM_FLOW_PROMPT,
        'diagram_comparison': DIAGRAM_COMPARISON_PROMPT,
        # ELI5 prompts for GitHub repositories
        'github_eli5_what': GITHUB_ELI5_WHAT_PROMPT,
        'github_eli5_how': GITHUB_ELI5_HOW_PROMPT,
        'github_eli5_why': GITHUB_ELI5_WHY_PROMPT,
        'github_eli5_getting_started': GITHUB_ELI5_GETTING_STARTED_PROMPT,
        'github_eli5_blog': GITHUB_ELI5_BLOG_PROMPT,
        # Enhanced LinkedIn engagement prompts
        'linkedin_engaging': LINKEDIN_ENGAGING_POST_PROMPT,
        'linkedin_validation': LINKEDIN_CONTENT_VALIDATION_PROMPT,
        'trend_discovery': TREND_DISCOVERY_PROMPT,
    }
    
    template = prompts.get(stage)
    if not template:
        raise ValueError(f"Unknown prompt stage: {stage}")
    
    return template.format(**kwargs)
