from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="CB AI Explorer")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


# Temporary scaffolding route to verify HTMX fragment delivery (task 1.12)
# Remove after infrastructure setup is complete
@app.get("/test-fragment", response_class=HTMLResponse)
def test_fragment(request: Request):
    return templates.TemplateResponse(request, "partials/test_fragment.html")
