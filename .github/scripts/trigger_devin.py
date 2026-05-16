import os
import json
import requests

def main():
    devin_api_key = os.getenv("DEVIN_API_KEY")
    devin_org_id = os.getenv("DEVIN_ORG_ID")
    repo_url = os.getenv("REPO_URL")
    alert_json_str = os.getenv("ALERT_JSON")

    if not devin_api_key or not devin_org_id:
        print("Error: DEVIN_API_KEY or DEVIN_ORG_ID is missing from GitHub Secrets.")
        exit(1)

    try:
        alert = json.loads(alert_json_str)
    except Exception as e:
        print(f"Failed to parse ALERT_JSON: {e}")
        exit(1)

    rule_name = alert.get("rule", {}).get("name", "Unknown Rule")
    rule_description = alert.get("rule", {}).get("description", "No description")
    severity = alert.get("rule", {}).get("security_severity_level", "unknown")
    
    # Extract location (using the most recent instance)
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
        print(f"✅ Devin session created successfully!")
        print(f"Session ID: {session_data.get('session_id')}")
        print(f"Session URL: {session_data.get('url')}")
    else:
        print(f"❌ Failed to create Devin session: {response.status_code} - {response.text}")
        exit(1)

if __name__ == "__main__":
    main()
