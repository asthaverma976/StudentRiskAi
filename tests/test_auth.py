import unittest
import os
import tempfile

import auth
import database
from auth import ADMIN_ROLE, HEAD_ROLE, require_admin


class StopRendering(Exception):
    pass


class FakeSidebar:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}
        self.secrets = {}
        self.sidebar = FakeSidebar()

    def title(self, *_args):
        pass

    def info(self, *_args):
        pass

    def caption(self, *_args):
        pass

    def error(self, *_args):
        pass

    def button(self, *_args, **_kwargs):
        return False

    def stop(self):
        raise StopRendering()


class AccountDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.previous_db_path = database.DB_PATH
        self.db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file.close()
        database.DB_PATH = self.db_file.name
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self.previous_db_path
        os.unlink(self.db_file.name)

    def test_head_bootstrap_and_admin_authentication(self):
        super_admin = "asthaverma976@gmail.com"
        self.assertTrue(database.bootstrap_head(super_admin, "strong-password"))
        account = database.authenticate_admin(super_admin.upper(), "strong-password")
        self.assertEqual(account, {"email": super_admin, "role": HEAD_ROLE})
        self.assertIsNone(database.authenticate_admin(super_admin, "wrong-password"))
        self.assertFalse(database.bootstrap_head("other@example.com", "strong-password"))
        self.assertFalse(database.bootstrap_head(super_admin, "short"))

    def test_recipient_isolation_and_forged_recipient_rejection(self):
        database.bootstrap_head("head@example.com", "strong-password")
        self.assertTrue(database.create_admin("asthaverma976@gmail.com", "admin@example.com", "another-strong-password"))
        complaint_id, tracking_code = database.insert_complaint(
            None, "Please repair the lab", "Negative", "Infrastructure", "High",
            assigned_admin_email="admin@example.com",
            return_tracking=True,
        )
        self.assertEqual(database.track_complaint(tracking_code)["status"], "Pending")
        self.assertIsNone(database.track_complaint("CMP-NOT-REAL"))
        self.assertEqual(database.get_stats("admin@example.com")["total"], 1)
        self.assertEqual(database.get_stats()["total"], 1)
        self.assertFalse(database.update_status(complaint_id, "Resolved", "head@example.com"))
        self.assertTrue(database.update_status(complaint_id, "Resolved", "admin@example.com"))
        with self.assertRaises(ValueError):
            database.insert_complaint(None, "test", "Neutral", "Library", "Low", assigned_admin_email="forged@example.com")

    def test_only_super_admin_can_create_or_delete_accounts(self):
        with self.assertRaises(PermissionError):
            database.create_admin("admin@example.com", "other@example.com", "another-strong-password")
        self.assertTrue(database.create_admin("asthaverma976@gmail.com", "other@example.com", "another-strong-password"))
        with self.assertRaises(PermissionError):
            database.delete_admin("other@example.com", "other@example.com")
        self.assertTrue(database.delete_admin("asthaverma976@gmail.com", "other@example.com"))

    def test_general_user_records_cannot_use_admin_or_head_roles(self):
        with self.assertRaises(ValueError):
            database.create_user("ADMIN-1", "Unauthorized Admin", "password123", "admin")
        with self.assertRaises(ValueError):
            database.create_user("HEAD-1", "Unauthorized Head", "password123", "head")

    def test_legacy_complaints_are_migrated_as_unassigned(self):
        conn = database.get_connection()
        conn.execute(
            "INSERT INTO complaints (student_name, text, sentiment, category, priority, status, created_at) "
            "VALUES ('Anonymous', 'legacy', 'Neutral', 'Library', 'Low', 'Pending', '2026-01-01')"
        )
        conn.commit()
        conn.close()
        self.assertIsNone(database.fetch_all_complaints()[0]["assigned_admin_email"])


class AdminGuardTests(unittest.TestCase):
    def setUp(self):
        self.previous_streamlit = auth.st
        self.previous_db_path = database.DB_PATH
        self.db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file.close()
        database.DB_PATH = self.db_file.name
        database.init_db()
        database.create_admin("asthaverma976@gmail.com", "admin@example.com", "another-strong-password")
        auth.st = FakeStreamlit()

    def tearDown(self):
        auth.st = self.previous_streamlit
        database.DB_PATH = self.previous_db_path
        os.unlink(self.db_file.name)

    def test_unauthenticated_session_stops_before_dashboard_can_render(self):
        with self.assertRaises(StopRendering):
            require_admin()

    def test_admin_role_is_allowed_through_the_guard(self):
        auth.st.session_state["role"] = ADMIN_ROLE
        auth.st.session_state["admin_email"] = "admin@example.com"
        self.assertEqual(require_admin(), {"email": "admin@example.com", "role": ADMIN_ROLE})


if __name__ == "__main__":
    unittest.main()
