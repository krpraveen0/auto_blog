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
- End with one thoughtful takeaway.

Structure:
- Opening statement (what happened)
- 3 key points
- One practical takeaway

Hashtags:
- Use 3–5 relevant technical hashtags only.

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
        'credibility_check': CREDIBILITY_CHECK_PROMPT
    }
    
    template = prompts.get(stage)
    if not template:
        raise ValueError(f"Unknown prompt stage: {stage}")
    
    return template.format(**kwargs)
