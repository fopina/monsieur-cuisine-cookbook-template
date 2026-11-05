#!/usr/bin/env python3
"""Replace an existing cookbook recipe with the authenticated CLI export."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


def recipe_id_in_markdown(path: Path) -> str | None:
    for line in path.read_text(encoding='utf-8').splitlines():
        # Keep the empty cells from the outer table delimiters. Stripping `|`
        # first leaves only two cells in a normal `| key | value |` row.
        cells = line.strip().split('|')
        if len(cells) < 4 or cells[1].strip() != 'recipeId':
            continue
        value = '|'.join(cells[2:-1])
        ids = set(re.findall(r'(?<!\d)[1-9][0-9]*(?!\d)', value))
        return next(iter(ids)) if len(ids) == 1 else None
    return None


def details_image(markdown: str) -> tuple[int, int, str] | None:
    for match in re.finditer(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', markdown, flags=re.MULTILINE):
        if match.group(1).strip().lower() == 'details image':
            return match.start(), match.end(), match.group(2)
    return None


def canonicalize_serving_unit(markdown: str) -> str:
    locale = re.search(r'^\|\s*languageLocale\s*\|\s*([^|]+)\|\s*$', markdown, flags=re.MULTILINE)
    if not locale or locale.group(1).strip() != 'pt-PT':
        return markdown

    # The portal calls this unit “doses”, while the cookbook schema's pt-PT
    # serving-size option is “porções”. Preserve the API amount and canonicalize
    # only that known label so the refreshed recipe remains valid cookbook data.
    return re.sub(
        r'^(\|\s*servings\s*\|\s*\d+\s*)\(\s*doses\s*\)(\s*\|\s*)$',
        r'\1(porções)\2',
        markdown,
        flags=re.MULTILINE | re.IGNORECASE,
    )


def main() -> None:
    repo = Path.cwd().resolve()
    recipe_id = os.environ.get('RECIPE_ID', '').strip()
    if not re.fullmatch(r'[1-9][0-9]*', recipe_id):
        raise SystemExit('RECIPE_ID must be a positive numeric ID.')

    generated = Path(os.environ['GENERATED_MARKDOWN']).resolve()
    recipe_root = (repo / 'recipes').resolve()
    if not generated.is_file():
        raise SystemExit(f'Generated Markdown file does not exist: {generated}')

    candidates = [path for path in recipe_root.rglob('*.md') if recipe_id_in_markdown(path) == recipe_id]
    if len(candidates) != 1:
        raise SystemExit(
            f'Expected exactly one existing cookbook recipe with recipeId {recipe_id}; found {len(candidates)}.'
        )
    target = candidates[0]

    refreshed = generated.read_text(encoding='utf-8')
    if recipe_id_in_markdown(generated) != recipe_id:
        raise SystemExit(
            f'The fetched recipe is not owned by this account or does not contain recipeId {recipe_id}; '
            'refusing to replace the existing cookbook entry.'
        )
    refreshed = canonicalize_serving_unit(refreshed)

    generated_image = os.environ.get('GENERATED_IMAGE', '').strip()
    image_output = ''
    new_image_match = details_image(refreshed)
    old_image_match = details_image(target.read_text(encoding='utf-8'))
    if new_image_match and not generated_image:
        raise SystemExit('The generated Markdown references a details image, but the action reported no image file.')
    if generated_image and new_image_match:
        image_source = Path(generated_image).resolve()
        expected_generated_root = (repo / 'build' / 'refreshed-markdown').resolve()
        if not image_source.is_file() or not image_source.is_relative_to(expected_generated_root):
            raise SystemExit('The downloaded details image is missing or outside the generated-output directory.')

        destination: Path | None = None
        if old_image_match:
            old_ref = old_image_match[2]
            old_path = (target.parent / old_ref).resolve()
            if old_path.is_relative_to(repo) and old_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
                destination = old_path
        if destination is None:
            destination = (recipe_root / 'images' / f'{recipe_id}-details{image_source.suffix.lower()}').resolve()
        if not destination.is_relative_to(repo):
            raise SystemExit('The details image destination must remain inside the repository.')

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(image_source, destination)
        relative_image = Path(os.path.relpath(destination, start=target.parent)).as_posix()
        start, end, _ = new_image_match
        refreshed = refreshed[:start] + f'![Details image]({relative_image})' + refreshed[end:]
        image_output = destination.relative_to(repo).as_posix()
    elif old_image_match and not new_image_match:
        # Keep the existing photo reference if the API omits a details image;
        # refreshing metadata should not silently remove a hand-curated asset.
        old_line = target.read_text(encoding='utf-8').splitlines()
        existing_line = next(
            line for line in old_line if details_image(line) is not None
        )
        refreshed = refreshed.replace('## Recipe', f'{existing_line}\n\n## Recipe', 1)
        old_path = (target.parent / old_image_match[2]).resolve()
        if old_path.is_relative_to(repo) and old_path.is_file():
            image_output = old_path.relative_to(repo).as_posix()

    target.write_text(refreshed.rstrip() + '\n', encoding='utf-8')
    output = Path(os.environ['GITHUB_OUTPUT'])
    with output.open('a', encoding='utf-8') as stream:
        stream.write(f'recipe-file={target.relative_to(repo).as_posix()}\n')
        stream.write(f'image-file={image_output}\n')
    print(f'Refreshed {target.relative_to(repo)} from recipe {recipe_id}.')


if __name__ == '__main__':
    main()
