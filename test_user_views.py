"""User View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY


db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testfollower = User.signup(username="testfollower",
                                    email="test2@test.com",
                                    password="testfollower",
                                    image_url=None)

        db.session.commit()

    def test_user_profile(self):
        """Access user profile"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h4 id="sidebar-username">@{self.testuser.username}</h4>', html)

    def test_user_likes(self):
        """Test user likes page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            likes_count_before = Likes.query.filter(Likes.user_id == self.testuser.id).count()
            self.assertEqual(likes_count_before, 0)

            # Add a new message
            resp = c.post("/messages/new", data={"text": "Hello"})
            msg = Message.query.one()

            # Like the message
            likeresp = c.post(f"/users/add_like/{msg.id}")

            # Count the new message liked
            likes_count_after = Likes.query.filter(Likes.user_id == self.testuser.id).count()
            self.assertEqual(likes_count_after, 1)

            # Test unlike the message
            likeresp = c.post(f"/users/unlike/{msg.id}")

            # Count the new message liked
            likes_count_new = Likes.query.filter(Likes.user_id == self.testuser.id).count()
            self.assertEqual(likes_count_new, 0)

    def test_user_follow(self):
        """Test follow user functionality"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                followed_id = self.testfollower.id

            resp = c.post(f"/users/follow/{followed_id}")
            self.assertEqual(resp.status_code, 302)

            resp2 = c.get(f"/users/{self.testuser.id}/following")
            html = resp2.get_data(as_text=True)
            self.assertIn("<p>@testfollower</p>", html)

