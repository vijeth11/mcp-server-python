import gradio as gr
from smolagents import CodeAgent, LiteLLMModel, MCPClient
from mcp import StdioServerParameters

model = LiteLLMModel(
    model_id="ollama_chat/qwen3:8b",  # or any model you've pulled
    api_base="http://localhost:11434"
)

client = MCPClient(StdioServerParameters(
    command= "npx",
    args= [
        "-y",
        "@wonderwhy-er/desktop-commander@latest"
      ]
))
tools = client.get_tools()
print(tools)
#prompts = client.

agent = CodeAgent(
    model=model,
    tools=tools,  # Add tools if needed
    instructions = " you are a resume assessment AI use the file reader tool to Read the contents of C:\\Users\\vijet\\Documents\\GitHub\\mcp-server-python\\file-assistant\\job_description.md. And then list the tools which you have to user."
    #prompt_templates= prompts,  # Add prompts if needed
)

demo = gr.ChatInterface(
    fn=lambda message, history: str(agent.run(message)),
    type="messages",
    examples=["Enter a command"],
    title="Agent with MCP Tools",
    description="This is a simple agent that uses MCP tools to analyze sentiment."
)

demo.launch()