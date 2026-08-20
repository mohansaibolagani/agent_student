import os
import sys

# Ensure project modules can be loaded
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

site_packages = os.path.join(project_dir, ".venv", "Lib", "site-packages")
if os.path.exists(site_packages) and site_packages not in sys.path:
    sys.path.insert(0, site_packages)

from my_agent.tools import push_project_to_github

if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "mohansaibolagani/agent_student"
    print(f"Pushing project to GitHub repository: {repo} ...")
    result = push_project_to_github(repo_name=repo, project_dir=project_dir)
    print(result)
