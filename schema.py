from pydantic import BaseModel, Field, model_validator
from typing import List, Union, Dict, Any
from enum import Enum


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


class Operator(str, Enum):
    AND = "AND"
    OR = "OR"
    EQUALS = "=="
    CONTAINS = "contains"


class Condition(BaseModel):
    field: str
    operator: Operator
    value: str
    key: str | None = None


class NestedCondition(BaseModel):
    operator: Operator
    conditions: List[Union['NestedCondition', Condition]]


class Rule(BaseModel):
    conditions: Union[Condition, NestedCondition]


class GroupingRequest(BaseModel):
    group_name: str
    rules: List[Rule]

    @model_validator(mode='after')
    def validate_rules(self) -> 'GroupingRequest':
        for rule in self.rules:
            if isinstance(rule.conditions, NestedCondition):
                self.validate_nested_conditions(rule.conditions)
            else:
                self.validate_condition(rule.conditions)
        return self

    @classmethod
    def validate_nested_conditions(cls, nested_condition: NestedCondition):
        if nested_condition.operator not in [Operator.AND, Operator.OR]:
            raise ValueError(f"Invalid operator for nested condition: {nested_condition.operator}")

        for condition in nested_condition.conditions:
            if isinstance(condition, NestedCondition):
                cls.validate_nested_conditions(condition)
            else:
                cls.validate_condition(condition)

    @staticmethod
    def validate_condition(condition: Condition):
        if condition.operator == Operator.CONTAINS:
            if condition.field == "tags" and not condition.key:
                raise ValueError("Key is required for tag contains operation")
        elif condition.operator == Operator.EQUALS:
            if condition.field == "tags" and not condition.key:
                raise ValueError("Key is required for tag equals operation")
        elif condition.operator not in [Operator.EQUALS, Operator.CONTAINS]:
            raise ValueError(f"Invalid operator for condition: {condition.operator}")
