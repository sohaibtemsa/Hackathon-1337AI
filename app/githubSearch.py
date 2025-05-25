import requests
from urllib.parse import urlparse

def get_repo_info(github_url):
    # Extract user and repo from URL
    parsed = urlparse(github_url)
    path_parts = parsed.path.strip('/').split('/')
    if len(path_parts) < 2:
        return {"error": "Invalid GitHub URL format. Must be https://github.com/user/repo"}

    user, repo = path_parts[:2]
    api_base = f"https://api.github.com/repos/{user}/{repo}"

    # Get README
    readme_url = f"{api_base}/readme"
    readme_response = requests.get(readme_url, headers={"Accept": "application/vnd.github.v3.raw"})
    readme_content = readme_response.text if readme_response.status_code == 200 else "README not found"

    # Get file tree
    tree_url = f"{api_base}/git/trees/HEAD?recursive=1"
    tree_response = requests.get(tree_url)
    if tree_response.status_code == 200:
        files = [item['path'] for item in tree_response.json().get("tree", []) if item['type'] == 'blob']
    else:
        files = ["Could not fetch file structure"]

    return {
        "readme": readme_content,
        "file_structure": files
    }

# Example use
info = get_repo_info("https://github.com/openai/openai-python")
print("README:\n", info["readme"])
print("\nProject Files:\n", "\n".join(info["file_structure"]))
