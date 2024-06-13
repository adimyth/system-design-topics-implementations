from flask import Flask, Response
from flask_cors import CORS
import json
import time
import random

app = Flask(__name__)
CORS(app)


def generate_stock_prices():
    """Simulate real-time stock price updates."""
    stocks = ["AAPL", "MSFT", "GOOG", "AMZN"]
    while True:
        data = {
            "stock": random.choice(stocks),
            "price": round(random.uniform(100, 500), 2),
        }
        # Yield the data as a Server-Sent Event.
        yield f"data: {json.dumps(data)}\n\n"
        # Update every 1 second
        time.sleep(1)


@app.route("/stock-updates")
def stock_updates():
    """Endpoint for Server-Sent Events."""

    # Set the response type to text/event-stream.
    return Response(generate_stock_prices(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)
