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


class TestLoadingIndicator:
    def test_run_button_has_hx_indicator(self, client):
        """Run Query button includes hx-indicator attribute."""
        response = client.get("/query/sentiment-hotels")
        html = response.text
        assert "hx-indicator" in html
