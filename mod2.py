import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import os
from dash import Dash

# Initial sample data for the 4D scatter plot
df = pd.DataFrame({
    'Service': ['Broadband Access', 'Mobile Hotspots', 'Online Content', 'IT Support Hotline', 'Tech Delivery'],
    'Urgency': np.random.randint(1, 10, 5),
    'Resources': np.random.randint(1, 10, 5),
    'Regulations': np.random.randint(1, 10, 5),
    'Uncertainty': np.random.randint(1, 10, 5)
})

# Initialize the Dash app
app = Dash(__name__)

# Layout of the app with dropdown, sliders, text input, and buttons
app.layout = html.Div([
    dcc.Graph(id="3d-scatter"),

    html.Label("Select Existing Service to Edit"),
    dcc.Dropdown(id="service-dropdown", options=[{'label': service, 'value': service} for service in df['Service']], placeholder="Select a service"),

    html.Label("Enter New Service Name"),
    dcc.Input(id="new-service-name", type="text", placeholder="Enter new service name"),

    html.Label("Urgency"),
    dcc.Slider(id="urgency-slider", min=1, max=10, step=1, value=5),
    html.Label("Resources"),
    dcc.Slider(id="resources-slider", min=1, max=10, step=1, value=5),
    html.Label("Regulations"),
    dcc.Slider(id="regulations-slider", min=1, max=10, step=1, value=5),
    html.Label("Uncertainty"),
    dcc.Slider(id="uncertainty-slider", min=1, max=10, step=1, value=5),

    html.Button("Add New Service", id="add-button", n_clicks=0),
    html.Button("Update Selected Service", id="update-button", n_clicks=0),
    html.Button("Remove Selected Service", id="remove-button", n_clicks=0),

    dcc.Store(id="data-store", data=df.to_dict("records"))
])

# Callback to update dropdown options and graph based on current data
@app.callback(
    [Output("3d-scatter", "figure"),
     Output("service-dropdown", "options")],
    [Input("data-store", "data")]
)
def update_graph(data):
    df_updated = pd.DataFrame(data)
    fig = px.scatter_3d(df_updated, x="Urgency", y="Resources", z="Regulations", color="Uncertainty", text="Service")
    fig.update_traces(marker=dict(size=8))
    options = [{'label': service, 'value': service} for service in df_updated['Service']]
    return fig, options

# Callback to handle adding, updating, and removing entries
@app.callback(
    Output("data-store", "data"),
    [Input("add-button", "n_clicks"),
     Input("update-button", "n_clicks"),
     Input("remove-button", "n_clicks")],
    [State("data-store", "data"),
     State("service-dropdown", "value"),
     State("new-service-name", "value"),
     State("urgency-slider", "value"),
     State("resources-slider", "value"),
     State("regulations-slider", "value"),
     State("uncertainty-slider", "value")]
)
def modify_data(add_clicks, update_clicks, remove_clicks, data, selected_service, new_service_name, urgency, resources, regulations, uncertainty):
    df_updated = pd.DataFrame(data)
    ctx = dash.callback_context
    if not ctx.triggered:
        return data
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Adding a new service
    if button_id == "add-button" and new_service_name:
        new_entry = {
            "Service": new_service_name,
            "Urgency": urgency,
            "Resources": resources,
            "Regulations": regulations,
            "Uncertainty": uncertainty
        }
        df_updated = pd.concat([df_updated, pd.DataFrame([new_entry])], ignore_index=True)

    elif button_id == "update-button" and selected_service:
        df_updated.loc[df_updated["Service"] == selected_service, ["Urgency", "Resources", "Regulations", "Uncertainty"]] = [urgency, resources, regulations, uncertainty]

    elif button_id == "remove-button" and selected_service:
        df_updated = df_updated[df_updated["Service"] != selected_service]

    return df_updated.to_dict("records")

# Run the app
if __name__ == "__main__":
    app.run_server(
        debug=True,
        port=int(os.environ.get("PORT", 8080)),
        host="0.0.0.0"
    )
