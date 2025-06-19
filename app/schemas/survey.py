from pydantic import BaseModel
from typing import List

class ChoiceBase(BaseModel):
    text: str

class ChoiceCreate(ChoiceBase):
    pass

class ChoiceRead(ChoiceBase):
    id: str

    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    text: str

class QuestionCreate(QuestionBase):
    choices: List[ChoiceCreate]

class QuestionRead(QuestionBase):
    id: str
    choices: List[ChoiceRead]

    class Config:
        orm_mode = True

class SurveyCreate(BaseModel):
    title: str
    questions: List[QuestionCreate]

class SurveyRead(BaseModel):
    id: str
    title: str
    questions: List[QuestionRead]

    class Config:
        orm_mode = True
