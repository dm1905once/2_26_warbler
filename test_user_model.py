"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

#db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_new(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # Validate the repr function
        self.assertEqual(f"<User #{u.id}: testuser, test@test.com>",u.__repr__())

        # Update profile
        u.update_profile("test2@test.com", "http://pic1.com", "http://pic2.com", "bio")
        self.assertEqual(f"<User #{u.id}: testuser, test2@test.com>",u.__repr__())
        self.assertEqual("http://pic1.com", u.image_url)
        self.assertEqual("http://pic2.com", u.header_image_url)
        self.assertEqual("bio", u.bio)

    def test_user_auth(self):
        """Test user authentication methods"""

        new_user = User.signup("testuser3", "test3@test3.com", "HASHED_PASSWORD3", "http://image_url.com")
        db.session.add(new_user)
        db.session.commit()

        self.assertEqual("testuser3", new_user.username)

        authenticated = User.authenticate("testuser3", "HASHED_PASSWORD3")
        self.assertEqual(new_user, authenticated)

        nonauthenticated = User.authenticate("testuser3", "WRONG_PWD")
        self.assertEqual(False, nonauthenticated)