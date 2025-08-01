-- database: /Users/Dev/Holberton/holbertonschool-hbnb/part3/hbnb/instance/development.db
-- inserte data and create admin
-- and add 3 amenity

INSERT INTO users (id, email, first_name, last_name, password, is_admin)
VALUES ("36c9050e-ddd3-4c3b-9731-9f487208bbc1", "admin@hbnb.io", "Admin", "HBnB", "$2b$12$DcqfWYcH6iC1sxyElC92PuxuxzEUK537bqEXT51zVk1rrFGqpDXcm", true);

INSERT INTO amenities (id, name) VALUES 
("550e8400-e29b-41d4-a716-446655440001", "WiFi"),
("550e8400-e29b-41d4-a716-446655440002", "Swimming Pool"),
("550e8400-e29b-41d4-a716-446655440003", "Air Conditioning");