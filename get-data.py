import calendar
import os
import sys
from datetime import date, timedelta

import pandas as pd
from ghapi.core import GhApi
from rich.console import Console

console = Console()


def make_clickable_url(name, url):
    return f'<a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>'


def get_last_month():
    year = date.today().year
    month = date.today().month

    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1

    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])

    return month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d")


def get_last_week():
    year, week_num, _ = date.today().isocalendar()

    if week_num == 1:
        week_num = 52
        year -= 1
    else:
        week_num -= 1

    new_date = date(year, 1, 1) + timedelta(7 * week_num)
    weekday = new_date.weekday()
    week_start = new_date - timedelta(weekday)
    week_end = new_date + timedelta(6 - weekday)

    return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")


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
            "closed_at": item["closed_at"],
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

month_start, month_end = get_last_month()
week_start, week_end = get_last_week()

all_items = []
queries = {
    f"is:issue is:open assignee:{username}": "assigned",
    f"is:pr is:open assignee:{username}": "assigned",
    f"is:issue is:open author:{username}": "created",
    f"is:pr is:open author:{username}": "created",
    f"is:pr is:open user-review-requested:{username}": "review_requested",
    f"is:issue assignee:{username} closed:{month_start}..{month_end}": "assigned_and_closed_last_month",
    f"is:issue author:{username} closed:{month_start}..{month_end}": "created_and_closed_last_month",
    f"is:pr assignee:{username} closed:{month_start}..{month_end}": "assigned_and_closed_last_month",
    f"is:pr author:{username} closed:{month_start}..{month_end}": "created_and_closed_last_month",
    f"is:issue assignee:{username} closed:{week_start}..{week_end}": "assigned_and_closed_last_week",
    f"is:issue author:{username} closed:{week_start}..{week_end}": "created_and_closed_last_week",
    f"is:pr assignee:{username} closed:{week_start}..{week_end}": "assigned_and_closed_last_week",
    f"is:pr author:{username} closed:{week_start}..{week_end}": "created_and_closed_last_week",
    f"is:issue assignee:{username} updated:{week_start}..{week_end}": "assigned_and_updated_last_week",
    f"is:issue author:{username} updated:{week_start}..{week_end}": "created_and_updated_last_week",
    f"is:pr assignee:{username} updated:{week_start}..{week_end}": "assigned_and_updated_last_week",
    f"is:pr author:{username} updated:{week_start}..{week_end}": "created_and_updated_last_week",
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

df.to_csv("github-activity.csv", index=False)
console.print("[bold green]Done!")
