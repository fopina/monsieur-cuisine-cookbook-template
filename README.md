# Monsieur Cuisine cookbook

A version-controlled recipe collection in Markdown. Recipes are readable here on GitHub; the Monsieur Cuisine GitHub Action validates them and creates JSON payloads for `monsieur-cuisine-cli`.

## Add a recipe

Create a Markdown file under `recipes/`. Use the first-level heading as its title, put the description immediately below it, then add the details photo as the next image. The action uploads that photo as the details image and creates an 800×600 thumbnail from a top-left 4:3 crop. When the source is smaller, it uses the largest 4:3 crop available without enlarging it. Store other recipe metadata in a Markdown table under `## Recipe`, followed by `## Ingredients` and `## Steps`. See [Tomato soup](recipes/tomato-soup.md) and the [action format guide](https://github.com/fopina/monsieur-cuisine-cli/tree/github-action-cookbook/action#recipe-format).

Every push and pull request validates the recipes and uploads the converted JSON as a workflow artifact. Generated payloads are drafts. Review them before using the CLI to create recipes in your account.

## Publish recipe drafts

The **Publish recipe drafts** workflow is manual and opt-in. Configure the repository Actions secret `MC_API_ACCESS_TOKEN` with the `accessToken` value from a valid Monsieur Cuisine `session.json`, then run the workflow with `confirm_publish` enabled. It converts every Markdown recipe and creates it as a draft when it has no `recipeId`; recipes with a `recipeId` are updated in the account. Normal pushes and pull requests only validate and generate downloadable JSON. Add the returned recipe ID to the `## Recipe` table after its first creation to make future publishes update it. The details photo is the image immediately after the description; the action generates and uploads its thumbnail automatically.
