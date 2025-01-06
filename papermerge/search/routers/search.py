from fastapi import APIRouter, Depends, HTTPException, Security
from papermerge.core.db.engine import Session
from papermerge.core.features.users import schema as usr_schema
from papermerge.core.features.auth import get_current_user
from papermerge.search.schema import SearchIndex, PaginatedResponse
from papermerge.search.schema import FOLDER, PAGE, SearchIndexRequest
from papermerge.core import dbapi, schema
from papermerge.search.api import createSearchIndex, deleteSearchIndex, searchForIndex
from typing import Annotated, List
from papermerge.core.features.auth import scopes
import logging

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse)
def search(
    q: str,
    page_number: int = 1,
    page_size: int = 10,
    user: usr_schema.User = Depends(get_current_user),
):

    return searchForIndex(q=q, user_id=str(user.id), page_number=page_number, page_size=page_size)

@router.post("/index", response_model=list[SearchIndex])
def indexNode(index_nodes: SearchIndexRequest,
              user: Annotated[schema.User, Security(get_current_user, scopes=[scopes.NODE_UPDATE])]):
    return createSearchIndex(index_nodes)
    
@router.delete("/index", response_model=list[SearchIndex])
def indexNode(index_nodes: SearchIndexRequest,
              user: Annotated[schema.User, Security(get_current_user, scopes=[scopes.NODE_UPDATE])]):
    return deleteSearchIndex(index_nodes)