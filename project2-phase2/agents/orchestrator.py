from typing import TypedDict

# Define the State that will be passed between agents
class PipelineState(TypedDict):
    data_path: str
    cleaned_path: str
    insights_path: str
    current_step: str

def orchestrator_node(state: PipelineState):
    print("[INFO] Orchestrator Agent: Reviewing current state and determining next route...")
    
    # Safety check to prevent infinite loops
    if state.get("current_step") == "error":
        print("[FATAL] Orchestrator Agent: Pipeline halted due to an error in a previous step.")
        return {"current_step": "end"}
        
    # Routing logic based on state
    if not state.get("cleaned_path"):
        print("[INFO] Orchestrator Agent: Routing data to Cleaner Agent.")
        return {"current_step": "clean"}
    else:
        print("[INFO] Orchestrator Agent: Routing cleaned data to Analyzer Agent.")
        return {"current_step": "analyze"}