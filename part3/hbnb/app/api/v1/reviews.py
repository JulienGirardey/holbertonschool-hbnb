from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('reviews', description='Review operations')

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user'),
    'place_id': fields.String(description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Bad Request')
    @api.response(500, 'An unexpected error occurred')
    @jwt_required()
    def post(self):
        """Register a new review."""
        current_user_id = get_jwt_identity()
        try:
            review_data = request.json
            place = facade.get_place(review_data['place_id'])

            if place.owner.id == current_user_id:
                return {'error': 'You cannot review your own place'}, 400

            for review in place.reviews:
                if review.user.id == current_user_id:
                    return {'error': 'You have already reviewed this place'}, 400

            review_data['user_id'] = current_user_id
            new_review = facade.create_review(review_data)

            return {
                'id': new_review.id,
                'text': new_review.text,
                'rating': new_review.rating,
                'user_id': new_review.user.id,
                'place_id': new_review.place.id
            }, 201

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    @api.response(200, 'List of reviews retrieved successfully')
    @api.response(500, 'An unexpected error occurred')
    def get(self):
        """Retrieve a list of all reviews."""
        try:
            reviews = facade.get_all_reviews()
            return [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating
                }
                for review in reviews
            ], 200
        except Exception as e:
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Not found')
    @api.response(500, 'An unexpected error occurred')
    def get(self, review_id):
        """Get review details by ID."""
        try:
            review = facade.get_review(review_id)
            if not review:
                return {'error': 'Review not found'}, 404
            return {
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user.id,
                'place_id': review.place.id
            }, 200
        except Exception as e:
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Not found')
    @api.response(500, 'An unexpected error occurred')
    @jwt_required()
    def put(self, review_id):
        """Update a review's information."""
        current_user_id = get_jwt_identity()
        review = facade.get_review(review_id)
        if review.user.id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            review_data = request.json

            try:
                review = facade.get_review(review_id)
            except KeyError:
                return {'error': 'Review not found'}, 404

            facade.update_review(review_id, review_data)

            return {
                'message': 'Review updated successfully'
            }, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': "An unexpected error occurred: {}".format(str(e))}, 500

    @api.response(200, 'Review deleted successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review."""
        current_user_id = get_jwt_identity()
        review = facade.get_review(review_id)
        if review.user.id != current_user_id:
            return {'error': 'Unauthorized action'}, 403
        
        try:
            try:
                facade.get_review(review_id)
            except KeyError:
                return {'error': 'Review not found'}, 404

            facade.delete_review(review_id)

            return {
                'message': 'Review deleted successfully'
            }, 200

        except Exception as e:
            return {'error': "An unexpected error occurred: {}".format(str(e))}, 500


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    """Resource for retrieving reviews by place."""

    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Not found')
    @api.response(500, 'An unexpected error occurred')
    def get(self, place_id):
        """Get all reviews for a specific place."""
        try:
            try:
                reviews = facade.get_reviews_by_place(place_id)
            except KeyError:
                return {'error': 'Place not found'}, 404

            return [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating
                }
                for review in reviews
            ], 200

        except Exception as e:
            return {'error': "An unexpected error occurred: {}".format(str(e))}, 500
@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Not found')
    @api.response(500, 'An unexpected error occurred')
    @jwt_required()
    def put(self, review_id):
        current_user = get_jwt_identity()
        is_admin = current_user.get('is_admin', False)
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        review_data = request.json
        try:
            updated_review = facade.update_review(review_id, review_data)
        except ValueError as e:
            return {'error': str(e)}, 400

        return updated_review.to_dict(), 200
    
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review (admin can delete any, user only own)."""
        current_user = get_jwt_identity()
        is_admin = current_user.get('is_admin', False)
        user_id = current_user.get('id') if isinstance(current_user, dict) else current_user

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_review(review_id)
            return {'message': 'Review deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 400

@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place."""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating
                }
                for review in reviews
            ], 200
        except KeyError:
            return {'error': 'Place not found'}, 404
        except Exception as e:
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500