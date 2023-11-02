#Wordsmith API

from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from fastapi import FastAPI, BackgroundTasks
import subprocess
import asyncio
import os
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/templates", StaticFiles(directory="templates"), name="static")  #Serves static image from templates folder

#response_class=HTMLResponse from index.html
@app.get("/", response_class=HTMLResponse) 
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#Sends user query and saves it temporarily in hi.txt
@app.post("/send_message") 
def send_message(message: dict):
    user_message = message.get('message')

    if user_message:
        try:
            with open("hi.txt", "w") as file:
                file.write(user_message)
            return JSONResponse(content={"message": "Message saved successfully"})
        except Exception as e:
            return JSONResponse(content={"error": f"Error saving message: {str(e)}"}, status_code=500)
    else:
        raise HTTPException(status_code=400, detail="No message provided")
    

#Executes privateGPT.py and returns bot response
@app.post("/execute")
async def execute_code(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_process)
    return {"message": "Process started"}

def long_running_process():
    process = subprocess.Popen(
        ['python', '/workspaces/GPT-Helper/privateGPT/privateGPT.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )

    while process.poll() is None:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)  # Wait if no data is available
            continue

    # Process has exited, yield any remaining output
    for line in process.stdout:
        pass  # Do nothing with the output

#Returns bot response after executing privateGPT.py and saving it in bot_responsesN.txt
@app.get("/get_bot_responses")
def get_bot_response_with_largest_number():
    try:
        base_filename = "bot_responses"
        response_extension = ".txt"
        
        largest_number = None
        largest_filename = None

        for filename in os.listdir():
            if filename.startswith(base_filename) and filename.endswith(response_extension):
                try:
                    number = int(filename[len(base_filename):-len(response_extension)])
                    if largest_number is None or number > largest_number:
                        largest_number = number
                        largest_filename = filename
                except ValueError:
                    pass  # Skip files that don't match the naming pattern
        
        if largest_filename:
            with open(largest_filename, "r") as file:
                response_text = file.read()
                return PlainTextResponse(content=response_text)
        else:
            return JSONResponse(content={"message": "No bot response found"}, status_code=404)
            
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

        
