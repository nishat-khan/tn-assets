from typing import List, Union, Dict, Any

from schema import GroupingRequest
from util.db_utils import MockAssetTable


def get_user_id_from_token(token: str) -> str:
    """
    Simplified token parsing to extract user ID. In a real application, use a library to handle this securely.
    Assuming token is in the format "token-userid"
    :param token:
    :return:
    """
    return token.split('-')[1]


def fetch_assets_for_user(db: MockAssetTable, user_id: str):
    """Fetches assets for a user."""
    return db.query().filter(f'owner_id == "{user_id}"').all()


def validate_grouping_request(request_data: Dict[str, Any]) -> GroupingRequest:
    try:
        grouping_request = GroupingRequest(**request_data)
        return grouping_request
    except ValueError as e:
        raise ValueError(f"Invalid grouping request: {str(e)}")