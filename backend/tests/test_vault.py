import unittest
from unittest.mock import MagicMock
from services.privacy_vault import PrivacyVaultService

class TestPrivacyVault(unittest.TestCase):
    def test_export_structure(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db.query.return_value.filter_by.return_value.all.return_value = []
        mock_db.query.return_value.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []

        vault = PrivacyVaultService.export_full_vault(mock_db, user_id=1)
        self.assertIn("vault_metadata", vault)
        self.assertIn("episodic_memories", vault)
        self.assertIn("associative_graph", vault)
        self.assertIn("consolidated_schemas", vault)
        self.assertEqual(vault["vault_metadata"]["format_version"], "2.0.0")

    def test_prune_episode(self):
        mock_db = MagicMock()
        mock_ep = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_ep

        success = PrivacyVaultService.prune_episode(mock_db, user_id=1, episode_id=42)
        self.assertTrue(success)
        mock_db.delete.assert_called_once_with(mock_ep)
        mock_db.commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()
