#!/usr/bin/env python3

from app.persistence.repository import InMemoryRepository
from app.models.place import Place
from app.models.user import User
from app.models.amenity import Amenity
import uuid

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # Placeholder method for creating a user
    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user
    
    def get_user(self, user_id):
        return self.user_repo.get(user_id)
    
    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_user(self):
        return self.user_repo.get_all()
    
    def put_user(self, user_id, data):
        return self.user_repo.update(user_id, data)
   
    def get_all_user(self):
        return self.user_repo.get_all()

    def create_amenity(self, amenity_data):
        name = amenity_data.get("name")
        new_amenity = Amenity(name)
        self.amenity_repo.add(new_amenity)
        return new_amenity

    def get_amenity(self, amenity_id):
        new_amenity = self.amenity_repo.get(amenity_id)
        return new_amenity

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if amenity is None:
            return None
        amenity.update(amenity_data)
        return amenity

    
    def create_place(self, place_data):
        required_fields = ['title', 'price', 'latitude', 'longitude', 'owner_id']
        for field in required_fields:
            if field not in place_data:
                raise ValueError(f"Missing required field: {field}")

        owner = self.get_user(place_data["owner_id"])
        if owner is None:
            raise ValueError("Invalid owner_id: owner does not exist.")
        
        new_place = Place(
            title=place_data["title"],
            description=place_data.get("description", ""),
            price=place_data["price"],
            latitude=place_data["latitude"],
            longitude=place_data["longitude"],
            owner=owner
        )

        amenities = place_data.get('amenities', None)
    
        if amenities is not None:
            for amenity_id in amenities:
                if amenity_id:
                    amenity = self.amenity_repo.get(amenity_id)
                    if amenity is None:
                        raise ValueError(f"Amenity with id {amenity_id} does not exist.")
                    new_place.add_amenity(amenity)

        self.place_repo.add(new_place)
        owner.add_place(new_place)
        return new_place

    def get_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place is None:
            raise KeyError("Place not found.")
        return place

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """Update a place with the given data"""
        place = self.get_place(place_id)
        if not place:
            raise ValueError(f"Place with id {place_id} does not exist.")
        
        updatable_attrs = ['title', 'description', 'price', 'latitude', 'longitude']
        for attr in updatable_attrs:
            if attr in place_data and place_data[attr] is not None:
                setattr(place, attr, place_data[attr])
        
        if 'amenity_ids' in place_data:
            place.amenities = []
            place.amenity_ids = []
            
            for amenity_id in place_data['amenity_ids']:
                amenity = self.amenity_repo.get(amenity_id)
                if amenity is None:
                    raise ValueError(f"Amenity with id {amenity_id} does not exist.")
                place.add_amenity(amenity)
        
        return place
