# Monsieur Cuisine cookbook

A version-controlled recipe collection in Markdown. Recipes are readable here on GitHub; the Monsieur Cuisine GitHub Action validates them and creates JSON payloads for `monsieur-cuisine-cli`.

## Add a recipe

Create a Markdown file under `recipes/`. Use the first-level heading as its title, put the description immediately below it, then add the details photo as the next image. The action uploads that photo as the details image and creates an 800×600 thumbnail from a top-left 4:3 crop. When the source is smaller, it uses the largest 4:3 crop available without enlarging it. Store other recipe metadata in a Markdown table under `## Recipe`, followed by `## Ingredients` and `## Steps`. See [Tomato soup](recipes/tomato-soup.md) and the [action format guide](https://github.com/fopina/monsieur-cuisine-cli/tree/github-action-cookbook/action#recipe-format).

Every push and pull request validates the recipes and uploads the converted JSON as a workflow artifact. Generated payloads use the API’s `status: private-publish` for private recipes. Review them before using the CLI to create recipes in your account.

## Fetch a recipe

Run the **Get recipe** workflow from the Actions tab and enter a Monsieur Cuisine recipe URL or numeric recipe ID. It fetches the recipe with the CLI and writes it as a Markdown file. When run on `main`, it opens a pull request; when run on another branch, it commits the new file directly to that branch. The workflow uses the `MC_API_ACCESS_TOKEN` repository secret described below.

## Recipe pull requests and publishing

Every recipe PR is validated. For PRs opened from a branch in this repository, **Prepare recipe drafts** creates a Monsieur Cuisine draft for each new recipe and commits its `recipeId` link to that same PR. Existing recipes with an ID are left untouched until merge. PRs from forks are validated but skip draft creation because their workflows do not receive write credentials.

When the recipe PR is merged, **Publish recipes** updates the recipe by ID to private-published status. This keeps publication behind the merge and avoids a second PR just to record the recipe ID. If a PR is abandoned after draft creation, its draft may remain in the Monsieur Cuisine account. Configure the repository Actions secrets described below before using either workflow. For a manual run on `main`, enable `confirm_publish` to publish every Markdown recipe under `recipes/` (each must have a `recipeId`).

### Use a dedicated Monsieur Cuisine API token

Each Monsieur Cuisine login creates an independent API access token. Refreshing a token rotates that token, so the cookbook workflow must have its own token. Do not copy a token from the session you use with the CLI elsewhere: a CLI refresh can invalidate the token saved in GitHub before the workflow has a chance to store its replacement.

Create a separate login session file for the cookbook workflow:

```sh
monsieur-cuisine-cli --session-file github-cookbook-session.json auth login
```

By default, this saves `github-cookbook-session.json` beside the CLI config file (normally `~/.config/monsieur-cuisine/`). Copy the `accessToken` value from that session file into the cookbook repository's `MC_API_ACCESS_TOKEN` Actions secret. Keep this session dedicated to GitHub Actions; do not use it for routine CLI work or manually renew it. The workflow refreshes the token and writes the rotated value back to `MC_API_ACCESS_TOKEN` after each run.

### GitHub Actions permissions

The draft workflow grants the built-in `GITHUB_TOKEN` `Contents: write` so it can commit the recipe ID to the existing same-repository PR branch. It does not open a new PR. The separate **Get recipe** workflow does open a PR when run on `main`, so the repository setting **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests** must remain enabled for that workflow.

### Secret-writing token

The workflow also needs a token with permission to update the rotated `MC_API_ACCESS_TOKEN` repository secret. It uses `GH_SECRETS_WRITE_TOKEN` for this operation.

Create a [fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for `GH_SECRETS_WRITE_TOKEN`:

1. Open [GitHub’s fine-grained token creation page](https://github.com/settings/personal-access-tokens/new) (or navigate through **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**).
2. Select the account that owns the cookbook storage repository as **Resource owner**.
3. Under **Repository access**, choose **Only select repositories**, then select the cookbook repository used to store the Markdown recipes.
4. Under **Repository permissions**, set **Secrets** to **Read and write**.
5. Choose an expiration that fits your maintenance schedule, generate the token, and copy it.
6. In that cookbook repository, open **Settings → Secrets and variables → Actions → New repository secret** and save it as `GH_SECRETS_WRITE_TOKEN`.

GitHub's [Actions secrets API documentation](https://docs.github.com/en/rest/actions/secrets#fine-grained-access-tokens-for-create-or-update-a-repository-secret) specifies the repository `Secrets: write` permission for updating a repository secret. Restrict the PAT to the single cookbook repository.

On a recipe PR, the workflow creates a draft only if the Markdown has no `recipeId` and no matching account recipe exists; it then writes a clickable recipe link into the existing PR. After merge, the publish workflow updates that ID to private-publish. If private publishing fails, the action falls back to a draft and fails the workflow with an error explaining the outcome. Recipe status is managed by the action, not Markdown. The details photo is the image immediately after the description; the action generates and uploads its thumbnail automatically.
