#!/usr/bin/env python3
"""API endpoints for Place resources."""

from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity


api = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

place_model = api.model('Place', {
    'title': fields.String(required=True,
                           description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True,
                             description='Latitude of the place'),
    'longitude': fields.Float(required=True,
                              description='Longitude of the place'),
    'owner_id': fields.String(required=True,
                              description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model),
                             description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model),
                           description='List of reviews')
})


@api.route('/')
class PlaceList(Resource):
    """Resource for collection of places."""

    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Bad Request')
    @api.response(500, 'An unexpected error occurred')
    @jwt_required()
    def post(self):
        """Register a new place."""
        current_user_id = get_jwt_identity()
        try:
            place_data = request.json

            if ('amenities' not in place_data or
                    place_data['amenities'] is None):
                place_data['amenities'] = []
                
            place_data['owner_id'] = current_user_id
            new_place = facade.create_place(place_data)

            response = {
                'id': new_place.id,
                'title': new_place.title,
                'description': new_place.description,
                'price': new_place.price,
                'latitude': new_place.latitude,
                'longitude': new_place.longitude,
                'owner_id': new_place.owner.id,
            }

            amenity_ids = [amenity.id for amenity in new_place.amenities]
            if amenity_ids:
                response['amenities'] = amenity_ids

            return response, 201

        except ValueError as e:
            return {"error": "Invalid input data: {}".format(str(e))}, 400
        except Exception as e:
            return {'error': "An unexpected error occurred: {}"
                    .format(str(e))}, 500

    @api.response(200, 'List of places retrieved successfully')
    @api.response(500, 'An unexpected error occurred')
    def get(self):
        """Retrieve a list of all places."""
        try:
            places = facade.get_all_places()
            return [
                {
                    'id': place.id,
                    'title': place.title,
                    'latitude': place.latitude,
                    'longitude': place.longitude
                }
                for place in places
            ], 200
        except Exception as e:
            return {'error': "An unexpected error occurred: {}"
                    .format(str(e))}, 500


@api.route('/<place_id>')
class PlaceResource(Resource):
    """Resource for individual place operations."""

    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Not found')
    @api.response(500, 'An unexpected error occurred')
    def get(self, place_id):
        """Get place details by ID."""
        try:
            try:
                place = facade.get_place(place_id)
            except KeyError:
                return {'error': 'Place not found'}, 404

            owner = place.owner
            owner_data = {
                'id': owner.id,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'email': owner.email
            }
            
            amenities_data = [
                {
                    'id': amenity.id,
                    'name': amenity.name
                }
                for amenity in place.amenities
            ]

            response = {
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'amenities': amenities_data,
                'owner': owner_data,
            }
            
            if amenities_data:
                response['amenities'] = amenities_data

            reviews_data = [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user.id,
                    'user_firstName': review.user.first_name,
                    'user_lastName': review.user.last_name
                }
                for review in place.reviews
            ]

            if reviews_data:
                response['reviews'] = reviews_data

            return response, 200

        except Exception as e:
            return {'error': "An unexpected error occurred: {}"
                    .format(str(e))}, 500

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(400, 'Bad Request')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Not found')
    @api.response(500, 'An unexpected error occurred')
    @jwt_required()
    def put(self, place_id):
        """Update a place's information."""
        current_user_id = get_jwt_identity()
        current_user = facade.get_user(current_user_id)
        
        if not current_user:
            return {'error': 'Invalid user'}, 401
        
        is_admin = current_user.is_admin

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        if not is_admin and place.owner_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403
        
        place_data = request.json
        try:
            updated_place = facade.update_place(place_id, place_data)
            return {
                'id': updated_place.id,
                'title': updated_place.title,
                'description': updated_place.description,
                'price': updated_place.price,
                'latitude': updated_place.latitude,
                'longitude': updated_place.longitude,
                'owner_id': updated_place.owner_id,
            }, 200
        except ValueError as e:
            return {"error": "Invalid input data: {}".format(str(e))}, 400
        except Exception as e:
            return {'error': 'An unexpected error occurred: {}'.format(str(e))}, 500
