import pandas as pd

def clean_node(state):
    print("[INFO] Cleaner Agent: Initializing data cleaning process...")
    raw_path = state["data_path"]
    
    try:
        # Fixed encoding issue here
        df = pd.read_csv(raw_path, encoding='windows-1252')
        initial_rows = len(df)
        
        # 1. Fix incorrect data types (Force numeric coercion)
        expected_numeric = ["Sales", "Quantity", "Profit", "Discount"]
        for col in expected_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
        # 2. Remove broken rows (Missing critical data or impossible values)
        if "Sales" in df.columns:
            df = df.dropna(subset=["Sales"])
        if "Quantity" in df.columns:
            df = df.dropna(subset=["Quantity"])
            df = df[df["Quantity"] > 0] # Filter out negative/zero quantities
            
        # 3. Remove obvious duplicates
        df = df.drop_duplicates()
        
        # 4. Handle remaining missing values gracefully
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            df[cat_cols] = df[cat_cols].fillna("Unknown")
            
        cleaned_path = "data/cleaned_data.csv"
        df.to_csv(cleaned_path, index=False)
        
        print(f"[INFO] Cleaner Agent: Fixed types & removed broken rows. Reduced from {initial_rows} to {len(df)} rows.")
        return {"cleaned_path": cleaned_path, "current_step": "orchestrator"}
        
    except Exception as e:
        print(f"[ERROR] Cleaner Agent: {str(e)}")
        return {"current_step": "error"}