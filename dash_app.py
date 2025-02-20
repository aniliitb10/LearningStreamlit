from dash import Dash, html

# Initialize Dash app with path prefixes
app = Dash(
    __name__,
)

# App layout
app.layout = html.Div("Hello, this is a Dash app served over HTTPS!")

if __name__ == "__main__":
    # Keep Dash running on plain HTTP, e.g., http://127.0.0.1:8050
    app.run_server(host="127.0.0.1", port=8050)