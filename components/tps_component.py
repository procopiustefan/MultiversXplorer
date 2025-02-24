import streamlit.components.v1 as components

def tps_gauge_component(tps_value):
    """Custom component for TPS gauge that auto-updates"""
    
    component_html = f"""
        <div id="tps-gauge">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                var tps = {tps_value};
                
                function createGauge() {{
                    var data = [{{
                        type: "indicator",
                        mode: "gauge+number",
                        value: tps,
                        number: {{ suffix: " TPS", font: {{ size: 24 }} }},
                        gauge: {{
                            axis: {{ range: [null, 100], tickwidth: 1 }},
                            bar: {{ color: tps < 10 ? "red" : tps < 30 ? "orange" : "green" }},
                            bgcolor: "white",
                            borderwidth: 2,
                            bordercolor: "gray",
                            steps: [
                                {{ range: [0, 10], color: "rgba(255, 0, 0, 0.1)" }},
                                {{ range: [10, 30], color: "rgba(255, 165, 0, 0.1)" }},
                                {{ range: [30, 100], color: "rgba(0, 128, 0, 0.1)" }}
                            ]
                        }}
                    }}];
                    
                    var layout = {{
                        height: 150,
                        margin: {{ l: 10, r: 10, t: 30, b: 10 }},
                        paper_bgcolor: "rgba(0,0,0,0)",
                        font: {{ color: "#808495" }}
                    }};
                    
                    Plotly.newPlot('tps-gauge', data, layout, {{displayModeBar: false}});
                }}
                
                // Create initial gauge
                createGauge();
                
                // Setup WebSocket-like connection to get updates
                var eventSource = new EventSource('/_stcore/stream');
                eventSource.onmessage = function(e) {{
                    try {{
                        var data = JSON.parse(e.data);
                        if (data.tps !== undefined) {{
                            tps = data.tps;
                            Plotly.update('tps-gauge', {{'value': [tps]}});
                        }}
                    }} catch (err) {{
                        console.error('Error updating TPS:', err);
                    }}
                }};
            </script>
        </div>
    """
    
    components.html(component_html, height=150) 