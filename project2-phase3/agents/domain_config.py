import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class DomainConfigAgent:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            model_name="openai/gpt-oss-20b",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def analyze_domain(self, file_path):
        print(f"[INFO] Domain Config Agent: Inspecting {file_path}")
        try:
            df = pd.read_csv(file_path, encoding='windows-1252', nrows=5, comment='#')
            columns = list(df.columns)
            
            base_name = os.path.basename(file_path).replace('.csv', '').replace('_', ' ')
            
            prompt = f"File Name: {base_name}. Columns: {columns}. Identify the specific business domain (e.g., Restaurant Sales, Inventory Management, E-commerce). Return ONLY the domain name in 2-3 words."
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            domain = response.content.strip()
            
            print(f"[INFO] Domain Identified: {domain}")
            return {"domain": domain, "columns": columns, "status": "success"}
        except Exception as e:
            print(f"[ERROR] Domain Config Agent: {e}")
            return {"domain": "Unknown", "columns": [], "status": "error"}