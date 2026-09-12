import re


def slugify(text, existing_slugs) -> str:
    """generate unique slugs for teams and players"""

    base = text.lower().strip()
    base = re.sub(r"[^a-z0-9\s-]", "", base)
    base = re.sub(r"\s+", "-", base)
    slug = base
    counter = 2
    while slug in existing_slugs:
        slug = f"{base}-{counter}"
        counter += 1
    existing_slugs.add(slug)
    return slug
