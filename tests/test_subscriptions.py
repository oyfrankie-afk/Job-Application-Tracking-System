import os
import sys
import sqlite3
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database


class SubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        database.DB_PATH = self.temp_db.name
        database.create_database()

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_add_and_read_subscription(self):
        database.add_subscription('user@example.com', 'Python Developer', 'Remote')
        subs = database.get_subscriptions()
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0][1], 'user@example.com')
        self.assertEqual(subs[0][2], 'Python Developer')
        self.assertEqual(subs[0][3], 'Remote')

    def test_delete_subscription(self):
        database.add_subscription('user@example.com', 'Python Developer', 'Remote')
        subs = database.get_subscriptions()
        deleted = database.delete_subscription(subs[0][0])
        self.assertEqual(deleted, 1)
        self.assertEqual(database.get_subscriptions(), [])

    def test_pause_and_resume_subscription(self):
        database.add_subscription('user@example.com', 'Python Developer', 'Remote')
        subs = database.get_subscriptions()
        sub_id = subs[0][0]
        updated = database.set_subscription_paused(sub_id, True)
        self.assertEqual(updated, 1)
        subs = database.get_subscriptions()
        self.assertEqual(subs[0][6], 1)
        updated = database.set_subscription_paused(sub_id, False)
        self.assertEqual(updated, 1)
        subs = database.get_subscriptions()
        self.assertEqual(subs[0][6], 0)

    def test_subscription_url_history(self):
        database.add_subscription('user@example.com', 'Python Developer', 'Remote')
        sub_id = database.get_subscriptions()[0][0]
        urls = ['https://example.com/job1', 'https://example.com/job2']
        database.save_subscription_sent_urls(sub_id, urls)
        seen = database.get_subscription_sent_urls(sub_id)
        self.assertEqual(seen, set(urls))


if __name__ == '__main__':
    unittest.main()
