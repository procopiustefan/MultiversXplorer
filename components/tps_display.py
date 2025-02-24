import streamlit.components.v1 as components

def tps_display(tps_value):
    """Custom component for TPS display with auto-refresh"""
    
    html = f"""
        <div id="tps-display" style="font-size: 1rem; margin-bottom: 1rem;">
            <div style="color: #808495;">Network Speed</div>
            <div id="tps-value" style="font-size: 1.5rem; font-weight: bold;">{tps_value} TPS</div>
            
            <script>
                function updateTPS() {{
                    fetch('/network_stats')
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('tps-value').innerText = data.tps + ' TPS';
                        }});
                }}
                
                // Update every 6 seconds
                setInterval(updateTPS, 6000);
            </script>
        </div>
    """
    
    components.html(html, height=100) 