from flask import Flask, g, jsonify, request
from pydantic import ValidationError
from typing import List, Union, Dict, Any
from schema import GroupingRequest, NestedCondition, Condition
from util.logger import setup_logger
from util.utils import get_user_id_from_token, fetch_assets_for_user
from .group_assets_helper import apply_conditions


def create_app(db):
    """
    Function to make sure mock db context is applied.
    :param db:
    :return:
    """
    app = Flask(__name__)
    logger = setup_logger('group_assets_app')

    def set_db():
        g.db = db

    @app.before_request
    def before_request():
        if 'db' not in g:
            set_db()

    @app.route('/apply-grouping-rules', methods=['POST'])
    def apply_grouping_rules():
        """
        API to fetch the user_id using token from Authorization and applies the grouping rules.
        :return:
        """
        token = request.headers.get('Authorization')
        if not token:
            logger.info('Authorization token is missing')
            return jsonify({"error": "Authorization token is missing"}), 401

        user_id = get_user_id_from_token(token)
        try:
            data = request.json
            grouping_request = GroupingRequest(**data)
        except ValidationError as e:
            logger.info(f'Validation error for user {user_id}: {e}')
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return jsonify({"error": str(e)}), 500

        logger.info(f'User {user_id} is applying rules for group {grouping_request.group_name}')

        try:
            user_assets = fetch_assets_for_user(g.db, user_id)

            # Checking for edge case no assets returned
            if not user_assets:
                logger.info(f'No assets found for user {user_id}')
                return jsonify({"error": "No assets found for the user"}), 404

            for asset in user_assets:
                for rule in grouping_request.rules:
                    if apply_rule_conditions(asset, rule.conditions):
                        asset.group_name = grouping_request.group_name
                        logger.info(f'Asset {asset.id} grouped into {grouping_request.group_name} by user {user_id}')
            logger.info(f'Grouping applied successfully for user {user_id} and group {grouping_request.group_name}')
            return jsonify({"message": "Grouping applied successfully"}), 200
        except Exception as e:
            logger.error(f'Error applying grouping rules for user {user_id}: {e}')
            return jsonify({"error": str(e)}), 500

    return app

def apply_rule_conditions(asset: Dict[str, Any], conditions: Union[Condition, NestedCondition]) -> bool:
    """
    Recursively apply conditions to an asset.
    """
    if isinstance(conditions, Condition):
        return apply_conditions(asset, conditions.dict())
    elif isinstance(conditions, NestedCondition):
        if conditions.operator == "AND":
            return all(apply_rule_conditions(asset, cond) for cond in conditions.conditions)
        elif conditions.operator == "OR":
            return any(apply_rule_conditions(asset, cond) for cond in conditions.conditions)
    return False

# uncomment this if you wanna test the server on your end
# if __name__ == '__main__':
#     from util.utils import MockAssetTable
#     mock_db = MockAssetTable()
#     app = create_app(mock_db)
#     app.run(debug=True)
