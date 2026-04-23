# skills/automation/github_specialist.py
import httpx
import os
import logging

logger = logging.getLogger("nex-skills")

async def github_specialist(input_data: dict):
    """
    Interact with GitHub (List Repos, Check Issues, Repo Info).
    Params: action (list_repos, repo_info), user (string, optional)
    """
    action = input_data.get("action", "list_repos")
    target_user = input_data.get("user")
    repo_name = input_data.get("repo")
    
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"token {token}" if token else "",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        async with httpx.AsyncClient() as client:
            if action == "list_repos":
                url = f"https://api.github.com/user/repos" if not target_user else f"https://api.github.com/users/{target_user}/repos"
                res = await client.get(url, headers=headers)
                
                if res.status_code != 200:
                    return {"status": "error", "message": f"GitHub API error ({res.status_code}): {res.text[:100]}"}
                
                repos = res.json()
                if not isinstance(repos, list):
                    return {"status": "error", "message": f"GitHub unexpected response format"}
                
                repo_list = [r['full_name'] for r in repos[:5]]
                return {"status": "success", "message": f"GITHUB | Repo found: {', '.join(repo_list)}"}
            
            elif action == "repo_info" and repo_name:
                url = f"https://api.github.com/repos/{repo_name}"
                res = await client.get(url, headers=headers)
                
                if res.status_code != 200:
                    return {"status": "error", "message": f"GitHub specific repo error ({res.status_code})"}

                repo_data = res.json()
                stars = repo_data.get('stargazers_count', 0)
                desc = repo_data.get('description', 'No description')
                return {"status": "success", "message": f"GITHUB | Repo: {repo_name} | Stars: {stars} | Desc: {desc}"}
                
            return {"status": "error", "message": "Invalid GitHub action or missing params"}

    except Exception as e:
        return {"status": "error", "message": f"GitHub API failed: {str(e)}"}
