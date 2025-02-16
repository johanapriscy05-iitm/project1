# Project Setup Instructions

## Prerequisites
Ensure that you have the following installed on your system:
- WSL (Windows Subsystem for Linux)
- Ubuntu
- VS Code
- Podman

## Steps

1. **Restart your system** and open the terminal.

    ```bash
    wsl -l -v
    ```

2. **Open Ubuntu**.

    ```bash
    # It will open your VS code on your Ubuntu WSL
    code
    ```

3. **Make a directory** in the VS Code Terminal.

    ```bash
    mkdir <your-repo-name>
    cd <your-repo-name>
    ```

4. **Initialize Git in VS Code Terminal**.

    ```bash
    git init
    git config --global user.name "iitm-rollno"
    git config --global user.email "iitm-email"
    git remote add <your-repo-name> <your-repo-link.git>
    git pull <your-repo-name> main
    ```

5. **Authenticate yourself** using VS Code to allow authentication for the repo.

6. **Go to your repo**. On the left extreme of VS Code, there’s a node-type shape; open that and figure out where you have created the repo using the open folder.

7. **Open Ubuntu Terminal** (not VS Code terminal).

    ```bash
    cd <your-repo-name>
    ls  # to list all the files and ensure you are in the GitHub repo
    ```

8. **Do your first commit**. Make a new file `app.py` in VS Code.

## Build the Docker Image
Make sure you have Podman installed. Run the following command to build the Docker image:

```bash
podman build -t user-name/repo-name .
```
## Run the Docker Container
- Run the container with the following command:

```bash
podman run -e AIPROXY_TOKEN=$env:AIPROXY_TOKEN -p 8000:8000 user-name/repo-name
```
## Access the API
- You can access the API at http://localhost:8000/. Use the following endpoints:

- Home Endpoint: GET /
  - Returns a simple message to check if the server is running.
- Run Task Endpoint: POST /run?task=<task_description>
  - Execute a specific task by providing a task description.
- Read File Endpoint: GET /read?path=<file_path>
  - Read the contents of a specified file.
### Example Commands
- To run a specific task, use:
```bash
curl -X POST "http://localhost:8000/run?task=Format+/data/format.md+using+prettier"
```
- To read a file, use:
```bash
curl "http://localhost:8000/read?path=/data/format.md"
```
### Contribution Guidelines
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Create a pull request to the main repository.
### License
- This project is licensed under the MIT License. See the LICENSE file for details.
