def test_fragment_returns_html_content_type(client):
  """HTMX fragment endpoint returns text/html content type."""
  response = client.get("/query/sentiment-hotels")
  assert response.status_code == 200
  assert "text/html" in response.headers["content-type"]


def test_fragment_contains_expected_content(client):
  """Fragment contains the expected partial HTML content."""
  response = client.get("/query/sentiment-hotels")
  assert "Hotel Review Sentiment" in response.text


def test_fragment_is_not_full_page(client):
  """Fragment is a partial — no <html> or <head> tags."""
  response = client.get("/query/sentiment-hotels")
  body = response.text.lower()
  assert "<html" not in body, "Fragment should not contain <html> tag"
  assert "<head" not in body, "Fragment should not contain <head> tag"
  assert "<!doctype" not in body, "Fragment should not contain <!DOCTYPE>"
