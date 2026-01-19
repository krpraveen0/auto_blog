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


def get_system_prompt() -> str:
    """Get the global system prompt"""
    return SYSTEM_PROMPT


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
        'diagram_comparison': DIAGRAM_COMPARISON_PROMPT
    }
    
    template = prompts.get(stage)
    if not template:
        raise ValueError(f"Unknown prompt stage: {stage}")
    
    return template.format(**kwargs)
