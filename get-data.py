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


def process_results(items, filter_name):
    results = []

    for item in items:
        details = {
            "number": item["number"],
            "title": item["title"],
            "link": item["pull_request"]["html_url"]
            if "pull_request" in item.keys()
            else item["html_url"],
            "repository": "",
            "repo_name": "/".join(item["repository_url"].split("/")[-2:]),
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

n_proc = os.cpu_count()
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
        details = process_results(result["items"], filter_name)
        all_items.extend(details)

        if total_pages > 1:
            for i in range(2, total_pages + 1):
                result = perform_search(search_query, page_num=i)
                details = process_results(result["items"], filter_name)
                all_items.extend(details)

    console.print("[bold yellow]Query processed!")


df = pd.DataFrame(all_items)

console.print("[bold blue]Saving results to CSV file...")
df["title"] = df.apply(lambda x: make_clickable_url(x["title"], x["link"]), axis=1)
df["repository"] = df.apply(
    lambda x: make_clickable_url(x["repo_name"], x["repo_url"]), axis=1
)

# df.drop_duplicates(subset="title", keep="last", inplace=True, ignore_index=True)
df.to_csv("github_activity.csv")
console.print("[bold green]Done!")
