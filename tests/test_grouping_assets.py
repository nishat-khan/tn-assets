# tests/test_grouping_assets.py
from flask import g
import json
import os
import pytest

from group_assets.group_assets import create_app
from schema import Asset
from util.db_utils import MockAssetTable
from tests.group_assets_fixtures import *
from util.utils import fetch_assets_for_user, validate_grouping_request


def test_fetch_assets_for_user(populate_mock_db):
    """Test to ensure filter on owner_id==user_id works"""
    user_id = "user1"
    assets = fetch_assets_for_user(populate_mock_db, user_id)
    assert len(assets) == 2
    assert assets[0].owner_id == user_id


def test_fetch_empty_assets_for_user(populate_mock_db):
    user_id = "user3"
    assets = fetch_assets_for_user(populate_mock_db, user_id)
    assert len(assets) == 0


def test_apply_grouping_rules(client, populate_mock_db, load_grouping_data_prod_instances):
    response = client.post('/apply-grouping-rules', json=load_grouping_data_prod_instances, headers={"Authorization": "token-user1"})
    assert response.status_code == 200

    # Check if the assets have been grouped correctly for user1
    user1_assets = fetch_assets_for_user(populate_mock_db, "user1")
    assert any(asset.group_name == "production-instances" for asset in user1_assets)

def test_apply_errored_grouping_rules(client, populate_mock_db, load_errored_grouping_data_prod_instances):
    response = client.post('/apply-grouping-rules', json=load_errored_grouping_data_prod_instances, headers={"Authorization": "token-user1"})
    assert response.status_code == 200

    # Check if the assets have been grouped correctly for user1
    user1_assets = fetch_assets_for_user(populate_mock_db, "user1")
    assert any(asset.group_name == "production-instances" for asset in user1_assets)


def test_validate_grouping_requests(client, valid_simple_request, valid_nested_request):
    for request in [valid_simple_request, valid_nested_request]:
        try:
            validated_request = validate_grouping_request(request)
            print(f"Validation successful for {request['group_name']}")
        except ValueError as e:
            print(f"Validation failed: {str(e)}")
