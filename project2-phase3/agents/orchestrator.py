import os
from clean import DataCleaner
from analysis import DataAnalyzer
from dashboard import DashboardAgent

class PipelineOrchestrator:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.analyzer = DataAnalyzer()
        self.dashboard = DashboardAgent()

    def run_pipeline(self, file_path, domain_config):
        print(f"[INFO] Orchestrator: Starting pipeline for {domain_config['domain']} domain.")
        try:
            cleaned_data = self.cleaner.clean_data(file_path)
            if cleaned_data["status"] == "error":
                return {"status": "error", "step": "clean"}
            
            analysis_results = self.analyzer.analyze(cleaned_data["cleaned_path"], domain_config)
            if analysis_results["status"] == "error":
                return {"status": "error", "step": "analyze"}
            
            dashboard_result = self.dashboard.generate(analysis_results["insights"], file_path)
            return {"status": "success", "dashboard": dashboard_result["path"]}
        except Exception as e:
            print(f"[ERROR] Orchestrator: {e}")
            return {"status": "error", "step": "orchestrator"}