import re

# import unidecode


def slugify(text):
    # text = unidecode.unidecode(text)
    return re.sub(r"[\W_]+", "_", text.lower())


def extract_uniques(elements, comp=lambda left, right: left == right):
    keep = []
    for e in elements:
        if not any(comp(e, k) for k in keep):
            keep.append(e)
    return keep


def groupby(iterable, key):
    mapping = {}
    for el in iterable:
        k = key(el)
        siblings = mapping.setdefault(k, [])
        siblings.append(el)
    return mapping
