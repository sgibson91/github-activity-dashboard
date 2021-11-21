import os
import sys

import pandas as pd
from ghapi.core import GhApi
from rich.console import Console

console = Console()


def make_clickable_url(name, url):
    return f'<a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>'


def perform_search(query, page_num=1):
    try:
        if page_num > 1:
            result = gh.search.issues_and_pull_requests(
                search_query,
                sort="updated",
                order="desc",
                per_page=100,
                page=page_num,
            )
        else:
            result = gh.search.issues_and_pull_requests(
                search_query,
                sort="updated",
                order="desc",
                per_page=100,
            )

        return result

    except Exception:
        pass


def process_results(items, filter_name, ignored_repos):
    results = []

    for item in items:
        repo_full_name = "/".join(item["repository_url"].split("/")[-2:])
        if repo_full_name in ignored_repos:
            continue

        details = {
            "number": item["number"],
            "raw_title": item["title"],
            "link": item["pull_request"]["html_url"]
            if "pull_request" in item.keys()
            else item["html_url"],
            "repo_name": repo_full_name,
            "repo_url": item["repository_url"]
            .replace("api.", "")
            .replace("repos/", ""),
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "pull_request": "pull_request" in item.keys(),
            "filter": filter_name,
        }

        results.append(details)

    return results


token = os.environ["ACCESS_TOKEN"] if "ACCESS_TOKEN" in os.environ else None
if token is None:
    raise ValueError("ACCESS_TOKEN must be set!")

gh = GhApi(token=token)

try:
    result = gh.users.get_authenticated()
    username = result["login"]
except Exception:
    console.print("[bold red]You are rate limited! :scream:")
    sys.exit(1)

if os.path.exists(".repoignore"):
    ignored_repos = []
    with open(".repoignore", "r") as f:
        for line in f.readlines():
            ignored_repos.append(line.strip("\n"))
else:
    ignored_repos = []

all_items = []
queries = {
    f"is:issue is:open assignee:{username}": "assigned",
    f"is:pr is:open assignee:{username}": "assigned",
    f"is:issue is:open author:{username}": "created",
    f"is:pr is:open author:{username}": "created",
    f"is:pr is:open user-review-requested:{username}": "review_requested",
}

for search_query, filter_name in queries.items():
    console.print(f"[bold blue]Query params:[/bold blue] {search_query}")
    result = perform_search(search_query)
    total_pages = (result["total_count"] // 100) + 1

    with console.status("[bold yellow]Processing query..."):
        details = process_results(result["items"], filter_name, ignored_repos)
        all_items.extend(details)

        if total_pages > 1:
            for i in range(2, total_pages + 1):
                result = perform_search(search_query, page_num=i)
                details = process_results(result["items"], filter_name, ignored_repos)
                all_items.extend(details)

    console.print("[bold yellow]Query processed!")


df = pd.DataFrame(all_items)

console.print("[bold blue]Saving results to CSV file...")
df["title"] = df.apply(lambda x: make_clickable_url(x["raw_title"], x["link"]), axis=1)
df["repository"] = df.apply(
    lambda x: make_clickable_url(x["repo_name"], x["repo_url"]), axis=1
)

df.to_csv("github-activity.csv")
console.print("[bold green]Done!")
