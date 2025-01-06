from typing import Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

LangCode = Literal[
    "ces",
    "dan",
    "deu",
    "ell",
    "eng",
    "fas",
    "fin",
    "fra",
    "guj",
    "heb",
    "hin",
    "ita",
    "jpn",
    "kor",
    "lit",
    "nld",
    "nor",
    "pol",
    "por",
    "ron",
    "san",
    "spa",
]


class OCRTaskIn(BaseModel):
    document_id: UUID  # document model ID
    lang: LangCode

class OCRTaskOut(BaseModel):
    task_id: UUID

class OCRTaskStatus(BaseModel):
    task_id: UUID
    status: str
    date_done: Optional[datetime]
