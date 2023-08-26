from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
import subprocess
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/templates", StaticFiles(directory="templates"), name="static")  # serve pics


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/execute")
def execute_code():
    process = subprocess.Popen(
        ['python', '/workspaces/GPT-Helper/privateGPT/privateGPT.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )

    async def generate():
        while process.poll() is None:
            line = process.stdout.readline()
            if not line:
                await asyncio.sleep(0.1)  # Wait if no data is available
                continue
            yield line

        # Process has exited, yield any remaining output
        for line in process.stdout:
            yield line

    return StreamingResponse(generate())


@app.get("/get_bot_responses")
def get_bot_responses():
    try:
        with open("bot_responses.txt", "r") as file:
            responses = file.read()
            return PlainTextResponse(content=responses) #read as text
    except FileNotFoundError:
        return JSONResponse(content={"error": "bot_responses.txt not found"}, status_code=404)
