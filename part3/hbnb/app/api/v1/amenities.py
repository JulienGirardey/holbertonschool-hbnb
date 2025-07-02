from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new amenity"""
        data_amenity = api.payload
        try:
            new_amenity = facade.create_amenity(data_amenity)
        except ValueError as e:
            api.abort(400, str(e))
        return {"id": new_amenity.id, "name":new_amenity.name}, 201
    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""
        
        amenities = facade.get_all_amenities()
        return[amenity.to_dict() for amenity in amenities],200

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
       
        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            api.abort(404, "Amenity not found")
        return amenity.to_dict(),200
    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, amenity_id):
        """Update an amenity's information"""
        
        data_amenity = api.payload

        amenity=facade.get_amenity(amenity_id)
        if amenity is None:
            api.abort(404,"Amenity not found")
        try:
            updated_amenity = facade.update_amenity(amenity_id, data_amenity)
        except ValueError as e:
            api.abort(400, str(e))
        return updated_amenity.to_dict(), 200
@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        data_amenity = api.payload
        try:
            new_amenity = facade.create_amenity(data_amenity)
        except ValueError as e:
            return{"error": str(e)},400
        return{"id":new_amenity.id,"name":new_amenity.name},201

@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    @jwt_required()
    def put(self, amenity_id):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        data_amenity = api.payload

        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            return {'error': 'Amenity not found'}, 404

        try:
            updated_amenity = facade.update_amenity(amenity_id, data_amenity)
        except ValueError as e:
            return {'error': str(e)}, 400

        return updated_amenity.to_dict(), 200
    