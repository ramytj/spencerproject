import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import os
from flask import Flask, session
from flask_session import Session
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the Flask server and configure sessions
server = Flask(__name__)
server.config["SECRET_KEY"] = "your_fixed_secret_key"  # Set a fixed secret key for session encryption
server.config["SESSION_TYPE"] = "filesystem"  # Store sessions on the filesystem
Session(server)  # Initialize Flask-Session

# Initialize the Dash app
app = dash.Dash(__name__, server=server)

# Initial sample data for the 4D scatter plot
def get_initial_data():
    return pd.DataFrame({
        'Service': ['Broadband Access', 'Mobile Hotspots', 'Online Content', 'IT Support Hotline', 'Tech Delivery'],
        'Urgency': np.random.randint(1, 10, 5),
        'Resources': np.random.randint(1, 10, 5),
        'Regulations': np.random.randint(1, 10, 5),
        'Uncertainty': np.random.randint(1, 10, 5)
    }).to_dict("records")

# Layout of the app with dropdown, sliders, text input, and buttons
app.layout = html.Div([
    dcc.Graph(id="3d-scatter"),
    html.Label("Select Existing Service to Edit"),
    dcc.Dropdown(id="service-dropdown", placeholder="Select a service"),
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
    dcc.Store(id="data-store")
])

# Combined callback to initialize, add, update, and remove entries in data-store.data
@app.callback(
    [Output("data-store", "data"),
     Output("3d-scatter", "figure"),
     Output("service-dropdown", "options")],
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
    # Initialize session data if it doesn't exist
    if "data" not in session:
        session["data"] = get_initial_data()

    df_updated = pd.DataFrame(session["data"])  # Use session data

    # Check which button was clicked
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "add-button" and new_service_name:
            # Add new service with entered values
            new_entry = {
                "Service": new_service_name,  
                "Urgency": urgency,
                "Resources": resources,
                "Regulations": regulations,
                "Uncertainty": uncertainty
            }
            df_updated = pd.concat([df_updated, pd.DataFrame([new_entry])], ignore_index=True)

        elif button_id == "update-button" and selected_service:
            # Update existing service
            df_updated.loc[df_updated["Service"] == selected_service, ["Urgency", "Resources", "Regulations", "Uncertainty"]] = [urgency, resources, regulations, uncertainty]

        elif button_id == "remove-button" and selected_service:
            # Remove selected service
            df_updated = df_updated[df_updated["Service"] != selected_service]

        # Update session data with modified dataframe
        session["data"] = df_updated.to_dict("records")

    # Create updated figure and dropdown options
    fig = px.scatter_3d(df_updated, x="Urgency", y="Resources", z="Regulations", color="Uncertainty", text="Service")
    fig.update_traces(marker=dict(size=8))
    options = [{'label': service, 'value': service} for service in df_updated['Service']]

    return session["data"], fig, options

# Run the app
if __name__ == "__main__":
    app.run_server(
        debug=True,
        port=int(os.environ.get("PORT", 8080)),  # Use Heroku's assigned port
        host="0.0.0.0"
    )
