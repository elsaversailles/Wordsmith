from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import subprocess
import asyncio
import threading

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def stream_subprocess_output(process, queue):
    for line in iter(process.stdout.readline, ''):
        queue.put(line)
    process.stdout.close()

@app.post("/execute")
def execute_code(background_tasks: BackgroundTasks):
    process = subprocess.Popen(
        ['python', '/workspaces/GPT-Helper/privateGPT/privateGPT.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )

    output_queue = asyncio.Queue()
    background_tasks.add_task(stream_subprocess_output, process, output_queue)

    async def generate():
        while process.poll() is None:
            try:
                line = await asyncio.wait_for(output_queue.get(), timeout=1.0)
                yield line
            except asyncio.TimeoutError:
                continue

    return StreamingResponse(generate())
