import pandas as pd
import os

class DataCleaner:
    def clean_data(self, file_path):
        print("[INFO] Cleaner Agent: Sanitizing data...")
        try:
            df = pd.read_csv(file_path, encoding='windows-1252', on_bad_lines='skip', comment='#')
            df = df.drop_duplicates()
            
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                df[col] = df[col].fillna(0)
                
            cat_cols = df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                df[col] = df[col].fillna("Unknown")
                
            os.makedirs("data", exist_ok=True)
            cleaned_path = "data/cleaned_data.csv"
            df.to_csv(cleaned_path, index=False)
            print(f"[INFO] Cleaner Agent: Cleaned {len(df)} rows.")
            return {"cleaned_path": cleaned_path, "status": "success"}
        except Exception as e:
            print(f"[ERROR] Cleaner Agent: {e}")
            return {"status": "error"}