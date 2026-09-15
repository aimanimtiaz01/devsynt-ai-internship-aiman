import os
import json

class DashboardAgent:
    def generate(self, insights, file_path):
        print("[INFO] Dashboard Agent: Rendering dynamic HTML...")
        try:
            primary_metric = insights.get('primary_metric_name', 'Metric')
            cat_col = insights.get('category_col_name', 'Category')
            summary = insights.get('llm_summary', 'No summary generated.')
            domain = insights.get('domain', 'Unknown Domain')
            
            top_items = insights.get('top_items', {})
            product_rows = ""
            for item, val in top_items.items():
                product_rows += f"<tr><td>{item}</td><td style='text-align: right;'>{val:,.2f}</td></tr>"

            chart_data = insights.get('distribution_chart', {})
            base_name = os.path.basename(file_path).replace('.csv', '')
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>{domain} Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
                <style>
                    body {{ font-family: 'Inter', sans-serif; margin: 0; background: #f3f4f6; color: #1f2937; }}
                    .header {{ background: linear-gradient(135deg, #0f172a 0%, #334155 100%); color: white; padding: 30px 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
                    .container {{ padding: 40px; max-width: 1400px; margin: 0 auto; }}
                    .card {{ background: white; padding: 25px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }}
                    .metrics {{ display: flex; gap: 24px; margin-bottom: 24px; }}
                    .metric {{ background: white; padding: 25px; border-radius: 12px; flex: 1; border-left: 5px solid #3b82f6; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                    th {{ background-color: #f9fafb; }}
                    .chart-container {{ background: white; padding: 20px; border-radius: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{domain} Data Dashboard</h1>
                </div>
                <div class="container">
                    <div class="card">
                        <h2>AI Executive Summary</h2>
                        <p>{summary}</p>
                    </div>
                    <div class="metrics">
                        <div class="metric">
                            <h3>Total Records</h3>
                            <h2>{insights.get('total_records', 0)}</h2>
                        </div>
                        <div class="metric" style="border-left-color: #10b981;">
                            <h3>Total {primary_metric.title()}</h3>
                            <h2>{insights.get('total_primary_metric', 0):,.2f}</h2>
                        </div>
                    </div>
                    <div class="chart-container" id="chart-{base_name}" style="margin-bottom: 24px;"></div>
                    <div class="card">
                        <h2>Top 5 by {primary_metric.title()}</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>{cat_col.title()}</th>
                                    <th style="text-align: right;">Total {primary_metric.title()}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {product_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                <script>
                    var chartData = {json.dumps(chart_data)};
                    Plotly.newPlot('chart-{base_name}', [{{
                        x: Object.keys(chartData),
                        y: Object.values(chartData),
                        type: 'bar',
                        marker: {{color: '#3b82f6'}}
                    }}], {{
                        font: {{ family: 'Inter, sans-serif' }},
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        margin: {{t: 40, b: 80, l: 60, r: 20}},
                        title: 'Top 10 {cat_col.title()} by {primary_metric.title()}'
                    }});
                </script>
            </body>
            </html>
            """
            
            os.makedirs("assets", exist_ok=True)
            output_path = f"assets/{base_name}-result.html"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"[INFO] Dashboard Agent: Created {output_path}")
            return {"path": output_path, "status": "success"}
        except Exception as e:
            print(f"[ERROR] Dashboard Agent: {e}")
            return {"status": "error"}