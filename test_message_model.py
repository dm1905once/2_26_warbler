"""Message model tests."""

import os
from unittest import TestCase
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class UserMessageTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_messages(self):
        """Messages"""

        # Create user to own messages
        u = User(
            email="message@test.com",
            username="msguser",
            password="PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # Create a first message
        new_message = Message(text="Hi, I'm a test message", user_id=u.id)
        db.session.add(new_message)
        db.session.commit()

        # Validate that message was created and assigned to the test user
        self.assertEqual(len(u.messages), 1)

        # Validate relationship
        self.assertEqual(u.id, new_message.user.id)

        # Validate message content
        self.assertEqual("Hi, I'm a test message", new_message.text)
