def test_health_endpoint(client):
  """GET /health returns 200 with {"status": "ok"}."""
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "ok"}


class TestIndexPage:
  def test_returns_200(self, client):
    response = client.get("/")
    assert response.status_code == 200

  def test_contains_query_names(self, client):
    response = client.get("/")
    html = response.text
    assert "Hotel Review Sentiment" in html
    assert "Hotel Description Summary" in html

  def test_queries_grouped_by_category(self, client):
    response = client.get("/")
    html = response.text
    assert "sentiment" in html.lower()
    assert "summary" in html.lower()


class TestQueryDetail:
  def test_returns_200_for_valid_id(self, client):
    response = client.get("/query/sentiment-hotels")
    assert response.status_code == 200

  def test_contains_query_info(self, client):
    response = client.get("/query/sentiment-hotels")
    html = response.text
    assert "Hotel Review Sentiment" in html
    assert "before_query" in html or "ai_sentiment" in html
    assert "Run Query" in html

  def test_returns_404_for_invalid_id(self, client):
    response = client.get("/query/nonexistent-query")
    assert response.status_code == 404


class TestQueryRun:
  def test_returns_200_with_html(self, client, mock_execute_query):
    """POST /query/{id}/run returns 200 with HTML content."""
    response = client.post("/query/sentiment-hotels/run")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

  def test_contains_before_and_after_sections(self, client, mock_execute_query):
    """Response HTML has before and after results sections."""
    response = client.post("/query/sentiment-hotels/run")
    html = response.text
    assert "before" in html.lower()
    assert "after" in html.lower()

  def test_returns_404_for_invalid_id(self, client, mock_execute_query):
    """POST /query/{invalid-id}/run returns 404."""
    response = client.post("/query/nonexistent-query/run")
    assert response.status_code == 404

  def test_returns_error_partial_on_query_failure(self, client, mock_execute_query_error):
    """When Couchbase query raises an error, returns error partial."""
    response = client.post("/query/sentiment-hotels/run")
    assert response.status_code == 200
    html = response.text
    assert "error" in html.lower() or "alert" in html.lower()


class TestHtmxHeaders:
  def test_query_detail_returns_html_fragment(self, client):
    """GET /query/{id} returns text/html and is a fragment (no <html> tag)."""
    response = client.get("/query/sentiment-hotels")
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "<html" not in html.lower()
    assert "<head" not in html.lower()

  def test_query_run_returns_html_fragment(self, client, mock_execute_query):
    """POST /query/{id}/run returns text/html and is a fragment (no <html> tag)."""
    response = client.post("/query/sentiment-hotels/run")
    assert "text/html" in response.headers["content-type"]
    html = response.text
    assert "<html" not in html.lower()
    assert "<head" not in html.lower()


class TestLoadingIndicator:
  def test_run_button_has_hx_indicator(self, client):
    """Run Query button includes hx-indicator attribute."""
    response = client.get("/query/sentiment-hotels")
    html = response.text
    assert "hx-indicator" in html
