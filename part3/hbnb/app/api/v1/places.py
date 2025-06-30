#!/usr/bin/env python3
"""API endpoints for Place resources."""

from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade
from flask_jwt_extended import jwt_required


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
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new place."""
        try:
            place_data = request.json

            if ('amenities' not in place_data or
                    place_data['amenities'] is None):
                place_data['amenities'] = []

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
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': "An unexpected error occurred: {}"
                    .format(str(e))}, 500

    @api.response(200, 'List of places retrieved successfully')
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
    @api.response(404, 'Place not found')
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

            response = {
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': place.price,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'owner': owner_data,
            }

            amenities_data = [
                {
                    'id': amenity.id,
                    'name': amenity.name
                }
                for amenity in place.amenities
            ]

            if amenities_data:
                response['amenities'] = amenities_data

            reviews_data = [
                {
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user.id
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
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, place_id):
        """Update a place's information."""
        try:
            place_data = request.json

            try:
                place = facade.get_place(place_id)
            except KeyError:
                return {'error': 'Place not found'}, 404

            facade.update_place(place_id, place_data)

            return {
                'message': 'Place updated successfully'
            }, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': "An unexpected error occurred: {}"
                    .format(str(e))}, 500
