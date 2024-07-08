from flask import g
import json
import os
import pytest

from group_assets.group_assets import create_app
from schema import Asset
from util.db_utils import MockAssetTable


def get_file_path(file_name):
    base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'data', file_name)

@pytest.fixture
def client(populate_mock_db):
    app = create_app(populate_mock_db)
    with app.test_client() as client:
        with app.app_context():
            g.db = populate_mock_db
        yield client


@pytest.fixture
def load_assets():
    file_path = get_file_path('assets.json')
    with open(file_path, 'r') as f:
        assets = json.load(f)
    return [Asset(**asset) for asset in assets]

@pytest.fixture
def load_grouping_data_prod_instances():
    file_path = get_file_path('test_grouping_data_prod_instances.json')
    with open(file_path, 'r') as f:
        grouping_data = json.load(f)
    return grouping_data


@pytest.fixture
def load_errored_grouping_data_prod_instances():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data', 'test_errored_grouping_data_prod_instances.json')
    with open(file_path, 'r') as f:
        grouping_data = json.load(f)
    return grouping_data


@pytest.fixture
def valid_simple_request():
    file_path = get_file_path('test_valid_simple_request.json')
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture
def valid_nested_request():
    file_path = get_file_path('test_valid_nested_request.json')
    with open(file_path) as f:
        return json.load(f)


@pytest.fixture
def populate_mock_db(load_assets):
    mock_db = MockAssetTable()
    for asset in load_assets:
        mock_db.add_asset(asset)
    return mock_db