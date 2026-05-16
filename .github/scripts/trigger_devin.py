import os
import requests

def get_codeql_alerts(repo_url, github_token):
    # repo_url is like https://github.com/t11a/medsecure-legacy-api
    repo_path = repo_url.replace("https://github.com/", "")
    url = f"https://api.github.com/repos/{repo_path}/code-scanning/alerts?state=open"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    print(f"Fetching CodeQL alerts from {repo_path}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching alerts: {response.status_code} - {response.text}")
        return []

def main():
    devin_api_key = os.getenv("DEVIN_API_KEY")
    devin_org_id = os.getenv("DEVIN_ORG_ID")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("REPO_URL")

    if not all([devin_api_key, devin_org_id, github_token, repo_url]):
        print("Error: Missing required environment variables.")
        exit(1)

    alerts = get_codeql_alerts(repo_url, github_token)
    if not alerts:
        print("No open alerts found.")
        return

    for alert in alerts:
        rule_name = alert.get("rule", {}).get("name", "Unknown Rule")
        rule_description = alert.get("rule", {}).get("description", "No description")
        severity = alert.get("rule", {}).get("security_severity_level", "unknown")
        
        location = alert.get("most_recent_instance", {}).get("location", {})
        file_path = location.get("path", "Unknown file")
        start_line = location.get("start_line", "Unknown line")

        prompt = f"""CodeQL has detected a '{severity}' security vulnerability in the repository {repo_url}.

Details:
- Rule: {rule_name}
- Description: {rule_description}
- File: {file_path}
- Line: {start_line}

Your task:
1. Clone the repository {repo_url}
2. Fix this security vulnerability.
3. Ensure the fix does not break existing functionality.
4. Create a Pull Request with a clear description indicating that this is an automated CodeQL remediation.
"""

        print(f"Triggering Devin for alert: {rule_name} in {file_path}:{start_line}")
        
        url = f"https://api.devin.ai/v3/organizations/{devin_org_id}/sessions"
        headers = {
            "Authorization": f"Bearer {devin_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Devin session created successfully! Session URL: {session_data.get('url')}")
        else:
            print(f"❌ Failed to create Devin session: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
