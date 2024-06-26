# Demo program for ahttpserver
#
# Start this program and use you browser to open the main page ('/').
# The current time will be displayed and updated every second.
# Use an API client like Insomnia or Postman to call '/api/date' or
# 'api/stop'.

import gc
import json
import time
import matrix

import uasyncio as asyncio

from ahttpserver import HTTPResponse, HTTPServer, sendfile
from ahttpserver.sse import EventSource

app = HTTPServer()

CORS_header = {"Access-Control-Allow-Origin":"*"}

@app.route("GET", "/")
async def root(reader, writer, request):
    response = HTTPResponse(200, "text/html", close=True)
    await response.send(writer)
    await sendfile(writer, "index.html")
    await writer.drain()


response = HTTPResponse(200, "text/html", close=True, header=CORS_header)

@app.route("POST", "/frame")
async def frame(reader, writer, request):
    try:
        frame = await reader.readexactly(matrix.frameBytes)
        print("got bytes: ", len(frame))
        matrix.set_leds(frame)
        
    except EOFError as e:
        print("EOF error in /frame: ", e)
    finally:
        await response.send(writer)
        
        
    
    


@app.route("GET", "/favicon.ico")
async def favicon(reader, writer, request):
    response = HTTPResponse(200, "image/x-icon", close=True)
    await response.send(writer)
    await writer.drain()
    await sendfile(writer, "favicon.ico")


@app.route("GET", "/api/time")
async def api_time(reader, writer, request):
    """ Setup a server sent event connection to the client updating the time every second """
    eventsource = await EventSource(reader, writer)
    while True:
        await asyncio.sleep(1)
        t = time.localtime()
        try:
            await eventsource.send(event="time", data=f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}")
        except Exception:
            break  # close connection




@app.route("GET", "/api/stop")
async def api_stop(reader, writer, request):
    """ Force asyncio scheduler to stop, just like ctrl-c on the repl """
    response = HTTPResponse(200, "text/plain", close=True)
    await response.send(writer)
    writer.write("stopping server")
    await writer.drain()
    raise (KeyboardInterrupt)


async def say_hello_task():
    """ Show system is still alive """
    count = 0
    while True:
        print("I'm Alive ", count)
        count += 1
        await asyncio.sleep(60)


async def free_memory_task():
    """ Avoid memory fragmentation """
    while True:
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        def handle_exception(loop, context):
            # uncaught exceptions end up here
            import sys
            print("global exception handler:", context)
            sys.print_exception(context["exception"])
            sys.exit()

        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_exception)

        loop.create_task(say_hello_task())
        loop.create_task(free_memory_task())
        loop.create_task(app.start())

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(app.stop())
        asyncio.new_event_loop()

