
import os
import requests
from datetime import datetime, timezone

USERNAME = "GariNikhil"
README_FILE = "README.md"

START = "<!-- PROJECTS_START -->"
END = "<!-- PROJECTS_END -->"

def get_repositories():
    url = f"https://api.github.com/users/{USERNAME}/repos"

    repos = []
    page = 1

    while True:
        response = requests.get(
            url,
            params={
                "sort": "updated",
                "per_page": 100,
                "page": page,
                "type": "owner"
            },
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return [
        repo for repo in repos
        if not repo["fork"] and not repo["archived"]
    ]

def generate_projects(repos):
    lines = [
        "| Project | Description | Language | Stars |",
        "|---|---|---|---|"
    ]

    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        description = (
            repo.get("description") or "No description provided."
        ).replace("|", " ").replace("\n", " ")

        language = repo.get("language") or "N/A"
        stars = repo["stargazers_count"]

        lines.append(
            f"| [{name}]({url}) | {description} | "
            f"{language} | ⭐ {stars} |"
        )

    if not repos:
        lines.append("| No projects yet | | | |")

    return "\n".join(lines)

def update_readme():
    with open(README_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    if START not in content or END not in content:
        raise ValueError("Project markers missing from README.md")

    repos = get_repositories()
    projects = generate_projects(repos)

    before, remainder = content.split(START, 1)
    _, after = remainder.split(END, 1)

    updated = (
        before + START + "\n" +
        projects + "\n" +
        END + after
    )

    if updated != content:
        with open(README_FILE, "w", encoding="utf-8") as file:
            file.write(updated)

        print(f"Updated {len(repos)} repositories.")
    else:
        print("README is already up to date.")

if __name__ == "__main__":
    update_readme()
