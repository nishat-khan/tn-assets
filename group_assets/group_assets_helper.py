from typing import List, Dict, Any
from schema import Asset
from util.logger import setup_logger

logger = setup_logger('group_assets_app')


def validate_conditions(conditions: Dict[str, Any]) -> bool:

    def check_condition_structure(cond: Dict[str, Any]) -> bool:
        """Check if the condition has the necessary keys"""
        if 'operator' not in cond or 'conditions' not in cond and ('field' not in cond or 'value' not in cond):
            return False

        # Recursively check nested conditions
        if 'conditions' in cond:
            return all(check_condition_structure(c) for c in cond['conditions'])
        return True

    def collect_conditions(cond: Dict[str, Any], collected: List[Dict[str, Any]]):
        """Collect all non-nested conditions"""
        if 'conditions' in cond:
            for c in cond['conditions']:
                collect_conditions(c, collected)
        else:
            collected.append(cond)

    def has_conflicts(conditions_list: List[Dict[str, Any]]) -> bool:
        field_conditions = {}

        for cond in conditions_list:
            field = cond['field']
            if field not in field_conditions:
                field_conditions[field] = []
            field_conditions[field].append(cond)

        for field, conds in field_conditions.items():
            if len(conds) > 1:
                # Check for conflicts within the same field
                for i, cond1 in enumerate(conds):
                    for cond2 in conds[i + 1:]:
                        if cond1['operator'] == 'contains' and cond2['operator'] == 'contains':
                            if cond1['value'] in cond2['value'] or cond2['value'] in cond1['value']:
                                return True
                        elif cond1['operator'] == '==' and cond2['operator'] == '==':
                            if cond1['value'] != cond2['value']:
                                return True
        return False

    # Check the structure of the conditions
    if not check_condition_structure(conditions):
        return False

    # Collect all non-nested conditions for conflict checking
    collected_conditions = []
    collect_conditions(conditions, collected_conditions)

    # Check for conflicts within the collected conditions
    if has_conflicts(collected_conditions):
        return False

    return True


def apply_conditions(asset: Asset, conditions: Dict[str, Any]) -> bool:
    """Implement logic to check if an asset matches the conditions"""
    if conditions["operator"] == "AND":
        return all(apply_conditions(asset, cond) for cond in conditions["conditions"])
    elif conditions["operator"] == "OR":
        return any(apply_conditions(asset, cond) for cond in conditions["conditions"])
    else:
        field = conditions["field"]
        if field == "tags":
            return any(tag.key == conditions["key"] and tag.value == conditions["value"] for tag in asset.tags)
        elif field in asset.__fields_set__:
            if conditions["operator"] == "==":
                return getattr(asset, field) == conditions["value"]
            elif conditions["operator"] == "contains":
                return conditions["value"] in getattr(asset, field)
        return False


def filter_assets_by_user(user_id: str, assets_db: List[Asset]) -> List[Asset]:
    return [asset for asset in assets_db if asset.owner_id == user_id]
