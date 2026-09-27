import unittest

class TestOmen(unittest.TestCase):
    def test_config(self):
        from app.config import config
        self.assertIsNotNone(config)

    def test_database(self):
        from database.database import get_db
        db = get_db()
        self.assertIsNotNone(db)

    def test_tool_registry(self):
        from tools.registry import get_tool_registry
        registry = get_tool_registry()
        self.assertIsNotNone(registry)

if __name__ == '__main__':
    unittest.main()
