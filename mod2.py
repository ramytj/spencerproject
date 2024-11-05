import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import os
import psycopg2
from flask import Flask
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the Flask server
server = Flask(__name__)

# Database connection function
def connect_db():
    DATABASE_URL = os.environ['DATABASE_URL']  # This environment variable is set by Heroku
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Initialize the Dash app
app = dash.Dash(__name__, server=server)

# Function to retrieve or initialize data from the database
def get_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS services (service TEXT, urgency INT, resources INT, regulations INT, uncertainty INT)")
    cursor.execute("SELECT * FROM services")
    data = cursor.fetchall()
    if not data:  # If no data, initialize it
        initial_data = [
            ('Broadband Access', np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10)),
            ('Mobile Hotspots', np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10)),
            ('Online Content', np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10)),
            ('IT Support Hotline', np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10)),
            ('Tech Delivery', np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10))
        ]
        cursor.executemany("INSERT INTO services (service, urgency, resources, regulations, uncertainty) VALUES (%s, %s, %s, %s, %s)", initial_data)
        conn.commit()
        data = initial_data
    conn.close()
    return pd.DataFrame(data, columns=["Service", "Urgency", "Resources", "Regulations", "Uncertainty"])

# Function to save updated data to the database
def save_data(df):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM services")
    conn.commit()
    for _, row in df.iterrows():
        cursor.execute("INSERT INTO services (service, urgency, resources, regulations, uncertainty) VALUES (%s, %s, %s, %s, %s)", row)
    conn.commit()
    conn.close()

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id="3d-scatter"),
    html.Label("Select Existing Service to Edit"),
    dcc.Dropdown(id="service-dropdown", placeholder="Select a service"),
    html.Label("Enter New Service Name"),
    dcc.Input(id="new-service-name", type="text", placeholder="Enter new service name"),
    html.Br(),
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

# Initialize, add, update, and remove entries with database storage
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
    df_updated = get_data()
    ctx = dash.callback_context

    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "add-button" and new_service_name:
            new_entry = pd.DataFrame([[new_service_name, urgency, resources, regulations, uncertainty]],
                                     columns=["Service", "Urgency", "Resources", "Regulations", "Uncertainty"])
            df_updated = pd.concat([df_updated, new_entry], ignore_index=True)

        elif button_id == "update-button" and selected_service:
            df_updated.loc[df_updated["Service"] == selected_service, ["Urgency", "Resources", "Regulations", "Uncertainty"]] = [urgency, resources, regulations, uncertainty]

        elif button_id == "remove-button" and selected_service:
            df_updated = df_updated[df_updated["Service"] != selected_service]

        save_data(df_updated)  # Save changes to the database

    fig = px.scatter_3d(df_updated, x="Urgency", y="Resources", z="Regulations", color="Uncertainty", text="Service")
    fig.update_traces(marker=dict(size=8))
    options = [{'label': service, 'value': service} for service in df_updated['Service']]

    return df_updated.to_dict("records"), fig, options

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
