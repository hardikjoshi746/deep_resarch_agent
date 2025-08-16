from agents import Agent, WebSearchTool, ModelSettings

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succintly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
) # the instructions for the search agent

search_agent = Agent(
    name="Search agent", # name of the agent
    instructions=INSTRUCTIONS, # instructions for the agent
    tools=[WebSearchTool(search_context_size="low")], # tool we are using from OpenAI SDK to search from web
    model="gpt-4o-mini", # openAI model we will use
    model_settings=ModelSettings(tool_choice="required"), # specify the tool is required
) # the search agent