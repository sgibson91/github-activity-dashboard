import os

import pandas as pd
from ghapi.core import GhApi
from ghapi.page import paged

token = os.environ["ACCESS_TOKEN"] if "ACCESS_TOKEN" in os.environ else None

if token is None:
    raise ValueError("ACCESS_TOKEN must be set!")

gh = GhApi(token=token)

result = gh.users.get_authenticated()
username = result["login"]

all_items = []
filters = ["assigned", "created"]

for filter_type in filters:
    result = paged(
        gh.issues.list,
        filter=filter_type,
        state="open",
        sort="updated",
        direction="desc",
        per_page=100,
    )

    for page in result:
        for item in page:
            details = {
                "number": item["number"],
                "title": item["title"],
                "link": item["pull_request"]["html_url"]
                if "pull_request" in item.keys()
                else item["html_url"],
                "repository": item["repository"]["html_url"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "pull_request": "pull_request" in item.keys(),
                "filter": filter_type,
            }

            if "pull_request" in item.keys():
                pr_result = gh.pulls.list_requested_reviewers(
                    item["repository"]["owner"]["login"],
                    item["repository"]["name"],
                    item["number"],
                )
                reviewers = [user["login"] for user in pr_result["users"]]

                if username in reviewers:
                    details["filter"] = "review_requested"

            all_items.append(details)

df = pd.DataFrame(all_items)
df.drop_duplicates(subset="link", keep="last", inplace=True, ignore_index=True)
df.to_csv("github_activity.csv")
