import unittest

from server import app
from model import db, example_data, connect_to_db


class RatingsIntegrationTests(unittest.TestCase):
    """Tests for Ratings site"""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("View all movies", result.data)


class RatingsTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def logged_in(self, user_id):
        with self.client as c:
            with c.session_transaction() as sesh:
                sesh['user_id'] = user_id

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        # import pdb; pdb.set_trace()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        # Closes database session and drops all tables/data
        db.session.close()
        db.drop_all()

    def test_login(self):
        """Test that log out button appears when logged in"""
        self.logged_in(666)
        result = self.client.get("/")
        self.assertIn("Log Out", result.data)

    def test_movie_list(self):
        """Test that movie list contains example movies"""
        result = self.client.get("/movies")
        self.assertIn("Killer Cupcakes", result.data)

    def test_user_list(self):
        """Test that user list contains example users"""
        result = self.client.get("/users")
        self.assertIn("test@test.com", result.data)

    def test_movie_detail_page(self):
        """Test that movie pages display example movie details"""
        result = self.client.get("/movie-page/1")
        self.assertIn("1995-01-01 00:00:00", result.data)

    def test_movie_rating_loggedin(self):
        """Test that movie rating form appears for logged in users"""
        self.logged_in(666)
        result = self.client.get("/movie-page/1")
        self.assertIn("Rate It!", result.data)

if __name__ == "__main__":
    unittest.main()
