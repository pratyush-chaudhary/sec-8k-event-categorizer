"""String constants for LLM prompt templates."""

# Basic classification prompt template
BASIC_CLASSIFICATION_TEMPLATE = """Classify the following 8-K filing event:

{text}

Choose from these categories:
{event_types}

Please provide your response in this exact structure:

REASONING:
[Provide a clear explanation of your analysis, including:
- What specific event is being reported
- Key factors that led to your classification decision
- Why this event is or isn't relevant for investors]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your analysis:"""

# Detailed classification prompt template  
DETAILED_CLASSIFICATION_TEMPLATE = """You are an expert financial analyst. Classify the following 8-K filing event:

Filing Content:
{text}

Event Categories:
{event_descriptions}

Instructions:
1. Read the filing content carefully
2. Identify the main business event being reported
3. Choose the most appropriate category from the list above
4. Determine if this event is relevant/significant for investors

An event is RELEVANT if it could materially impact:
- Stock price
- Company's financial performance
- Business operations
- Competitive position
- Strategic direction

An event is NOT RELEVANT if it's:
- Routine administrative filing
- Minor operational change
- Scheduled/expected announcement
- Immaterial to business performance

Please provide your response in this exact structure:

REASONING:
[Provide a comprehensive analysis including:
- Summary of the key event being reported
- Analysis of which category best fits and why
- Assessment of materiality and investor impact
- Justification for relevance determination]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your analysis:"""

# Chain of thought prompt template
CHAIN_OF_THOUGHT_TEMPLATE = """Analyze this 8-K filing step by step:

Filing Content:
{text}

Available Categories:
{event_types}

Please provide your response in this exact structure:

REASONING:
Step 1: Identify the key facts
- What specific event is being reported?
- Who are the parties involved?
- What are the financial/business implications?

Step 2: Match to category
- Which category best fits this event?
- Why does it fit this category better than others?

Step 3: Assess significance
- Could this materially impact the company's business?
- Would investors consider this important?
- Is this routine or exceptional?

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your step-by-step analysis:"""

# Few shot prompt template
FEW_SHOT_TEMPLATE = """Classify 8-K filing events into these categories:
{event_types}

Here are some examples of the expected format:

{examples_text}

Now classify this filing using the same structure:

Text: {text}

Please provide your response in this exact structure:

REASONING:
[Your detailed analysis here]

CLASSIFICATION:
Event Type: [Category], Relevant: [true/false]

Begin your analysis:"""

# Validation prompt template
VALIDATION_TEMPLATE = """Please validate this event classification:

Original Filing:
{text}

Proposed Classification: {classification}

Valid Categories: {event_types}

Please provide your response in this exact structure:

REASONING:
[Analyze the following questions:
1. Is the event type correct?
2. Is the relevance assessment appropriate?
3. Does the classification make logical sense?
4. Provide specific justification for your assessment]

VALIDATION:
Status: [VALID or INVALID]
Issues: [If INVALID, describe the specific problems]

Begin your validation analysis:"""

# Default examples for few-shot prompting
DEFAULT_FEW_SHOT_EXAMPLES = [
    {
        "text": "Apple Inc. announced the acquisition of XYZ Corp for $1.2 billion...",
        "reasoning": "This is a significant acquisition announcement involving a substantial financial transaction. The $1.2 billion value indicates material impact on Apple's financial position and business strategy.",
        "classification": "Event Type: Acquisition, Relevant: true",
    },
    {
        "text": "The company announced quarterly earnings results showing 15% revenue growth...",
        "reasoning": "Quarterly earnings with significant growth are highly material to investors as they directly impact stock valuation and demonstrate business performance.",
        "classification": "Event Type: Financial Event, Relevant: true",
    },
    {
        "text": "John Smith was appointed as new Chief Technology Officer...",
        "reasoning": "Executive appointments at the CTO level can signal strategic direction changes and are relevant for investor assessment of company leadership and technology strategy.",
        "classification": "Event Type: Personnel Change, Relevant: true",
    },
] 