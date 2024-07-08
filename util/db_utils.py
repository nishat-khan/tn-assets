
class MockAssetTable:
    def __init__(self):
        self.assets = []

    def add_asset(self, asset):
        self.assets.append(asset)

    def query(self, asset_class):
        class MockQuery:
            def __init__(self, assets):
                self.assets = assets

            def filter(self, condition):
                key, operator, value = condition.split()
                value = value.strip('"')
                if operator == '==':
                    self.assets = [asset for asset in self.assets if getattr(asset, key) == value]
                return self

            def all(self):
                return self.assets

        return MockQuery(self.assets)
