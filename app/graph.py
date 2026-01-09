from langgraph.graph import StateGraph, END
from app.state import GraphState
from app.nodes import router_node, weather_node, rag_node, generation_node

def build_graph():
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("weather_node", weather_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("generator", generation_node)

    # Set Entry Point
    workflow.set_entry_point("router")

    # Add Conditional Edges
    def decide_next_node(state):
        if state["route"] == "weather":
            return "weather_node"
        else:
            return "rag_node"

    workflow.add_conditional_edges(
        "router",
        decide_next_node,
        {
            "weather_node": "weather_node",
            "rag_node": "rag_node"
        }
    )

    # Connect Tools to Generator
    workflow.add_edge("weather_node", "generator")
    workflow.add_edge("rag_node", "generator")
    
    # End
    workflow.add_edge("generator", END)

    return workflow.compile()