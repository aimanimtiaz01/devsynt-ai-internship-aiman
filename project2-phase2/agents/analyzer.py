import pandas as pd
import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

def analyze_node(state):
    print("[INFO] Analyzer Agent: Generating insights and LLM summary...")
    cleaned_path = state["cleaned_path"]
    
    try:
        df = pd.read_csv(cleaned_path)
        insights = {}
        
        # Calculate EDA metrics
        if 'Sales' in df.columns:
            insights['total_sales'] = round(float(df['Sales'].sum()), 2)
            
            # True Average Order Value using unique Order IDs
            if 'Order ID' in df.columns:
                unique_orders = df['Order ID'].nunique()
                insights['average_order_value'] = round(float(insights['total_sales'] / unique_orders), 2) if unique_orders > 0 else 0.0
            else:
                insights['average_order_value'] = round(float(df['Sales'].mean()), 2)
                
        if 'Profit' in df.columns:
            insights['total_profit'] = round(float(df['Profit'].sum()), 2)
        if 'Quantity' in df.columns:
            insights['total_quantity'] = int(df['Quantity'].sum())
            
        if 'Region' in df.columns and 'Sales' in df.columns:
            region_sales = df.groupby('Region')['Sales'].sum().to_dict()
            insights['sales_by_region'] = {k: round(float(v), 2) for k, v in region_sales.items()}
            
        if 'Category' in df.columns and 'Sales' in df.columns:
            category_sales = df.groupby('Category')['Sales'].sum().to_dict()
            insights['sales_by_category'] = {k: round(float(v), 2) for k, v in category_sales.items()}
            
        if 'Product Name' in df.columns and 'Sales' in df.columns:
            top_products = df.groupby('Product Name')['Sales'].sum().nlargest(5).to_dict()
            insights['top_5_products'] = {k: round(float(v), 2) for k, v in top_products.items()}
            
        # Save JSON
        insights_path = "assets/analysis_insights.json"
        with open(insights_path, 'w') as f:
            json.dump(insights, f, indent=4)
            
        # Stricter LangChain LLM Integration to prevent unsupported claims
        llm = ChatGroq(
            temperature=0,
            model_name="openai/gpt-oss-20b",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = f"""
        You are a retail data analyst. Review these exact metrics and provide a precise, 2-sentence executive summary based strictly on the provided numbers:
        - Total Sales: ${insights.get('total_sales', 0):,.2f}
        - Total Profit: ${insights.get('total_profit', 0):,.2f}
        - Total Quantity Sold: {insights.get('total_quantity', 0)}
        - Average Order Value: ${insights.get('average_order_value', 0):,.2f}
        Do not mention inventory turnover, supply chain efficiency, or any metrics not listed above.
        """
        response = llm.invoke([HumanMessage(content=prompt)])
        llm_summary = response.content
        print(f"\n[INFO] Analyzer Agent LLM Summary:\n{llm_summary}\n")
        
        # Generate Static Dashboard with Top Products table included
        generate_dashboard(insights, llm_summary)
        print("[INFO] Analyzer Agent: Dynamic dashboard.html generated successfully.")
        
        return {"insights_path": insights_path, "current_step": "done"}
        
    except Exception as e:
        print(f"[ERROR] Analyzer Agent: {str(e)}")
        return {"current_step": "error"}

def generate_dashboard(insights, summary):
    """Writes the actual calculated data and top products into a styled HTML file."""
    
    # Format Top Products for HTML table rendering
    top_products = insights.get('top_5_products', {})
    product_rows = ""
    for prod, sales in top_products.items():
        product_rows += f"<tr><td>{prod}</td><td style='text-align: right;'>${sales:,.2f}</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Retail Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #f3f4f6; color: #1f2937; }}
            .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #312e81 100%); color: white; padding: 30px 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
            .container {{ padding: 40px; max-width: 1400px; margin: 0 auto; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }}
            .card h2 {{ margin-top: 0; font-size: 16px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; }}
            .summary-text {{ font-size: 16px; line-height: 1.6; color: #374151; }}
            .metrics {{ display: flex; gap: 24px; margin-bottom: 24px; }}
            .metric {{ background: white; padding: 25px; border-radius: 12px; flex: 1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; border-left: 5px solid #3b82f6; }}
            .metric h3 {{ color: #6b7280; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }}
            .metric h2 {{ margin: 0; font-size: 28px; color: #111827; font-weight: 700; }}
            .charts {{ display: flex; flex-wrap: wrap; gap: 24px; margin-bottom: 24px; }}
            .chart-container {{ background: white; padding: 20px; border-radius: 12px; flex: 1; min-width: 450px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e5e7eb; font-size: 14px; }}
            th {{ background-color: #f9fafb; font-weight: 600; color: #4b5563; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }}
            tr:hover {{ background-color: #f9fafb; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Retail Data Pipeline Dashboard</h1>
        </div>
        <div class="container">
            <div class="card">
                <h2>AI Executive Summary</h2>
                <p class="summary-text">{summary}</p>
            </div>

            <div class="metrics">
                <div class="metric" style="border-left-color: #3b82f6;">
                    <h3>Total Sales</h3>
                    <h2>${insights.get('total_sales', 0):,.2f}</h2>
                </div>
                <div class="metric" style="border-left-color: #10b981;">
                    <h3>Total Profit</h3>
                    <h2>${insights.get('total_profit', 0):,.2f}</h2>
                </div>
                <div class="metric" style="border-left-color: #8b5cf6;">
                    <h3>Avg Order Value</h3>
                    <h2>${insights.get('average_order_value', 0):,.2f}</h2>
                </div>
            </div>
            
            <div class="charts">
                <div class="chart-container" id="region-chart"></div>
                <div class="chart-container" id="category-chart"></div>
            </div>

            <div class="card">
                <h2>Top 5 Products by Sales</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th style="text-align: right;">Total Sales</th>
                        </tr>
                    </thead>
                    <tbody>
                        {product_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            var regionData = {json.dumps(insights.get('sales_by_region', {}))};
            var categoryData = {json.dumps(insights.get('sales_by_category', {}))};
            
            var layoutConfig = {{
                font: {{ family: 'Inter, sans-serif' }},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {{t: 40, b: 40, l: 40, r: 20}}
            }};
            
            Plotly.newPlot('region-chart', [{{
                x: Object.keys(regionData),
                y: Object.values(regionData),
                type: 'bar',
                marker: {{color: '#3b82f6'}}
            }}], {{...layoutConfig, title: 'Sales by Region'}});
            
            Plotly.newPlot('category-chart', [{{
                x: Object.keys(categoryData),
                y: Object.values(categoryData),
                type: 'bar',
                marker: {{color: '#8b5cf6'}}
            }}], {{...layoutConfig, title: 'Sales by Category'}});
        </script>
    </body>
    </html>
    """
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)