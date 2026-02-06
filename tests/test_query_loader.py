import json

import pytest

from app.query_loader import (
  get_queries_by_category,
  get_query_by_id,
  load_queries,
)

EXPECTED_CATEGORIES = {
  "sentiment", "summary", "classification", "extraction",
  "grammar", "generation", "masking", "similarity",
  "translation", "completion",
}

SAMPLE_QUERIES = [
  {
    "id": "sentiment-hotels",
    "name": "Hotel Review Sentiment",
    "description": "Analyze sentiment of hotel reviews",
    "category": "sentiment",
    "before_query": "SELECT r.content FROM reviews r LIMIT 5",
    "after_query": "SELECT r.content, AI_SENTIMENT(r.content) AS sentiment FROM reviews r LIMIT 5",
    "ai_fields": ["sentiment"],
    "display_hint": "table",
  },
  {
    "id": "summary-hotels",
    "name": "Hotel Description Summary",
    "description": "Summarize hotel descriptions",
    "category": "summary",
    "before_query": "SELECT h.description FROM hotels h LIMIT 5",
    "after_query": "SELECT h.description, AI_SUMMARY(h.description) AS summary FROM hotels h LIMIT 5",
    "ai_fields": ["summary"],
    "display_hint": "cards",
  },
  {
    "id": "sentiment-airlines",
    "name": "Airline Review Sentiment",
    "description": "Analyze sentiment of airline reviews",
    "category": "sentiment",
    "before_query": "SELECT r.content FROM airline_reviews r LIMIT 5",
    "after_query": "SELECT r.content, AI_SENTIMENT(r.content) AS sentiment FROM airline_reviews r LIMIT 5",
    "ai_fields": ["sentiment"],
    "display_hint": "table",
  },
]


@pytest.fixture
def sample_json(tmp_path):
  """Write sample queries to a temp JSON file and return its path."""
  path = tmp_path / "queries.json"
  path.write_text(json.dumps(SAMPLE_QUERIES))
  return str(path)


class TestLoadQueries:
  def test_returns_list_of_dicts(self, sample_json):
    queries = load_queries(sample_json)
    assert isinstance(queries, list)
    assert len(queries) == 3
    assert all(isinstance(q, dict) for q in queries)

  def test_each_query_has_required_fields(self, sample_json):
    required_fields = {
      "id", "name", "description", "category",
      "before_query", "after_query", "ai_fields", "display_hint",
    }
    queries = load_queries(sample_json)
    for query in queries:
      assert required_fields.issubset(query.keys())

  def test_raises_on_missing_required_field(self, tmp_path):
    incomplete = [{"id": "test", "name": "Test Query"}]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(incomplete))

    with pytest.raises(ValueError, match="missing required field"):
      load_queries(str(path))

  def test_raises_on_duplicate_ids(self, tmp_path):
    dupes = [SAMPLE_QUERIES[0], SAMPLE_QUERIES[0]]
    path = tmp_path / "dupes.json"
    path.write_text(json.dumps(dupes))

    with pytest.raises(ValueError, match="duplicate.*id"):
      load_queries(str(path))

  def test_raises_on_file_not_found(self):
    with pytest.raises(FileNotFoundError):
      load_queries("/nonexistent/queries.json")


class TestGetQueriesByCategory:
  def test_groups_by_category(self, sample_json):
    queries = load_queries(sample_json)
    grouped = get_queries_by_category(queries)

    assert isinstance(grouped, dict)
    assert set(grouped.keys()) == {"sentiment", "summary"}
    assert len(grouped["sentiment"]) == 2
    assert len(grouped["summary"]) == 1

  def test_preserves_query_data(self, sample_json):
    queries = load_queries(sample_json)
    grouped = get_queries_by_category(queries)

    sentiment_ids = {q["id"] for q in grouped["sentiment"]}
    assert sentiment_ids == {"sentiment-hotels", "sentiment-airlines"}


class TestFullQueryCatalog:
  def test_contains_exactly_12_entries(self):
    queries = load_queries()
    assert len(queries) == 12

  def test_all_10_ai_function_categories_represented(self):
    queries = load_queries()
    categories = {q["category"] for q in queries}
    assert categories == EXPECTED_CATEGORIES

  def test_all_required_fields_present(self):
    required_fields = {
      "id", "name", "description", "category",
      "before_query", "after_query", "ai_fields", "display_hint",
    }
    queries = load_queries()
    for query in queries:
      missing = required_fields - query.keys()
      assert not missing, f"Query {query.get('id', '?')} missing: {missing}"

  def test_no_duplicate_ids(self):
    queries = load_queries()
    ids = [q["id"] for q in queries]
    assert len(ids) == len(set(ids)), f"Duplicate ids: {[i for i in ids if ids.count(i) > 1]}"

  def test_each_query_has_nonempty_ai_fields(self):
    queries = load_queries()
    for query in queries:
      assert len(query["ai_fields"]) > 0, f"Query {query['id']} has empty ai_fields"

  def test_display_hint_is_valid(self):
    queries = load_queries()
    valid_hints = {"table", "cards"}
    for query in queries:
      assert query["display_hint"] in valid_hints, (
        f"Query {query['id']} has invalid display_hint: {query['display_hint']}"
      )


class TestGetQueryById:
  def test_returns_matching_query(self, sample_json):
    queries = load_queries(sample_json)
    result = get_query_by_id(queries, "summary-hotels")

    assert result is not None
    assert result["id"] == "summary-hotels"
    assert result["name"] == "Hotel Description Summary"

  def test_returns_none_for_unknown_id(self, sample_json):
    queries = load_queries(sample_json)
    result = get_query_by_id(queries, "nonexistent-id")
    assert result is None
