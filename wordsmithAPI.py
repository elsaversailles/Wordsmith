from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
import subprocess
import asyncio
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/templates", StaticFiles(directory="templates"), name="static")  # serve pics


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
