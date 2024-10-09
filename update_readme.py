import requests
import os

def fetch_pr_status(pr_url):
    parts = pr_url.split('/')
    owner = parts[3]
    repo = parts[4]
    pull_number = parts[6]
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    print(f"API URL: {api_url}")
    response = requests.get(api_url)

    if response.status_code == 200:
        pr_data = response.json()
        title = pr_data['title']
        status = pr_data['state']
        link = pr_data['html_url']
        
        return {'title': title, 'status': status, 'link': link}
    else:
        return {"error": "Error fetching PR data."}

def read_existing_entries(content):
    existing_entries = set()
    for line in content:
        if line.startswith('| Title'):
            continue
        if line.strip():  # Check if the line is not empty
            parts = line.split('|')
            if len(parts) > 1:
                title = parts[1].strip()
                existing_entries.add(title)
    return existing_entries

def update_readme(pr_urls):
    pr_entries = []
    existing_entries = set()

    # Read current README content
    readme_path = 'README.md'
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as file:
            content = file.readlines()
            existing_entries = read_existing_entries(content)
    else:
        content = []

    for pr_url in pr_urls:
        pr_info = fetch_pr_status(pr_url)
        if 'error' not in pr_info:
            # Only add if the title is not already present
            if pr_info['title'] not in existing_entries:
                pr_entries.append(f"| {pr_info['title']} | [{pr_info['link']}]({pr_info['link']}) | {pr_info['status']} | YYYY-MM-DD |\n")
                existing_entries.add(pr_info['title'])

    # Create the table header and separator
    print("Creating Table")
    table_header = "| Title | Link | Status | Date |\n"
    table_separator = "|-------|------|--------|------|\n"

    # Check if the table already exists
    table_exists = any(line.startswith('| Title') for line in content)

    if table_exists:
        # Find the table and replace it
        for i, line in enumerate(content):
            if line.startswith('| Title'):
                # Clear existing entries after the header and separator
                content = content[:i+1] + [table_separator] + pr_entries + content[i+2:]
                break
    else:
        # If the table header is not found, create it
        content.append(table_header)
        content.append(table_separator)
        content.extend(pr_entries)

    # Write back to README
    print("Writing to table")
    with open(readme_path, 'w') as file:
        file.writelines(content)

if __name__ == "__main__":
    # List of PR URLs you want to track
    pr_urls = [
        "https://github.com/TBD54566975/dwn-sdk-js/pull/818",  # Add more PR URLs as needed
        "https://github.com/TBD54566975/dwn-sdk-js/pull/815"
    ]
    update_readme(pr_urls)
