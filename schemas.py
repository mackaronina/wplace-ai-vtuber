from enum import Enum

from pydantic import BaseModel


class GradeEnum(str, Enum):
    negative = 'negative'
    neutral = 'neutral'
    positive = 'positive'


class CommentModel(BaseModel):
    text: str
    grade: GradeEnum
