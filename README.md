# My GitHub Activity Dashboard

A Jupyter-based dashboard to help visualise activity in issues and Pull Requests across many repositories and organisations - all in one place!

Click here to view the dashboard! :point_right: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sgibson91/github-activity-dashboard/notebook-env?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Fsgibson91%252Fgithub-activity-dashboard%26urlpath%3D%252Fvoila%252Frender%252Fgithub-activity-dashboard%252Factivity-dashboard.ipynb%26branch%3Dmain)

---

**Table of Contents:**

- [How the dashboard works](#how-the-dashboard-works)
  - [Python script](#python-script)
  - [Continuous Delivery of data](#continuous-delivery-of-data)
  - [Visualising the data](#visualising-the-data)
  - [Binder and `nbgitpuller`](#binder-and-nbgitpuller)
- [Get your own dashboard!](#get-your-own-dashboard)
- [Using the tools locally](#using-the-tools-locally)
  - [Installation requirements](#installation-requirements)
  - [Getting the data](#getting-the-data)
  - [Viewing the dashboard](#viewing-the-dashboard)

## How the dashboard works

### Python script

`get-data.py` is a Python script that makes call to the [GitHub REST API](https://docs.github.com/en/rest) in order to collect information about issues and pull requests.
It specifically makes requests to the [search endpoint](https://docs.github.com/en/rest/reference/search#search-issues-and-pull-requests) which allows us search for issues and pull requests as we would expect to do so in GitHub's own search bar.
For example, `is:issue is:open assignee:sgibson91` would return all open issues assigned to me.
This turned out to be much more efficient than using the ['list issues assigned to the authenticated user' endpoint](https://docs.github.com/en/rest/reference/issues#list-issues-assigned-to-the-authenticated-user) since it made fewer individual requests and, therefore, wouldn't rate-limit the script.

The script searches for all open issues and pull requests that the user is either assigned to or has created, and also any pull requests where their review has been requested.
The results are compiled into a pandas dataframe, along with some metadata, and then written to CSV file called `github-activity.csv`.

You can provide a `.repoignore` file to prevent results from specific repos turning up the the dataset.
This is a plain text file with a repository to be ignored on each new line.
The repository to be ignored is represented by the form `ORG_OR_USER/REPO_NAME`.

### Continuous Delivery of data

The `get-data.py` script is run in a GitHub Actions workflow on a regular cron trigger.
This cron job runs as if running the script locally and commits the updated CSV file to the `main` branch.

### Visualising the data

The data are visualised using the `activity-dashboard.ipynb` Jupyter Notebook.
It implements widgets to interact with the data so that users can filter by an individual repository and sort by time created or updated.
The Notebook is executed with `voila` in order to give the dashboard a more aesthetically pleasing look.

### Binder and `nbgitpuller`

The dashboard can be launched in Binder to generate a quick view with needing to use the repository locally.
Binder usually rebuilds the Docker image of the repository with every new commit it sees on the provided git reference.
However since the CSV file is regularly updated, this meant Binder was rebuilding _a lot_ when it didn't need to since only the data were changing - not the Notebook or the environment required by the Notebook.

To mitigate the number of rebuilds Binder would need to make, the `requirements.txt` rcontaining _only_ the packages needed to run the Notebook have been separated out onto the `notebook-env` branch.
This is the branch we build with Binder.
We then use [`nbgitpuller`](https://jupyterhub.github.io/nbgitpuller/) to dynamically pull in the content from the `main` branch.
This results in a Binder environment that is only rebuilt when the Notebook requirements are changed, but still operates with the most up-to-date data from the `main` branch.

**Binder needs BOTH the `main` branch and the `notebook-env` branch to operate in this way!**
**If you are using this project as a template or forking it, DO NOT remove the `notebook-env` branch without ALSO updating the Binder link!**

## Get your own dashboard!

1. [Create your own version of this repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) by clicking the "Use this template" button at the top of this page
2. Delete the `github-activity.csv` file from your repo.
   (It will be regenerated when the CI job next runs!)
3. Delete the `.repoignore` file or edit it contain a list of repos you'd like excluded from the dataset, in the form `ORG_OR_USER/REPO_NAME`.
4. [Create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `public_repo` scope and [add it as a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository) called `ACCESS_TOKEN`
5. Edit the [README](./README.md) and update the Binder badge, replacing all instances of `{{ YOUR_GITHUB_HANDLE_HERE }}` (including `{{}}`!!!) with your GitHub handle in the below snippet:

   ```markdown
   [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{{ YOUR_GITHUB_HANDLE_HERE }}/github-activity-dashboard/notebook-env?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252F{{ YOUR_GITHUB_HANDLE_HERE }}%252Fgithub-activity-dashboard%26urlpath%3D%252Fvoila%252Frender%252Fgithub-activity-dashboard%252Factivity-dashboard.ipynb%26branch%3Dmain)
   ```

   :rotating_light: Be careful not to edit anything else in the URL! :rotating_light:

You can either get started straight away by [manually triggering the 'Update GitHub Activity' workflow](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow#running-a-workflow) or wait for the cron job to run it for you to produce your `github-activity.csv`.
Once that has been added to your repo, click your edited Binder badge to see your dashboard!

## Using the tools locally

### Installation requirements

This project requires a Python installation.
Any minor patch of Python3 should suffice, but that hasn't been tested so proceed with caution!

The packages required to run this project are stored in `requirements.txt` and can be installed via `pip`:

```bash
pip install -r requirements.txt
```

### Getting the data

1. If you have not already done so, [create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with the `public_repo` scope
2. Add this as a variable called `ACCESS_TOKEN` to your shell environment

   ```bash
   export ACCESS_TOKEN="PASTE YOUR TOKEN HERE"
   ```

3. Run the Python script to generate the `github-activity.csv` file

   ```bash
   python get-data.py
   ```

:rotating_light: If you see the message "You are rate limited! :scream:", you will need to wait ~1hour before trying to run the script again :rotating_light:

### Viewing the dashboard

Once `github-activity.csv` has been generated, view the dashboard by running:

```bash
voila activity-dashboard.ipynb
```

A browser window should be automatically opened.
