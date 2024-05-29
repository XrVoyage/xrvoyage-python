from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolExecutor
from langchain_core.tools import tool
from langgraph.prebuilt import ToolExecutor
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def search(query: str):
    """Call to surf the web."""
    return ["It's sunny in San Francisco, but you better look out if you're a Gemini 😈."]

@tool
def create_panel(panel_id: str):
    """Creates a panel with the given panel_id."""
    # Dummy implementation for panel creation
    return f"Panel with ID {panel_id} has been added to the ship."

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

def call_model(state):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

def call_tool(state):
    messages = state["messages"]
    last_message = messages[-1]
    tool_call = last_message.tool_calls[0]
    action = ToolInvocation(tool=tool_call["name"], tool_input=tool_call["args"], id=tool_call["id"])
    response = tool_executor.invoke(action)
    tool_message = ToolMessage(content=str(response), name=action.tool, tool_call_id=tool_call["id"])
    return {"messages": [tool_message]}

memory = SqliteSaver.from_conn_string(":memory:")
tools = [search, create_panel]
tool_executor = ToolExecutor(tools)
model = ChatOpenAI(temperature=0)
model = model.bind_tools(tools)
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")
app = workflow.compile(checkpointer=memory, interrupt_before=["action"])

import sys

thread = {"configurable": {"thread_id": "2"}}

def prompt_user():
    return input("Enter your message: ")

instruction = '''
    you are serious software. agent launcher equipped with precision sub-agents (your toolset).
    you will be paying serious attention to every execution of external tool.
    you will not allow any unwanted executions or unverified parameters.
    you will prompt your human operator if data is missing and make no assumptions.
    your prompts will be super short and very precise.
'''
inputs = [HumanMessage(content=instruction)]
for event in app.stream({"messages": inputs}, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

while True:
    user_input = prompt_user()
    if user_input.lower() in {"exit", "quit"}:
        break

    inputs = [HumanMessage(content=user_input)]
    for event in app.stream({"messages": inputs}, thread, stream_mode="values"):
        event["messages"][-1].pretty_print()

# Resume the interrupted graph
for event in app.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
