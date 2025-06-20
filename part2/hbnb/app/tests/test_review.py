#!/usr/bin/env python3
"""Tests for Review model and APIs."""

import unittest
from app import create_app
from app.models.user import User
from app.models.place import Place
from app.models.review import Review


class TestReviewModel(unittest.TestCase):
    """Test cases for Review model."""

    def test_review_creation(self):
        """Test successful Review creation with valid data."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        review = Review(text="Great experience!",
                        rating=5, place=place, user=user)

        self.assertEqual(review.text, "Great experience!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.place, place)
        self.assertEqual(review.user, user)

    def test_review_creation_empty_text(self):
        """Test that Review creation raises ValueError with empty text."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        with self.assertRaises(ValueError):
            Review(text="", rating=5, place=place, user=user)

    def test_review_creation_invalid_rating_low(self):
        """Test that Review creation raises ValueError with rating < 1."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        with self.assertRaises(ValueError):
            Review(text="Bad experience", rating=0, place=place, user=user)

    def test_review_creation_invalid_rating_high(self):
        """Test that Review creation raises ValueError with rating > 5."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        with self.assertRaises(ValueError):
            Review(text="Amazing beyond rating scale",
                   rating=6, place=place, user=user)

    def test_review_creation_invalid_rating_type(self):
        """Test that Review creation raises ValueError with non-int rating."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        with self.assertRaises(ValueError):
            Review(text="Good place", rating="5", place=place, user=user)

    def test_review_creation_null_place(self):
        """Test that Review creation raises ValueError with null place."""
        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        with self.assertRaises(ValueError):
            Review(text="Good experience",
                   rating=4, place=None, user=user)

    def test_review_creation_null_user(self):
        """Test that Review creation raises ValueError with null user."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        with self.assertRaises(ValueError):
            Review(text="Good experience",
                   rating=4, place=place, user=None)

    def test_review_text_setter(self):
        """Test setting the text property of a Review."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        review = Review(text="Initial review",
                        rating=4, place=place, user=user)
        review.text = "Updated review"

        self.assertEqual(review.text, "Updated review")

    def test_review_text_setter_invalid(self):
        """Test that setting an invalid text raises ValueError."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        review = Review(text="Initial review",
                        rating=4, place=place, user=user)

        with self.assertRaises(ValueError):
            review.text = ""

    def test_review_rating_setter(self):
        """Test setting the rating property of a Review."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        review = Review(text="Good place",
                        rating=3, place=place, user=user)
        review.rating = 5

        self.assertEqual(review.rating, 5)

    def test_review_rating_setter_invalid(self):
        """Test that setting an invalid rating raises ValueError."""
        owner = User(first_name="Alice", last_name="Smith",
                     email="alice.smith@example.com")

        place = Place(title="Cozy Apartment",
                      description="A nice place to stay",
                      price=100, latitude=37.7749,
                      longitude=-122.4194, owner=owner)

        user = User(first_name="Bob", last_name="Johnson",
                    email="bob@example.com")

        review = Review(text="Good place", rating=3, place=place, user=user)

        with self.assertRaises(ValueError):
            review.rating = 0
        with self.assertRaises(ValueError):
            review.rating = 6
        with self.assertRaises(ValueError):
            review.rating = "3"


class TestReviewEndpoints(unittest.TestCase):
    """Test cases for Review API endpoints."""

    def setUp(self):
        """Set up test client and create test user and place."""
        self.app = create_app()
        self.client = self.app.test_client()

        user_response = self.client.post('/api/v1/users/', json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com"
        })
        self.user_id = user_response.json["id_user"]

        place_response = self.client.post('/api/v1/places/', json={
            "title": "Cozy Apartment",
            "description": "A nice place to stay",
            "price": 100,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner_id": self.user_id
        })
        self.place_id = place_response.json["id"]

    def test_create_review(self):
        """Test creating a review with valid data."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Great place to stay!",
            "rating": 5,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["text"], "Great place to stay!")
        self.assertEqual(response.json["rating"], 5)
        self.assertEqual(response.json["user_id"], self.user_id)
        self.assertEqual(response.json["place_id"], self.place_id)
        self.assertIn("id", response.json)

        self.review_id = response.json["id"]

    def test_create_review_empty_text(self):
        """Test that creating a review with empty text fails."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "",
            "rating": 4,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_create_review_invalid_rating(self):
        """Test that creating a review with invalid rating fails."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Nice place",
            "rating": 6,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_create_review_invalid_user_id(self):
        """Test that creating a review with invalid user_id fails."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Nice place",
            "rating": 4,
            "user_id": "invalid-user-id",
            "place_id": self.place_id
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_create_review_invalid_place_id(self):
        """Test that creating a review with invalid place_id fails."""
        response = self.client.post('/api/v1/reviews/', json={
            "text": "Nice place",
            "rating": 4,
            "user_id": self.user_id,
            "place_id": "invalid-place-id"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_get_all_reviews(self):
        """Test getting all reviews."""
        self.client.post('/api/v1/reviews/', json={
            "text": "Great experience!",
            "rating": 5,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        response = self.client.get('/api/v1/reviews/')

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreater(len(response.json), 0)

    def test_get_review_by_id(self):
        """Test getting a specific review by ID."""
        create_response = self.client.post('/api/v1/reviews/', json={
            "text": "Amazing views!",
            "rating": 5,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        review_id = create_response.json["id"]

        response = self.client.get('/api/v1/reviews/{}'.format(review_id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["id"], review_id)
        self.assertEqual(response.json["text"], "Amazing views!")
        self.assertEqual(response.json["rating"], 5)

    def test_get_reviews_by_place(self):
        """Test getting all reviews for a specific place."""
        self.client.post('/api/v1/reviews/', json={
            "text": "Great location!",
            "rating": 5,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        self.client.post('/api/v1/reviews/', json={
            "text": "Very clean",
            "rating": 4,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        response = self.client.get('/api/v1/reviews/places/{}/reviews'
                                   .format(self.place_id))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 2)

    def test_get_nonexistent_review(self):
        """Test getting a review that doesn't exist."""
        response = self.client.get('/api/v1/reviews/nonexistent-id')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    def test_update_review(self):
        """Test updating a review's attributes."""
        create_response = self.client.post('/api/v1/reviews/', json={
            "text": "Good place",
            "rating": 3,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        review_id = create_response.json["id"]

        update_response = self.client.put(
            '/api/v1/reviews/{}'.format(review_id),
            json={
                "text": "Much better than initially thought",
                "rating": 4
            }
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertIn("message", update_response.json)

        get_response = self.client.get(
            '/api/v1/reviews/{}'.format(review_id)
        )
        self.assertEqual(get_response.json["text"],
                         "Much better than initially thought")
        self.assertEqual(get_response.json["rating"], 4)

    def test_update_review_invalid_data(self):
        """Test updating a review with invalid data."""
        create_response = self.client.post('/api/v1/reviews/', json={
            "text": "Good place",
            "rating": 3,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        review_id = create_response.json["id"]

        update_response = self.client.put(
            '/api/v1/reviews/{}'.format(review_id),
            json={
                "text": "",
                "rating": 6
            }
        )

        self.assertEqual(update_response.status_code, 400)
        self.assertIn("error", update_response.json)

    def test_delete_review(self):
        """Test deleting a review."""
        create_response = self.client.post('/api/v1/reviews/', json={
            "text": "Review to delete",
            "rating": 3,
            "user_id": self.user_id,
            "place_id": self.place_id
        })

        review_id = create_response.json["id"]

        delete_response = self.client.delete('/api/v1/reviews/{}'
                                             .format(review_id))
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("message", delete_response.json)

        get_response = self.client.get('/api/v1/reviews/{}'.format(review_id))
        self.assertEqual(get_response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
