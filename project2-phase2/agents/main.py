import os
import sys

# This ensures Python can find your other agent files without errors
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph.graph import StateGraph, END
from orchestrator import PipelineState, orchestrator_node
from cleaner import clean_node
from analyzer import analyze_node

# Routing function for conditional edges
def router(state):
    step = state.get("current_step")
    if step == "clean":
        return "cleaner"
    elif step == "analyze":
        return "analyzer"
    else:
        return END

def build_and_run_graph():
    print("-" * 60)
    print("[SYSTEM] Initializing Multi-Agent LangGraph Pipeline")
    print("-" * 60)
    
    # Initialize the state graph
    workflow = StateGraph(PipelineState)
    
    # Add nodes (Agents)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("cleaner", clean_node)
    workflow.add_node("analyzer", analyze_node)
    
    # Set the entry point
    workflow.set_entry_point("orchestrator")
    
    # Add conditional edges from the orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        router,
        {
            "cleaner": "cleaner",
            "analyzer": "analyzer",
            END: END
        }
    )
    
    # Add standard edges returning to orchestrator
    workflow.add_edge("cleaner", "orchestrator")
    workflow.add_edge("analyzer", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Define initial state
    initial_state = {
        "data_path": "data/superstore_sales.csv",
        "cleaned_path": "",
        "insights_path": "",
        "current_step": ""
    }
    
    if not os.path.exists(initial_state["data_path"]):
        print(f"[FATAL] Dataset not found at {initial_state['data_path']}")
        print("Please ensure superstore_sales.csv is inside the 'data' folder.")
        return
        
    # Execute the graph
    app.invoke(initial_state)
    print("-" * 60)
    print("[SYSTEM] Pipeline Execution Completed Successfully")
    print("-" * 60)

if __name__ == "__main__":
    build_and_run_graph()