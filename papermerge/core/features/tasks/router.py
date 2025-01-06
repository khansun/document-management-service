from fastapi import APIRouter, Security
from typing import Annotated
from papermerge.core.utils.decorators import if_redis_present
from papermerge.celery_app import app as celery_app
import logging
from papermerge.core import constants, schema, utils, config
from papermerge.core.features.auth import get_current_user, scopes
from .schema import OCRTaskIn, OCRTaskOut, OCRTaskStatus
from celery.result import AsyncResult
from papermerge.search.api import createSearchIndex
from papermerge.search.schema import SearchIndexRequest
import threading
from uuid import UUID
import time
from fastapi import BackgroundTasks

settings = config.get_settings()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.post("/ocr")
@utils.docstring_parameter(scope=scopes.TASK_OCR)
def start_ocr(
    ocr_task: OCRTaskIn,
    user: Annotated[schema.User, Security(get_current_user, scopes=[scopes.TASK_OCR])],
    background_tasks: BackgroundTasks
) -> OCRTaskOut:
    """Triggers OCR for specific document

    Required scope: `{scope}`
    """
    result = celery_app.send_task(
        constants.WORKER_OCR_DOCUMENT,
        kwargs={
            "document_id": str(ocr_task.document_id),
            "lang": ocr_task.lang,
        },
        route_name="ocr",
    )
    logger.info(f"OCR Task sent: {str(result)}")
    return OCRTaskOut(task_id=result.task_id)


    
@router.get("/ocr/status/{task_id}")
def get_ocr_status(task_id: str) -> OCRTaskStatus:
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state:
            logger.info(f"Task {task_id} status: {result.state}")
        else:
            logger.warning(f"Task {task_id} state is None.")
        
        return OCRTaskStatus(task_id=task_id, status=result.state, date_done=result.date_done)
    except Exception as e:
        logger.error(f"Failed to retrieve OCR status for task {task_id}: {e}")
        return OCRTaskStatus(task_id=task_id, status=result.state or "Unknown", date_done=None)