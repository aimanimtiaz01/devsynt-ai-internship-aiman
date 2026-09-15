import pandas as pd
import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

class DataAnalyzer:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="openai/gpt-oss-20b",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def analyze(self, cleaned_path, domain_config):
        print("[INFO] Analyzer Agent: Generating insights...")
        try:
            df = pd.read_csv(cleaned_path)
            insights = {}
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            col_lower = {col.lower(): col for col in df.columns}
            revenue_keywords = ['sales', 'amount', 'price', 'profit', 'total', 'revenue', 'quantity']
            target_num_col = None
            
            for kw in revenue_keywords:
                for col_l, original_col in col_lower.items():
                    if kw in col_l and original_col in numeric_cols:
                        target_num_col = original_col
                        break
                if target_num_col: break
                
            if not target_num_col and numeric_cols:
                target_num_col = numeric_cols[0]
                
            cat_keywords = ['category', 'product', 'item', 'style', 'city', 'region', 'name']
            target_cat_col = None
            
            for kw in cat_keywords:
                for col_l, original_col in col_lower.items():
                    if kw in col_l and original_col in categorical_cols:
                        target_cat_col = original_col
                        break
                if target_cat_col: break
                
            if not target_cat_col and categorical_cols:
                target_cat_col = categorical_cols[0]

            insights['domain'] = domain_config['domain']
            insights['total_records'] = len(df)
            
            if target_num_col:
                insights['total_primary_metric'] = round(float(df[target_num_col].sum()), 2)
                insights['primary_metric_name'] = target_num_col
                
                if target_cat_col:
                    top_items = df.groupby(target_cat_col)[target_num_col].sum().nlargest(5).to_dict()
                    insights['top_items'] = {str(k): round(float(v), 2) for k, v in top_items.items()}
                    insights['category_col_name'] = target_cat_col
                    
                    dist_items = df.groupby(target_cat_col)[target_num_col].sum().nlargest(10).to_dict()
                    insights['distribution_chart'] = {str(k): round(float(v), 2) for k, v in dist_items.items()}

            os.makedirs("assets", exist_ok=True)
            with open("assets/analysis_insights.json", 'w') as f:
                json.dump(insights, f, indent=4)

            prompt = f"Review metrics for {insights['domain']} domain: Records: {insights.get('total_records')}, Metric {insights.get('primary_metric_name')}: {insights.get('total_primary_metric')}. Write a precise 2-sentence executive summary based strictly on these numbers."
            response = self.llm.invoke([HumanMessage(content=prompt)])
            insights['llm_summary'] = response.content.strip()
            
            print("[INFO] Analyzer Agent: Analysis completed.")
            return {"insights": insights, "status": "success"}
        except Exception as e:
            print(f"[ERROR] Analyzer Agent: {e}")
            return {"status": "error"}