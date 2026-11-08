import json
import urllib.request
from pathlib import Path

USERNAME = "GariNikhil"
PROFILE_REPO = "GariNikhil"

README_PATH = Path(__file__).resolve().parents[2] / "README.md"

START_MARKER = "<!-- PROJECTS_START -->"
END_MARKER = "<!-- PROJECTS_END -->"

API_URL = (
    f"https://api.github.com/users/{USERNAME}/repos"
    "?per_page=100&type=owner&sort=updated"
)


def fetch_repositories():
    repositories = []
    page = 1

    while True:
        url = f"{API_URL}&page={page}"

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "GariNikhil-Profile-README-Updater",
            },
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def select_top_repositories(repositories):
    eligible = [
        repo
        for repo in repositories
        if not repo["fork"]
        and not repo["archived"]
        and repo["name"].lower() != PROFILE_REPO.lower()
    ]

    eligible.sort(
        key=lambda repo: (
            repo.get("stargazers_count", 0),
            repo.get("pushed_at") or "",
        ),
        reverse=True,
    )

    return eligible[:5]


def clean_markdown(value, limit=80):
    if not value:
        return "—"

    text = str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def generate_table(repositories):
    lines = [
        "| # | Repository | Description | Language | Stars |",
        "|:--:|:---|:---|:---:|:--:|",
    ]

    for index, repo in enumerate(repositories, start=1):
        name = repo["name"]
        url = repo["html_url"]
        description = clean_markdown(repo.get("description"))
        language = clean_markdown(repo.get("language"))
        stars = repo.get("stargazers_count", 0)

        lines.append(
            f"| {index} | [{name}]({url}) | {description} | {language} | ⭐ {stars} |"
        )

    if not repositories:
        lines.append("| — | No public repositories found | — | — | — |")

    return "\n".join(lines)


def update_readme():
    if not README_PATH.exists():
        raise FileNotFoundError(f"README not found: {README_PATH}")

    readme = README_PATH.read_text(encoding="utf-8")

    if readme.count(START_MARKER) != 1:
        raise ValueError("README must contain exactly one PROJECTS_START marker.")

    if readme.count(END_MARKER) != 1:
        raise ValueError("README must contain exactly one PROJECTS_END marker.")

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)

    if start >= end:
        raise ValueError("README project markers are in the wrong order.")

    repositories = fetch_repositories()
    top_five = select_top_repositories(repositories)
    table = generate_table(top_five)

    updated_readme = readme[:start] + "\n\n" + table + "\n\n" + readme[end:]

    if updated_readme != readme:
        README_PATH.write_text(updated_readme, encoding="utf-8")
        print("README updated successfully.")
    else:
        print("README is already up to date.")

    print(f"Repositories displayed: {len(top_five)}")


if __name__ == "__main__":
    try:
        update_readme()
    except Exception as error:
        print(f"Update failed: {error}")
        raise
