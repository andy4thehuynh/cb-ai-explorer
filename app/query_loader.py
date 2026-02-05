import json

_REQUIRED_FIELDS = (
    "id", "name", "description", "category",
    "before_query", "after_query", "ai_fields", "display_hint",
)


def load_queries(path: str = "data/queries.json") -> list[dict]:
    """Load and validate queries from a JSON file.

    Raises ValueError if any entry is missing a required field or has a duplicate id.
    Raises FileNotFoundError if the path does not exist.
    """
    with open(path) as f:
        queries = json.load(f)

    seen_ids: set[str] = set()
    for query in queries:
        for field in _REQUIRED_FIELDS:
            if field not in query:
                raise ValueError(
                    f"Query {query.get('id', '(unknown)')} missing required field: {field}"
                )
        qid = query["id"]
        if qid in seen_ids:
            raise ValueError(f"Queries contain duplicate id: {qid}")
        seen_ids.add(qid)

    return queries


def get_queries_by_category(queries: list[dict]) -> dict[str, list[dict]]:
    """Group queries by their category field."""
    grouped: dict[str, list[dict]] = {}
    for query in queries:
        grouped.setdefault(query["category"], []).append(query)
    return grouped


def get_query_by_id(queries: list[dict], query_id: str) -> dict | None:
    """Return the query with the given id, or None if not found."""
    for query in queries:
        if query["id"] == query_id:
            return query
    return None
