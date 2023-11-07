#Wordsmith API
from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import asyncio
import os
import time
import psutil
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/templates", StaticFiles(directory="templates"), name="static")  # Serves static image from templates folder

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/fileUpload", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("fileupload.html", {"request": request})


@app.get("/help", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(f'/workspaces/GPT-Helper/privateGPT/source_documents/{file.filename}', 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}

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

@app.get("/cpu-usage")
async def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)  # Query CPU usage for 1 second
    return {"cpu_usage": cpu_percent}  

def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024**3), 2)  # Convert to GB and round to 2 decimal places

@app.get("/ram-usage")
async def get_ram_usage():
    virtual_memory = psutil.virtual_memory()
    ram_usage = {
        "total": bytes_to_gb(virtual_memory.total),
        "available": bytes_to_gb(virtual_memory.available),
        "used": bytes_to_gb(virtual_memory.used),
        "free": bytes_to_gb(virtual_memory.free),
    }
    return {"ram_usage": ram_usage}

def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024**3), 2)  # Convert to GB and round to 2 decimal places

@app.get("/free-disk-space")
async def get_free_disk_space():
    partitions = psutil.disk_partitions()
    free_space_gb = {}
    
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        free_space_gb[partition.device] = bytes_to_gb(usage.free)
    
    return {"free_disk_space": free_space_gb}
