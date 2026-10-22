#!/usr/bin/env python3
"""Write a fetched Monsieur Cuisine recipe as a cookbook Markdown file."""

import json
import os
import re
import unicodedata
from pathlib import Path


def markdown(value: object) -> str:
    if value is None:
        return ''
    return str(value).replace('|', r'\|').replace('\r\n', '<br>').replace('\n', '<br>').strip()


def ids(value: object) -> str:
    if not isinstance(value, list):
        return ''
    return ', '.join(str(item.get('id') if isinstance(item, dict) else item) for item in value if item)


def main() -> None:
    response = json.loads(Path(os.environ['RECIPE_JSON']).read_text(encoding='utf-8'))
    recipe = response.get('recipe', response) if isinstance(response, dict) else None
    if not isinstance(recipe, dict):
        raise SystemExit('The CLI response did not contain a recipe object.')

    title = str(recipe.get('title') or '').strip()
    locale = str(recipe.get('languageLocale') or response.get('viewerLang') or '').strip()
    recipe_id = response.get('recipeId') or recipe.get('id')
    devices = ids(recipe.get('deviceTypeIds') or recipe.get('deviceTypes'))
    serving_sizes = recipe.get('servingSizes')
    if not title or not locale or not devices or not isinstance(serving_sizes, list) or not serving_sizes:
        raise SystemExit('The recipe is missing a title, locale, device type, or serving size.')

    serving = next((item for item in serving_sizes if isinstance(item, dict) and item.get('isDefault')), None)
    if serving is None:
        serving = next((item for item in serving_sizes if isinstance(item, dict)), None)
    unit = serving.get('unit') if serving else None
    if isinstance(unit, dict):
        unit = unit.get('name') or unit.get('unit')
    if serving is None or not unit or serving.get('amount') is None:
        raise SystemExit('The recipe has no usable serving size.')

    metadata = [
        ('languageLocale', locale),
        ('deviceTypeIds', devices),
        ('servings', f"{serving['amount']} ({unit})"),
    ]
    # Numeric IDs refer to the user's own recipes; retain them for later updates.
    if re.fullmatch(r'[1-9][0-9]*', os.environ.get('INPUT_RECIPE', '').strip()):
        metadata.append(('recipeId', os.environ['INPUT_RECIPE'].strip()))
    for field in ('preparationTime', 'readyInTime'):
        value = serving.get(field, recipe.get(field))
        if value is not None:
            metadata.append((field, value))

    groups = serving.get('ingredientGroups') or []
    if groups and isinstance(groups[0], dict) and groups[0].get('name'):
        metadata.append(('ingredientGroupName', groups[0]['name']))
    categories = ids(recipe.get('categories') or recipe.get('categoryIds'))
    if categories:
        metadata.append(('categoryIds', categories))
    complexity = recipe.get('complexity')
    if isinstance(complexity, dict) and complexity.get('id'):
        metadata.append(('complexityId', complexity['id']))
    if recipe.get('hintsAndTips'):
        metadata.append(('hintsAndTips', recipe['hintsAndTips']))

    lines = [f'# {title}', '', markdown(recipe.get('description')), '', '## Recipe', '', '| Field | Value |', '| --- | --- |']
    lines.extend(f'| {markdown(key)} | {markdown(value)} |' for key, value in metadata)
    lines.extend(['', '## Ingredients', ''])
    ingredient_count = 0
    for group in groups:
        if not isinstance(group, dict):
            continue
        for ingredient in group.get('ingredients') or []:
            if not isinstance(ingredient, dict) or not ingredient.get('name'):
                continue
            details = {
                'amount': str(ingredient.get('amount') if ingredient.get('amount') is not None else ''),
                'unit': ingredient.get('unit') or '',
                'isOptional': bool(ingredient.get('isOptional', False)),
            }
            annotation = json.dumps(details, ensure_ascii=False, separators=(',', ':'))
            lines.append(f"- {markdown(ingredient['name'])} <!-- mc-ingredient: {annotation} -->")
            ingredient_count += 1
    if not ingredient_count:
        raise SystemExit('The recipe has no ingredients to write to Markdown.')

    steps = [step for step in (serving.get('steps') or []) if isinstance(step, dict)]
    if not steps:
        raise SystemExit('The recipe has no steps to write to Markdown.')
    lines.extend(['', '## Steps', ''])
    for index, step in enumerate(steps, 1):
        step_title = markdown(step.get('title') or title)
        description = markdown(step.get('description'))
        line = f'{index}. **{step_title}**: {description}'
        if isinstance(step.get('mode'), dict):
            mode = json.dumps(step['mode'], ensure_ascii=False, separators=(',', ':'))
            line += f' <!-- mc-mode: {mode} -->'
        lines.append(line)

    nutrients = recipe.get('nutrients') or []
    if nutrients:
        lines.extend(['', '## Nutrition', '', '| Nutrient | Amount | Unit |', '| --- | --- | --- |'])
        for nutrient in nutrients:
            if isinstance(nutrient, dict):
                amount = nutrient.get('amount', nutrient.get('amountFloat', ''))
                lines.append(
                    f"| {markdown(nutrient.get('name'))} | {markdown(amount)} | {markdown(nutrient.get('unit'))} |"
                )

    slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode().lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-') or 'recipe'
    recipe_path = Path('recipes') / f'{slug}-{recipe_id or slug}.md'
    if recipe_path.exists():
        raise SystemExit(f'{recipe_path} already exists; refusing to overwrite it.')
    recipe_path.parent.mkdir(parents=True, exist_ok=True)
    recipe_path.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
        output.write(f'recipe-file={recipe_path.as_posix()}\n')
    print(f'Created {recipe_path}')


if __name__ == '__main__':
    main()
