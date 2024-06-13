# Server Sent Events (SSE)

## What is Server Sent Events?

## Example
### Server-Side: Stream of Events
* **Continuous Stream**: `server.py` is continuously sending a stream of data at the `/stock-updates` endpoint. This data is formatted specifically for SSE, using a `text/event-stream` content type.
* **Stateless HTTP Protocol**: Despite HTTP being a stateless protocol, *SSE allows the server to keep the connection open and continuously send data over a single HTTP response*.
  
    ```python
    return Response(generate_stock_prices(), content_type="text/event-stream")
    ```

> On the server side, SSE involves setting up an endpoint that sends a continuous stream of data formatted for SSE.    

### Client-Side: Consuming the Stream (EventSource)
* **EventSource API**: This JavaScript API is designed to handle the SSE protocol on the client side. It establishes a persistent connection to the server and listens for messages sent over this connection.
* **Automatic Reconnection**: The EventSource API automatically tries to reconnect if the connection to the server is lost, making it resilient.
* **Event Handling**: The API allows you to define event handlers (like `onmessage`) to process incoming messages. When the Flask server sends a new stock price, the onmessage event is triggered, and your script updates the webpage.


> To build an interactive web application that updates in real-time (like displaying stock prices), you need a way to handle the stream of data programmatically. That's what the EventSource API does. It lets you capture each piece of data sent by the server and use it in your web application

> On the client side, SSE requires handling this stream appropriately, usually with JavaScript and the EventSource API, to integrate the data into the web page dynamically.