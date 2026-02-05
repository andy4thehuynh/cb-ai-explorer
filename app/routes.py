from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.query_loader import load_queries, get_queries_by_category, get_query_by_id

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

router = APIRouter()

_queries = load_queries()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    categories = get_queries_by_category(_queries)
    return templates.TemplateResponse(request, "index.html", {"categories": categories})


@router.get("/query/{query_id}", response_class=HTMLResponse)
def query_detail(request: Request, query_id: str):
    query = get_query_by_id(_queries, query_id)
    if query is None:
        return HTMLResponse(status_code=404, content="Query not found")
    return templates.TemplateResponse(request, "partials/query_detail.html", {"query": query})
