import os
import json
import uvicorn
import subprocess
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
import openai

# Load AI Proxy Token
aiproxy_token = os.getenv("AIPROXY_TOKEN")
if not aiproxy_token:
    raise ValueError("AIPROXY_TOKEN environment variable not set")

openai.api_key = aiproxy_token
app = FastAPI()

data_dir = Path("/data")

def run_command(command: list):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr}")

@app.post("/run")
def run_task(task: str = Query(..., description="Task description")):
    """Parses and executes a given task."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an automation assistant that translates tasks into precise execution steps."},
                {"role": "user", "content": task}
            ]
        )
        parsed_task = response["choices"][0]["message"]["content"].strip()
        
        # Execute parsed commands (simplified example for clarity)
        if "install uv" in parsed_task:
            run_command(["pip", "install", "uv"]) 
        elif "count Wednesdays" in parsed_task:
            file_path = data_dir / "dates.txt"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            with file_path.open() as f:
                count = sum(1 for line in f if "Wed" in line)
            (data_dir / "dates-wednesdays.txt").write_text(str(count))
        elif "sort contacts" in parsed_task:
            file_path = data_dir / "contacts.json"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            with file_path.open() as f:
                contacts = json.load(f)
            contacts.sort(key=lambda x: (x["last_name"], x["first_name"]))
            (data_dir / "contacts-sorted.json").write_text(json.dumps(contacts, indent=2))
        else:
            raise HTTPException(status_code=400, detail="Task not recognized")
        
        return {"message": "Task executed successfully", "task": parsed_task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
def read_file(path: str = Query(..., description="File path to read")):
    """Returns the content of a specified file."""
    file_path = data_dir / Path(path).name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return file_path.read_text()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
