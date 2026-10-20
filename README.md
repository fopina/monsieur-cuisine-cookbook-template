# Monsieur Cuisine cookbook

A version-controlled recipe collection in Markdown. Recipes are readable here on GitHub; the Monsieur Cuisine GitHub Action validates them and creates JSON payloads for `monsieur-cuisine-cli`.

## Add a recipe

Create a Markdown file under `recipes/` with TOML metadata between `+++` lines, then add `## Ingredients` and `## Steps` sections. See [Tomato soup](recipes/tomato-soup.md) and the [action format guide](https://github.com/fopina/monsieur-cuisine-cli/tree/github-action-cookbook/action#recipe-format).

Every push and pull request validates the recipes and uploads the converted JSON as a workflow artifact. Generated payloads are drafts. Review them before using the CLI to create recipes in your account.


## Publish recipe drafts

The **Publish recipe drafts** workflow is manual and opt-in. Configure the repository Actions secret `MC_API_ACCESS_TOKEN` with the `accessToken` value from a valid Monsieur Cuisine `session.json`, then run the workflow with `confirm_publish` enabled. It converts every Markdown recipe and creates it as a draft in the account. Normal pushes and pull requests only validate and generate downloadable JSON. Re-running publish creates additional drafts; it does not update existing recipes.
