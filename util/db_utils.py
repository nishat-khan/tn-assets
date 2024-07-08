from schema import Asset


class MockAssetTable:
    def __init__(self):
        self.assets = []

    def add_asset(self, asset: Asset):
        if not isinstance(asset, Asset):
            raise ValueError("asset must be an instance of Asset")
        self.assets.append(asset)

    def query(self):
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
