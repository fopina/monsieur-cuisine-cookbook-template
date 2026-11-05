# Monsieur Cuisine cookbook template

Use this repository as a starter for a private, version-controlled Monsieur Cuisine cookbook. Recipes live as Markdown files; the [CLI GitHub Action](https://github.com/fopina/monsieur-cuisine-cli/tree/main/action) validates them and manages their account recipes.

## Start your cookbook

1. Select **Use this template** on GitHub and create a repository in your account.
2. Configure the repository secrets below.
3. Add recipe files under `recipes/` and open a pull request.

## Configure Actions secrets

### `MC_API_ACCESS_TOKEN`

Log in with a dedicated session for this cookbook, then pipe its token directly to the repository secret:

```sh
uvx monsieur-cuisine-cli --session-file github-cookbook-session.json auth login
uvx monsieur-cuisine-cli --session-file github-cookbook-session.json auth get-token | gh secret set MC_API_ACCESS_TOKEN --repo OWNER/REPOSITORY
```

`uvx` runs the published CLI from PyPI. Replace `OWNER/REPOSITORY` with your cookbook repository; `gh` must be authenticated and able to update its Actions secrets. Keep this session dedicated to GitHub Actions: the API rotates tokens, and the workflow saves a rotated value back to `MC_API_ACCESS_TOKEN` after use. For CLI token transfer details, see [CLI sign-in and token transfer](https://github.com/fopina/monsieur-cuisine-cli/blob/main/README-CLI.md#transfer-an-api-token).

### `GH_SECRETS_WRITE_TOKEN`

Add a fine-grained personal access token restricted to this repository, with **Secrets: Read and write** permission. The Action uses it to persist token rotations. GitHub’s [fine-grained token guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) explains how to create one.

The **Get recipe** workflow opens a pull request when run on `main`; enable **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**. The Action guide has the exact [workflow permissions and setup](https://github.com/fopina/monsieur-cuisine-cli/blob/main/action/README.md#use-in-a-cookbook-repository).

## Add recipes

Create a Markdown file under `recipes/` and open a pull request. The CLI Action guide is the canonical reference for the [recipe format, accepted fields, and validation rules](https://github.com/fopina/monsieur-cuisine-cli/blob/main/action/README.md#recipe-format); this README intentionally keeps the schema there instead of duplicating it.

The demos are separate recipes in different locales: [Tomato soup (`en-US`)](recipes/tomato-soup.md) and [Sopa cremosa de tomate (`pt-PT`)](recipes/sopa-de-tomate.md). There is no “master” locale that contains all recipes in every language. Create a separate file for each language, with its own localized content, locale-specific dropdown values, and account recipe ID.

## Fetch a recipe

Run **Get recipe** from the Actions tab and enter a Monsieur Cuisine URL or numeric recipe ID. It creates a Markdown file and a pull request on `main`. The workflow also converts the Markdown back to JSON, compares it with the fetched recipe, and attaches the JSON artifacts to the run. See the Action guide for [operation details](https://github.com/fopina/monsieur-cuisine-cli/blob/main/action/README.md#use-in-a-cookbook-repository).

Recipes created by this workflow are private. To make one public, change its visibility separately in Monsieur Cuisine; merging a cookbook pull request does not make it public.
