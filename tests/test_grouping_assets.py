# tests/test_grouping_assets.py
from flask import g
import json
import os
import pytest

from group_assets.group_assets import create_app
from schema import Asset
from util.db_utils import MockAssetTable
from util.utils import fetch_assets_for_user


@pytest.fixture
def client(populate_mock_db):
    app = create_app(populate_mock_db)
    with app.test_client() as client:
        with app.app_context():
            g.db = populate_mock_db
        yield client


@pytest.fixture
def load_assets():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', 'assets.json')
    with open(file_path, 'r') as f:
        assets = json.load(f)
    return [Asset(**asset) for asset in assets]

@pytest.fixture
def load_grouping_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', 'test_grouping_data.json')
    with open(file_path, 'r') as f:
        grouping_data = json.load(f)
    return grouping_data

@pytest.fixture
def populate_mock_db(load_assets):
    mock_db = MockAssetTable()
    for asset in load_assets:
        mock_db.add_asset(asset)
    return mock_db


def test_fetch_assets_for_user(populate_mock_db):
    user_id = "user1"
    assets = fetch_assets_for_user(populate_mock_db, user_id)
    assert len(assets) == 1
    assert assets[0].owner_id == user_id


def test_fetch_empty_assets_for_user(populate_mock_db):
    user_id = "user3"
    assets = fetch_assets_for_user(populate_mock_db, user_id)
    assert len(assets) == 0


def test_apply_grouping_rules(client, populate_mock_db, load_grouping_data):
    response = client.post('/apply-grouping-rules', json=load_grouping_data, headers={"Authorization": "token-user1"})
    assert response.status_code == 200

    # Check if the assets have been grouped correctly for user1
    user1_assets = fetch_assets_for_user(populate_mock_db, "user1")
    assert any(asset.group_name == "production-instances" for asset in user1_assets)
