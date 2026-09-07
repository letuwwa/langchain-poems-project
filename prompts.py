from langchain_core.prompts import ChatPromptTemplate


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
