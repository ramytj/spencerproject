import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask, session
from flask_session import Session
import os

# Initialize the Flask server and configure sessions
server = Flask(__name__)
server.config["SECRET_KEY"] = os.urandom(24)
server.config["SESSION_TYPE"] = "filesystem"  # Store sessions on the filesystem
Session(server)  # Initialize session management

# Initialize the Dash app
app = dash.Dash(__name__, server=server)

# Initial data for a new session
def get_initial_data():
    return pd.DataFrame({
        'Service': ['Broadband Access', 'Mobile Hotspots', 'Online Content', 'IT Support Hotline', 'Tech Delivery'],
        'Urgency': np.random.randint(1, 10, 5),
        'Resources': np.random.randint(1, 10, 5),
        'Regulations': np.random.randint(1, 10, 5),
        'Uncertainty': np.random.randint(1, 10, 5)
    }).to_dict("records")

# Set up layout
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

# Load or initialize session data
@app.callback(Output("data-store", "data"), Input("add-button", "n_clicks"), Input("update-button", "n_clicks"))
def load_session_data(add_clicks, update_clicks):
    if "data" not in session:
        session["data"] = get_initial_data()  # Initialize session data
    return session["data"]

# Save session data after changes
@app.callback(
    Output("3d-scatter", "figure"),
    Input("data-store", "data"),
    State("service-dropdown", "value"),
    State("new-service-name", "value"),
    # Add more inputs for slider values...
)
def update_session_data(data, selected_service, new_service_name):
    # Modify the session data as needed based on user actions
    # Update session["data"] here based on actions like add, update, remove
    session["data"] = data  # Save data back to session
    # Update graph, dropdown, and options
