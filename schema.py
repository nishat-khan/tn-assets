from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Tag(BaseModel):
    key: str
    value: str


class CloudAccount(BaseModel):
    id: str
    name: str


class Asset(BaseModel):
    id: str
    name: str
    type: str
    tags: List[Tag]
    cloud_account: CloudAccount
    owner_id: str
    region: str
    group_name: str = None


class Condition(BaseModel):
    operator: str
    field: str = None
    value: str = None
    key: str = None
    conditions: List[Any] = None


class Rule(BaseModel):
    conditions: Condition


class GroupingRequest(BaseModel):
    group_name: str
    rules: List[Rule]
