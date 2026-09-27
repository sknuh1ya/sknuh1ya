
def find_duplicates(documents: list[dict]) -> set[str]:
    seen = {}
    duplicates = set()

    for document in documents:
        key = document.get("duplicate_key")

        if not key:
            continue

        if key in seen:
            duplicates.add(key)
        else:
            seen[key] = document["file_name"]

    result = set()

    for key in duplicates:
        for document in documents:
            if document.get("duplicate_key") == key:
                result.add(document["file_name"])

    return result
