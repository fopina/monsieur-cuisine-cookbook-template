# Monsieur Cuisine cookbook

A version-controlled recipe collection in Markdown. Recipes are readable here on GitHub; the Monsieur Cuisine GitHub Action validates them and creates JSON payloads for `monsieur-cuisine-cli`.

## Add a recipe

Create a Markdown file under `recipes/`. Use the first-level heading as its title, put the description immediately below it, then add the details photo as the next image. The action uploads that photo as the details image and creates an 800×600 thumbnail from a top-left 4:3 crop. When the source is smaller, it uses the largest 4:3 crop available without enlarging it. Store other recipe metadata in a Markdown table under `## Recipe`, followed by `## Ingredients` and `## Steps`. See [Tomato soup](recipes/tomato-soup.md) and the [action format guide](https://github.com/fopina/monsieur-cuisine-cli/tree/github-action-cookbook/action#recipe-format).

Every push and pull request validates the recipes and uploads the converted JSON as a workflow artifact. Generated payloads use the API’s `status: private-publish` for private recipes. Review them before using the CLI to create recipes in your account.

## Publish recipes

The **Publish recipes** workflow is manual and opt-in. Configure the repository Actions secret `MC_API_ACCESS_TOKEN` with the `accessToken` value from a valid Monsieur Cuisine `session.json`, then run the workflow with `confirm_publish` enabled. It creates or updates every Markdown recipe with private visibility (`private-publish` in the API). For a recipe without a `recipeId`, the workflow searches the account by exact title and prefers a matching locale. One match is updated; no match creates a recipe; ambiguous matches fail and require a `recipeId` link. Existing `recipeId` values are updated directly. A failed private publish is retried as a draft and fails the workflow with an error explaining the outcome. A draft fallback is only created through the workflow; recipe status is not controlled in Markdown. After a successful create or title match, the workflow opens a PR that adds or updates the `recipeId` row as a clickable Monsieur Cuisine recipe link. Merge that PR to make future runs update by ID. The details photo is the image immediately after the description; the action generates and uploads its thumbnail automatically.
