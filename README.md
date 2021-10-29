# My GitHub Activity Dashboard

A Jupyter-based dashbaord to help visualise activity in issues and Pull Requests across many repositories and organisations.

Click here to view the dashboard! :point_right: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sgibson91/github-activity/HEAD?urlpath=voila%2Frender%2Fvisualise.ipynb)

---

## Get your own dashboard!

1. [Create your own version of this repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) by clicking the "Use this template" button at the top of this page
2. Delete the `github-activity.csv` file from your repo.
   (It will be regenerated when the CI job next runs!)

    ```bash
    git rm github-activity.csv
    git add .
    git commit -m "Remove old github-activity.csv"
    git push
    ```

3. [Create a Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `public_repo` scope and [add it as a repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository) called `ACCESS_TOKEN`
4. Edit the [README](./README.md) and update the Binder badge to the following, inserting your GitHub handle where appropriate:

   ```markdown
   [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{{ YOUR GITHUB HANDLE HERE }}/github-activity/HEAD?urlpath=voila%2Frender%2Fvisualise.ipynb)
   ```

You can either get started straight away by [manually triggering the Update GitHub Activity workflow](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow#running-a-workflow) or wait for the cron job to run it for you to produce your `github-activity.csv`.
Once that has been added to your repo, click your edited Binder badge to see your dashboard!

## Using the tools locally

### Installation Requuirements

This project requires a Python installation.
Any minor patch of Python3 should suffice, but that hasn't been tested so proceed with caution!

The packages required to run `get-data.py` are stored in `dev-requirements.txt` and can be installed via `pip`:

```bash
pip install -r dev-requirements.txt
```

The packages required to view the dashboard are listed in `requirements.txt` and can also be installed with `pip`:

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
