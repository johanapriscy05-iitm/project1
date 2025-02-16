import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Callable
import requests
import git
import sqlite3
import duckdb
import markdown
import pandas as pd
from PIL import Image
from bs4 import BeautifulSoup
import speech_recognition as sr

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Security Manager: Restricts file access and prevents deletion
class SecurityManager:
    DATA_DIR = Path("/data").resolve()

    @staticmethod
    def validate_path(filepath: str) -> Path:
        """Ensures the file path is within /data."""
        path = Path(filepath).resolve()
        if not str(path).startswith(str(SecurityManager.DATA_DIR)):
            raise PermissionError("Access denied outside /data.")
        return path

    @staticmethod
    def prevent_deletion():
        """Overrides deletion functions to prevent file removal."""
        def restricted_function(*args, **kwargs):
            raise PermissionError("File deletion is not allowed.")

        os.remove = restricted_function
        shutil.rmtree = restricted_function

# Task Dispatcher: Maps task names to functions
class TaskDispatcher:
    tasks: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    @classmethod
    def register_task(cls, name: str):
        """Decorator to register a new task."""
        def wrapper(func: Callable[[Dict[str, Any]], Any]):
            cls.tasks[name] = func
            return func
        return wrapper

    @classmethod
    def execute_task(cls, task_name: str, params: Dict[str, Any]) -> Any:
        """Executes a registered task safely."""
        if task_name not in cls.tasks:
            raise ValueError(f"Task '{task_name}' is not supported.")
        return cls.tasks[task_name](params)

# Enforce security policies
SecurityManager.prevent_deletion()

# Task Implementations
@TaskDispatcher.register_task("fetch_api")
def fetch_api_task(params: Dict[str, Any]) -> str:
    """Executes all registered tasks."""
    results = []
    
    # Fetch API
    url = params.get("url")
    filename = params.get("filename", "output.json")
    if not url:
        raise ValueError("URL is required.")

    response = requests.get(url)
    response.raise_for_status()

    save_path = SecurityManager.validate_path(f"/data/{filename}")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    logging.info(f"Data saved to {save_path}")
    results.append(f"Data saved to {save_path}")

    # Clone Git Repository
    results.append(TaskDispatcher.execute_task("clone_git", {"repo_url": "https://github.com/johanapriscy05-iitm/.github-workflows-.git", "repo_name": "repo"}))

    # Run SQL Query
    results.append(TaskDispatcher.execute_task("run_sql", {"db_name": "database.db", "query": "SELECT 1"}))

    # Resize Image
    results.append(TaskDispatcher.execute_task("resize_image", {"image_path": "/data/sample.jpg", "output_path": "/data/resized.jpg", "size": (200, 200)}))

    # Scrape Website
    results.append(TaskDispatcher.execute_task("scrape_website", {"url": "https://example.com", "filename": "scraped.html"}))

    return "\n".join(results)

@TaskDispatcher.register_task("clone_git")
def clone_git_task(params: Dict[str, Any]) -> str:
    repo_url = params.get("repo_url")
    save_path = SecurityManager.validate_path(f"/data/{params.get('repo_name', 'repo')}")

    if save_path.exists():
        try:
            # If repo exists, pull the latest changes
            repo = git.Repo(save_path)
            origin = repo.remotes.origin
            origin.pull()
            logging.info(f"Repo already exists. Pulled latest changes in {save_path}")
            return f"Repo already exists. Pulled latest changes in {save_path}"
        except Exception as e:
            logging.error(f"Error pulling changes: {e}")
            return f"Error pulling changes: {e}"
    else:
        # Clone the repository if it does not exist
        git.Repo.clone_from(repo_url, save_path)
        logging.info(f"Repo cloned to {save_path}")
        return f"Repo cloned to {save_path}"

@TaskDispatcher.register_task("run_sql")
def run_sql_task(params: Dict[str, Any]) -> Any:
    db_path = SecurityManager.validate_path(f"/data/{params.get('db_name', 'database.db')}")
    query = params.get("query")

    if not query:
        raise ValueError("SQL query is required.")

    conn = sqlite3.connect(db_path) if params.get("db_type", "sqlite") == "sqlite" else duckdb.connect(str(db_path))
    result = conn.execute(query).fetchall()
    conn.close()
    return f"SQL query executed: {query} -> {result}"

@TaskDispatcher.register_task("resize_image")
def resize_image_task(params: Dict[str, Any]) -> str:
    image_path = SecurityManager.validate_path(params.get("image_path"))
    output_path = SecurityManager.validate_path(params.get("output_path"))
    size = params.get("size", (100, 100))

    img = Image.open(image_path)
    img = img.resize(size)
    img.save(output_path)
    logging.info(f"Image saved to {output_path}")
    return f"Image saved to {output_path}"

@TaskDispatcher.register_task("scrape_website")
def scrape_website_task(params: Dict[str, Any]) -> str:
    url = params.get("url")
    filename = params.get("filename", "scraped_data.html")

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    save_path = SecurityManager.validate_path(f"/data/{filename}")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    logging.info(f"Scraped data saved to {save_path}")
    return f"Scraped data saved to {save_path}"

# Execute fetch_api to trigger all tasks
result = TaskDispatcher.execute_task("fetch_api", {"url": "https://jsonplaceholder.typicode.com/posts", "filename": "posts.json"})
print(result)
