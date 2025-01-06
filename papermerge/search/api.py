from salinic import IndexRO, Search, create_engine, IndexRW
from papermerge.core.db.engine import Session
from papermerge.core.features.users import schema as usr_schema
from papermerge.core.features.auth import get_current_user
from papermerge.core.config import get_settings
from papermerge.search.schema import SearchIndex, PaginatedResponse
from papermerge.search.schema import FOLDER, PAGE, SearchIndexRequest
from papermerge.core import dbapi, schema
from typing import Annotated, List
from papermerge.core.features.auth import scopes
import logging
from uuid import UUID
config = get_settings()
logger = logging.getLogger(__name__)

def searchForIndex(
    q: str,
    user_id: str, 
    page_number: int = 1,
    page_size: int = 10
):
    engine = create_engine(config.papermerge__search__url)
    index = IndexRO(engine, schema=SearchIndex)

    sq = Search(SearchIndex).query(q, page_number=page_number, page_size=page_size)
    results = index.search(sq=sq, user_id=user_id)

    return results

def createSearchIndex(node_ids: SearchIndexRequest):
    engine = create_engine(config.papermerge__search__url)
    index = IndexRW(engine, schema=SearchIndex)
    items = []  # to be added to the index

    with Session() as db_session:
        nodes = dbapi.get_nodes(db_session, None, node_ids.node_ids)
        logger.info("user_id: "+str(node_ids.user_id)+" nodes: "+ str(nodes))
        for node in nodes:
            if isinstance(node, schema.Document):
                last_ver = dbapi.get_last_doc_ver(
                    db_session, user_id=str(node_ids.user_id), doc_id=node.id
                )
                pages = dbapi.get_doc_ver_pages(db_session, last_ver.id)
                for page in pages:
                    item = SearchIndex(
                        id=str(page.id),
                        title=node.title,
                        user_id=str(node_ids.user_id),
                        document_id=str(node.id),
                        document_version_id=str(last_ver.id),
                        page_number=page.number,
                        text=page.text,
                        entity_type=PAGE,
                        tags=[tag.name for tag in node.tags],
                    )
                    items.append(item)
            else:
                item = SearchIndex(
                    id=str(node.id),
                    title=node.title,
                    user_id=str(node_ids.user_id),
                    entity_type=FOLDER,
                    tags=[tag.name for tag in node.tags],
                )

                items.append(item)

        for item in items:
            index.add(item)
            
        logger.info("added index: "+ str(items))
    return items


def deleteSearchIndex(request: SearchIndexRequest):
    """
    Deletes documents, pages, or folders from the search index.
    
    Args:
        request (SearchIndexRequest): SearchIndexRequest List of UUIDs of documents, pages, or folders to delete from the index.
    
    Returns:
        List of deleted index items.
    """
    engine = create_engine(config.papermerge__search__url)
    index = IndexRW(engine, schema=SearchIndex)
    deleted_items = []  # to hold the deleted items for logging or other purposes
    
    for node_id in request.node_ids:
        try:
            indices = searchForIndex(q=str(node_id), user_id=str(request.user_id))
            for doc in indices.items:
                logger.info(f"Attempting to remove item from index: {str(doc)}")
                index.remove(id=doc.id)
                deleted_items.append(doc)
        except Exception as e:
            logger.error(f"Failed to delete item {node_id} from the index: {e}")
    
    logger.info(f"Deleted items from index: {deleted_items}")
    return deleted_items