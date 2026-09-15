import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from domain_config import DomainConfigAgent
from orchestrator import PipelineOrchestrator

def main():
    datasets = [
        "test-datasets/online_retail.csv",
        "test-datasets/restaurant_sales.csv",
        "test-datasets/inventory_management.csv",
        "test-datasets/amazon_sale_report.csv"
    ]
    
    domain_agent = DomainConfigAgent()
    orchestrator = PipelineOrchestrator()
    
    for ds in datasets:
        print("-" * 60)
        print(f"[SYSTEM] Starting process for {ds}")
        
        if not os.path.exists(ds):
            print(f"[ERROR] File not found: {ds}")
            continue
        
        domain_config = domain_agent.analyze_domain(ds)
        
        if domain_config["status"] == "success":
            orchestrator.run_pipeline(ds, domain_config)
        else:
            print(f"[ERROR] Domain config failed for {ds}. Skipping.")
            
        print("-" * 60)

if __name__ == "__main__":
    main()