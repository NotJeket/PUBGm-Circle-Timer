from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import requests
from datetime import datetime

external_stylesheets = ['assets/style.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Initialize data API URL
api_url = "http://127.0.0.1:5000/data5"  # Replace with the actual URL of your data API

app.layout = html.Div(
    [
        html.Div(id="reveal-container", className="reveal-container", children=[
            html.Div(className="timer-container",
                children=[
                    html.Div(className="timer-bar-wrapper",
                        children=[
                            html.Div(id="timer-bar", className="timer-bar"),
                            html.Div("CIRCLE CLOSING", className="overlay-text-1")
                        ]
                    ),
                    html.Div(id="timer-value", className="timer"),
                    html.Div(className="timer-bar-wrapper mirrored",
                        children=[
                            html.Div(id="timer-bar-mirrored", className="timer-bar"),
                            html.Div("CIRCLE CLOSING", className="overlay-text-2")
                        ]
                    )
                ]
            ),
        ]),
        dcc.Interval(
            id="interval-component",
            interval=500,  # Update every 0.5 seconds
            n_intervals=0
        ),
        dcc.Store(
            id="circle-data-store"
        )
    ],
    className="app-container"
)

@app.callback(
    Output("circle-data-store", "data"),
    Input("interval-component", "n_intervals")
)
def update_circle_data(n):
    # Retrieve data from the API
    response = requests.get(api_url)
    if response.status_code == 200:
        json_data = response.json()
        return json_data.get("circleInfo", {})
    else:
        return {}


# Update the timer value
def update_timer(circle_data):
    if isinstance(circle_data, dict):
        counter = int(circle_data.get("Counter", 0))
        max_time = int(circle_data.get("MaxTime", 0))

        # Calculate the remaining time until the circle closes
        remaining_time = max_time - counter

        # Limit the remaining time to the last 30 seconds
        remaining_time = max(remaining_time, 0)  # Ensure the remaining time is not negative
        remaining_time = min(remaining_time, 21)  # Limit the remaining time to the last 30 seconds
    else:
        remaining_time = 0

    return remaining_time


@app.callback(
    Output("timer-value", "children"),
    Output("timer-bar", "style"),
    Output("timer-bar-mirrored", "style"),
    Input("circle-data-store", "data")
)
def update_timer_display(data):
    remaining_time = update_timer(data)

    # Calculate the width of the timer bar
    bar_width = f"{(remaining_time / 20) * 100}%"

    # Update the style of the timer bar elements
    bar_style = {"width": bar_width}

    # Format the timer text with milliseconds
    milliseconds = datetime.now().strftime("%f")[:-6] #3 for miliseconds to display
    timer_text = html.Div(
        [
            f"{remaining_time}",
            html.Sup(milliseconds)
        ],
        className="timer-text"
    )

    return timer_text, bar_style, bar_style


@app.callback(
    Output("reveal-container", "style"),
    Input("circle-data-store", "data")
)
def update_timer_class(data):
    remaining_time = update_timer(data)
    circle_status = data.get("CircleStatus")
    game_time = data.get("GameTime")

    if circle_status == '2':
        return {"display": "none"}

    if remaining_time <= 20 and remaining_time > 0:
        return {"opacity": "1", "transition": "opacity 1s ease-in-out"}
    elif remaining_time == 0:
        return {"opacity": "0", "transition": "opacity 1s ease-in-out"}
    else:
        return {"opacity": "0", "transition": "opacity 1s ease-in-out"}


if __name__ == "__main__":
    app.run_server(debug=False, port=8055, host="127.0.0.1")