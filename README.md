# Monsieur Cuisine cookbook

A version-controlled recipe collection in Markdown. Recipes are readable here on GitHub; the Monsieur Cuisine GitHub Action validates them and creates JSON payloads for `monsieur-cuisine-cli`.

## Add a recipe

Create a Markdown file under `recipes/` with TOML metadata between `+++` lines, then add `## Ingredients` and `## Steps` sections. See [Tomato soup](recipes/tomato-soup.md) and the [action format guide](https://github.com/fopina/monsieur-cuisine-cli/tree/github-action-cookbook/action#recipe-format).

Every push and pull request validates the recipes and uploads the converted JSON as a workflow artifact. Generated payloads are drafts. Review them before using the CLI to create recipes in your account.
