from langchain_core.prompts import ChatPromptTemplate


router_prompt = ChatPromptTemplate.from_template(
    "Classify the user's request into one route: write or explain. "
    "Use explain when the user asks to explain or interpret a poem. "
    "Use write when the user asks for a new poem or provides just a topic. "
    "Return only write or explain.\n\nRequest: {request}"
)

explanation_prompt = ChatPromptTemplate.from_template(
    "Explain the poem in the user's request in simple language. "
    "Describe its meaning, mood, and imagery briefly. "
    "If no poem is provided, ask the user to include it.\n\n"
    "Request: {request}"
)

planning_prompt = ChatPromptTemplate.from_template(
    "Plan a short poem about {topic}. "
    "Suggest a mood. "
    "Keep the plan brief, one sentence. Do not write the poem."
)

writing_prompt = ChatPromptTemplate.from_template(
    "Write a simple poem about {topic} in at most {lines} lines.\n"
    "Use this plan:\n{plan}\n"
    "Return only the poem."
)

revision_prompt = ChatPromptTemplate.from_template(
    "Shorten this poem to at most {lines} nonempty lines. "
    "Preserve its topic and mood. Return only the revised poem.\n\n"
    "{poem}"
)
