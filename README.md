# My GitHub Activity Dashboard

A Jupyter-based dashboard to help visualise activity in issues and Pull Requests across many repositories and organisations.

Click here to view the dashboard! :point_right: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sgibson91/github-activity-dashboard/notebook-env?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Fsgibson91%252Fgithub-activity-dashboard%26urlpath%3D%252Fvoila%252Frender%252Fgithub-activity-dashboard%252Fvisualise.ipynb%26branch%3Dmain)

---

## Get your own dashboard!

1. [Create your own version of this repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) by clicking the "Use this template" button at the top of this page
2. Delete the `github-activity.csv` file from your repo.
   (It will be regenerated when the CI job next runs!)
3. [Create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `public_repo` scope and [add it as a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository) called `ACCESS_TOKEN`
4. Edit the [README](./README.md) and update the Binder badge, replacing all instances of `{{ YOUR_GITHUB_HANDLE_HERE }}` (including `{{}}`!!!) with your GitHub handle in the below snippet:

   ```markdown
   [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{{ YOUR_GITHUB_HANDLE_HERE }}/github-activity-dashboard/notebook-env?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252F{{ YOUR_GITHUB_HANDLE_HERE }}%252Fgithub-activity-dashboard%26urlpath%3D%252Fvoila%252Frender%252Fgithub-activity-dashboard%252Fvisualise.ipynb%26branch%3Dmain)
   ```

   :rotating_light: Be careful not to edit anything else in the URL! :rotating_light:

You can either get started straight away by [manually triggering the Update GitHub Activity workflow](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow#running-a-workflow) or wait for the cron job to run it for you to produce your `github-activity.csv`.
Once that has been added to your repo, click your edited Binder badge to see your dashboard!

## Using the tools locally

### Installation Requirements

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
voila visualise.ipynb
```

A browser window should be automatically opened.
