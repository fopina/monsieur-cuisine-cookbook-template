# Monsieur Cuisine cookbook

A version-controlled recipe collection in Markdown. Recipes are readable here on GitHub; the Monsieur Cuisine GitHub Action validates them and creates JSON payloads for `monsieur-cuisine-cli`.

## Add a recipe

Create a Markdown file under `recipes/`. Use the first-level heading as its title, put the description immediately below it, then add the details photo as the next image. The action uploads that photo as the details image and creates an 800×600 thumbnail from a top-left 4:3 crop. When the source is smaller, it uses the largest 4:3 crop available without enlarging it. Store other recipe metadata in a Markdown table under `## Recipe`, followed by `## Ingredients` and `## Steps`. See [Tomato soup](recipes/tomato-soup.md) and the [action format guide](https://github.com/fopina/monsieur-cuisine-cli/tree/github-action-cookbook/action#recipe-format).

Every push and pull request validates the recipes and uploads the converted JSON as a workflow artifact. Generated payloads use the API’s `status: private-publish` for private recipes. Review them before using the CLI to create recipes in your account.

## Publish recipes

The **Publish recipes** workflow is manual and opt-in. Configure the repository Actions secrets described below, then run the workflow with `confirm_publish` enabled.

### Use a dedicated Monsieur Cuisine API token

Each Monsieur Cuisine login creates an independent API access token. Refreshing a token rotates that token, so the cookbook workflow must have its own token. Do not copy a token from the session you use with the CLI elsewhere: a CLI refresh can invalidate the token saved in GitHub before the workflow has a chance to store its replacement.

Create a separate login session file for the cookbook workflow:

```sh
monsieur-cuisine-cli --session-file github-cookbook-session.json auth login
```

By default, this saves `github-cookbook-session.json` beside the CLI config file (normally `~/.config/monsieur-cuisine/`). Copy the `accessToken` value from that session file into the cookbook repository's `MC_API_ACCESS_TOKEN` Actions secret. Keep this session dedicated to GitHub Actions; do not use it for routine CLI work or manually renew it. The workflow refreshes the token and writes the rotated value back to `MC_API_ACCESS_TOKEN` after each run.

### Configure GitHub tokens

The workflow uses two separate tokens for GitHub operations:

- `GH_SECRETS_WRITE_TOKEN` updates the rotated `MC_API_ACCESS_TOKEN` repository secret.
- `GH_PULL_REQUESTS_TOKEN` opens the `recipeId` pull request. The workflow's `GITHUB_TOKEN` pushes its branch (using the workflow's `Contents: write` permission), but this repository does not allow that token to create pull requests.

Create a [fine-grained personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for each token:

1. Open [GitHub’s fine-grained token creation page](https://github.com/settings/personal-access-tokens/new) (or navigate through **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**).
2. Select the account that owns the cookbook storage repository as **Resource owner**.
3. Under **Repository access**, choose **Only select repositories**, then select the cookbook repository used to store the Markdown recipes.
4. For `GH_SECRETS_WRITE_TOKEN`, set **Secrets** to **Read and write**. For `GH_PULL_REQUESTS_TOKEN`, set **Contents** and **Pull requests** to **Read and write**.
5. Choose an expiration that fits your maintenance schedule, generate each token, and copy it.
6. In that cookbook repository, open **Settings → Secrets and variables → Actions → New repository secret** and save each token under its corresponding name.

GitHub's [Actions secrets API documentation](https://docs.github.com/en/rest/actions/secrets#fine-grained-access-tokens-for-create-or-update-a-repository-secret) specifies the repository `Secrets: write` permission for updating a repository secret. The action documents `Contents: write` and `Pull requests: write` for its `github_token` input, which is used to open the `recipeId` pull request. Restrict both tokens to the single cookbook repository.

The workflow creates or updates every Markdown recipe with private visibility (`private-publish` in the API). For a recipe without a `recipeId`, it searches the account by exact title and prefers a matching locale. One match is updated; no match creates a recipe; ambiguous matches fail and require a `recipeId` link. Existing `recipeId` values are updated directly. A failed private publish is retried as a draft and fails the workflow with an error explaining the outcome. A draft fallback is only created through the workflow; recipe status is not controlled in Markdown. After a successful create or title match, the workflow opens a PR that adds or updates the `recipeId` row as a clickable Monsieur Cuisine recipe link. Merge that PR to make future runs update by ID. The details photo is the image immediately after the description; the action generates and uploads its thumbnail automatically.
