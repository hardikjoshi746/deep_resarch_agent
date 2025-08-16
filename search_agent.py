from agents import Agent, WebSearchTool, ModelSettings

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise, 2–3 paragraph summary under 250 words. Capture the main points. "
    "Write succinctly; sentence fragments are fine. This will be consumed by a writer agent, "
    "so prioritize signal over style. Do not include anything except the summary."
) # the instructions for the search agent

search_agent = Agent(
    name="Search agent", # name of the agent
    instructions=INSTRUCTIONS, # instructions for the agent
    tools=[WebSearchTool(search_context_size="low")], # tool we are using from OpenAI SDK to search from web
    model="gpt-4o-mini", # openAI model we will use
    model_settings=ModelSettings(tool_choice="required"), # specify the tool is required
) # the search agent