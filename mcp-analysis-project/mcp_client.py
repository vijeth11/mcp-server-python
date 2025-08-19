import gradio as gr
from smolagents import CodeAgent, LiteLLMModel, MCPClient

model = LiteLLMModel(
    model_id="ollama_chat/qwen3:8b",  # or any model you've pulled
    api_base="http://localhost:11434"
)

client = MCPClient({"url": "http://localhost:8000/mcp", "transport": "streamable-http"})
tools = client.get_tools()

#prompts = client.

agent = CodeAgent(
    model=model,
    tools=tools,  # Add tools if needed
    #prompt_templates= prompts,  # Add prompts if needed
    instructions = """You are a sentiment analysis expert. 
    Analyze the sentiment for the provided text and return the result in user friendly format.
    Use the tools provided to assist in your analysis.""",
)

demo = gr.ChatInterface(
    fn=lambda message, history: str(agent.run(message)),
    type="messages",
    examples=["Enter a text to analyze sentiment."],
    title="Agent with MCP Tools",
    description="This is a simple agent that uses MCP tools to analyze sentiment."
)

demo.launch()