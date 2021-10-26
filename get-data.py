import os
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd
from ghapi.core import GhApi
from ghapi.page import paged


def make_clickable_url(name, url):
    return f'<a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>'


def process_gh_results(page, i):
    results = []

    for item in page:
        details = {
            "number": item["number"],
            "title": item["title"],
            "link": item["pull_request"]["html_url"]
            if "pull_request" in item.keys()
            else item["html_url"],
            "repository": "",
            "repo_name": item["repository"]["full_name"],
            "repo_url": item["repository"]["html_url"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "pull_request": "pull_request" in item.keys(),
            "filter": query["filter"],
        }

        if ("pull_request" in item.keys()) and (query["filter"] == "repos"):
            pull_result = paged(
                gh.pulls.list_requested_reviewers,
                item["repository"]["owner"]["login"],
                item["repository"]["name"],
                item["number"],
                per_page=100,
            )

            reviewers = [
                user["login"]
                for pull_page in pull_result
                for user in pull_page["users"]
            ]

            if username in reviewers:
                details["filter"] = "review_requested"

        results.append(details)

    return results


n_proc = os.cpu_count()
token = os.environ["ACCESS_TOKEN"] if "ACCESS_TOKEN" in os.environ else None

if token is None:
    raise ValueError("ACCESS_TOKEN must be set!")

gh = GhApi(token=token)

result = gh.users.get_authenticated()
username = result["login"]

all_items = []
filters = ["assigned", "created"]

queries = [
    {"filter": "assigned", "pulls": False},
    {"filter": "created", "pulls": False},
    {"filter": "repos", "pulls": True},
]

for query in queries:
    result = paged(
        gh.issues.list,
        filter=query["filter"],
        pulls=query["pulls"],
        state="open",
        sort="updated",
        direction="desc",
        per_page=100,
    )

    with ProcessPoolExecutor(n_proc) as executor:
        futures = [executor.submit(process_gh_results, page, i) for i, page in enumerate(result)]

        for future in as_completed(futures):
            all_items.extend(future.result())


df = pd.DataFrame(all_items)

df["title"] = df.apply(lambda x: make_clickable_url(x["title"], x["link"]), axis=1)
df["repository"] = df.apply(
    lambda x: make_clickable_url(x["repo_name"], x["repo_url"]), axis=1
)

df.drop_duplicates(subset="link", keep="last", inplace=True, ignore_index=True)
df.to_csv("github_activity.csv")
