

import base64
import os
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_github_token(provided_token: str = "") -> str:
    """Retrieve GitHub token from argument, environment variables, or local .env file."""
    if provided_token:
        return provided_token
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return ""


def calculate_average(marks: list[float]) -> float:
    """Calculate the average of a list of marks."""
    return sum(marks) / len(marks)


def create_file(filename: str, content: str) -> str:
    """Create a new file with the specified name and write the provided content into it.

    Args:
        filename: The name or path of the file to create (e.g., 'output.txt', 'notes.md').
        content: The text content to write into the file.

    Returns:
        A confirmation message indicating success or details of an error.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Successfully created '{filename}'."
    except Exception as e:
        return f"Failed to create '{filename}': {str(e)}"


def push_to_github(
    repo_name: str,
    file_path: str,
    content: str = "",
    local_file_path: str = "",
    commit_message: str = "Update file via agent",
    branch: str = "main",
    github_token: str = "",
) -> str:
    """Push a file or custom code content to a GitHub repository using the GitHub REST API.

    Args:
        repo_name: Target repository name in 'owner/repo' format (e.g. 'username/repo-name') or just 'repo-name'.
        file_path: Destination path in the GitHub repository (e.g. 'my_agent/tools.py').
        content: The text content to push. If empty, content is read from local_file_path.
        local_file_path: Path to the local file to read content from if 'content' is not provided.
        commit_message: Commit message describing the changes.
        branch: The branch to push to (default: 'main').
        github_token: GitHub Personal Access Token (PAT). Defaults to GITHUB_TOKEN or GH_TOKEN environment variable.

    Returns:
        A confirmation message with commit details or an error message.
    """
    token = _get_github_token(github_token)
    if not token:
        return (
            "Error: GitHub token is required. Please provide 'github_token' argument "
            "or set the GITHUB_TOKEN or GH_TOKEN in environment / .env file."
        )

    # Determine file content to push
    file_text = content
    if not file_text:
        source_path = local_file_path or (file_path if os.path.exists(file_path) else "")
        if source_path and os.path.exists(source_path):
            try:
                with open(source_path, "r", encoding="utf-8") as f:
                    file_text = f.read()
            except Exception as e:
                return f"Error reading local file '{source_path}': {str(e)}"
        else:
            return (
                "Error: No content provided and valid local file was not found. "
                "Please provide 'content' or a valid 'local_file_path'."
            )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Resolve full repo name (owner/repo) if only repo name was provided
    full_repo = repo_name.strip()
    if "/" not in full_repo:
        user_res = requests.get("https://api.github.com/user", headers=headers)
        if user_res.status_code == 200:
            user_login = user_res.json().get("login")
            if user_login:
                full_repo = f"{user_login}/{full_repo}"
        else:
            return f"Error resolving GitHub user details: {user_res.status_code} - {user_res.text}"

    # Check if the repository exists, or attempt to create it if it doesn't
    repo_check_url = f"https://api.github.com/repos/{full_repo}"
    repo_res = requests.get(repo_check_url, headers=headers)
    if repo_res.status_code == 404:
        repo_short_name = full_repo.split("/")[-1]
        create_repo_res = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={"name": repo_short_name, "auto_init": True},
        )
        if create_repo_res.status_code not in (200, 201):
            return (
                f"Repository '{full_repo}' does not exist and could not be created: "
                f"{create_repo_res.status_code} - {create_repo_res.text}"
            )

    # Check if the file already exists in the repository to retrieve its SHA
    contents_url = f"https://api.github.com/repos/{full_repo}/contents/{file_path.lstrip('/')}"
    get_file_res = requests.get(f"{contents_url}?ref={branch}", headers=headers)
    sha = None
    if get_file_res.status_code == 200:
        sha = get_file_res.json().get("sha")

    # Encode content to base64
    encoded_bytes = base64.b64encode(file_text.encode("utf-8"))
    encoded_content = encoded_bytes.decode("utf-8")

    payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    put_res = requests.put(contents_url, headers=headers, json=payload)
    if put_res.status_code in (200, 201):
        commit_sha = put_res.json().get("commit", {}).get("sha", "unknown")
        action = "Updated" if sha else "Created"
        return (
            f"Successfully {action.lower()} and pushed '{file_path}' to repository '{full_repo}' "
            f"on branch '{branch}'. Commit SHA: {commit_sha}"
        )
    else:
        return f"Failed to push file to GitHub: {put_res.status_code} - {put_res.text}"


def push_project_to_github(
    repo_name: str,
    project_dir: str = ".",
    commit_message: str = "Add project files via agent",
    branch: str = "main",
    github_token: str = "",
    is_private: bool = False,
) -> str:
    """Push all files in the current project to a GitHub repository using the GitHub REST API.

    Args:
        repo_name: Target repository name in 'owner/repo' format (e.g. 'mohansaibolagani/student-assistant') or 'student-assistant'.
        project_dir: Local project directory to push (default: current directory '.').
        commit_message: Commit message for the pushed files.
        branch: The branch to push to (default: 'main').
        github_token: GitHub Personal Access Token (PAT). Defaults to GITHUB_TOKEN or GH_TOKEN environment variable.
        is_private: Whether the repository should be private if it needs to be created (default: False).

    Returns:
        A detailed summary of pushed files and repository link or error message.
    """
    token = _get_github_token(github_token)
    if not token:
        return (
            "Error: GitHub token is required. Please provide 'github_token' argument "
            "or set the GITHUB_TOKEN or GH_TOKEN in environment / .env file."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Resolve full repo name
    full_repo = repo_name.strip()
    if "/" not in full_repo:
        user_res = requests.get("https://api.github.com/user", headers=headers)
        if user_res.status_code == 200:
            user_login = user_res.json().get("login")
            if user_login:
                full_repo = f"{user_login}/{full_repo}"
        else:
            return f"Error resolving GitHub user details: {user_res.status_code} - {user_res.text}"

    # Check if repo exists; create if it doesn't
    repo_check_url = f"https://api.github.com/repos/{full_repo}"
    repo_res = requests.get(repo_check_url, headers=headers)
    if repo_res.status_code == 404:
        repo_short_name = full_repo.split("/")[-1]
        create_repo_res = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={"name": repo_short_name, "private": is_private, "auto_init": True},
        )
        if create_repo_res.status_code not in (200, 201):
            return (
                f"Repository '{full_repo}' does not exist and could not be created: "
                f"{create_repo_res.status_code} - {create_repo_res.text}"
            )

    ignored_dirs = {".git", ".venv", "venv", "__pycache__", ".idea", ".vscode"}
    ignored_extensions = {".pyc", ".pyo", ".pyd"}
    ignored_files = {".env", ".env.local"}

    pushed_files = []
    failed_files = []

    base_path = os.path.abspath(project_dir)
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            if file in ignored_files or any(file.endswith(ext) for ext in ignored_extensions):
                continue

            local_abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_abs_path, base_path).replace("\\", "/")

            try:
                with open(local_abs_path, "r", encoding="utf-8", errors="replace") as f:
                    file_content = f.read()
            except Exception as e:
                failed_files.append(f"{rel_path} (Read error: {str(e)})")
                continue

            contents_url = f"https://api.github.com/repos/{full_repo}/contents/{rel_path}"
            get_res = requests.get(f"{contents_url}?ref={branch}", headers=headers)
            sha = get_res.json().get("sha") if get_res.status_code == 200 else None

            encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")
            payload = {
                "message": f"{commit_message} - {rel_path}",
                "content": encoded_content,
                "branch": branch,
            }
            if sha:
                payload["sha"] = sha

            put_res = requests.put(contents_url, headers=headers, json=payload)
            if put_res.status_code in (200, 201):
                pushed_files.append(rel_path)
            else:
                failed_files.append(f"{rel_path} (HTTP {put_res.status_code})")

    summary = [
        f"Push complete for repository: https://github.com/{full_repo}",
        f"Total files pushed successfully: {len(pushed_files)}",
    ]
    if pushed_files:
        summary.append("Pushed files:\n- " + "\n- ".join(pushed_files))
    if failed_files:
        summary.append("Failed files:\n- " + "\n- ".join(failed_files))

    return "\n\n".join(summary)


    

