INSERT INTO airport (airport_code, airport_name, airport_country, airport_city, airport_address, longitude, latitude) VALUES
('JFK', 'John F. Kennedy International Airport', 'USA', 'New York', 'Queens, NY 11430', '-73.7781', '40.6413'),
('LAX', 'Los Angeles International Airport', 'USA', 'Los Angeles', '1 World Way, Los Angeles, CA 90045', '-118.4085', '33.9416'),
('ORD', 'O''Hare International Airport', 'USA', 'Chicago', '10000 W O''Hare Ave, Chicago, IL 60666', '-87.9073', '41.9742'),
('ATL', 'Hartsfield–Jackson Atlanta International Airport', 'USA', 'Atlanta', '6000 N Terminal Pkwy, Atlanta, GA 30320', '-84.4277', '33.6407'),
('DFW', 'Dallas/Fort Worth International Airport', 'USA', 'Dallas', '2400 Aviation Dr, DFW Airport, TX 75261', '-97.0403', '32.8998');

INSERT INTO aircraft (aircraft_id, manufacturer, aircraft_model, current_distance, maintenance_interval, aircraft_status, aircraft_location) VALUES
('11111111-1111-1111-1111-111111111111', 'Boeing', '737-800', 12000, 15000, 'AVAILABLE', 'JFK'),
('22222222-2222-2222-2222-222222222222', 'Airbus', 'A320', 18000, 20000, 'DEPLOYED', 'LAX'),
('33333333-3333-3333-3333-333333333333', 'Boeing', '787-9', 5000, 12000, 'AVAILABLE', 'ORD'),
('44444444-4444-4444-4444-444444444444', 'Embraer', 'E175', 21000, 25000, 'AOG', 'ATL'),
('55555555-5555-5555-5555-555555555555', 'Airbus', 'A321', 8000, 15000, 'AVAILABLE', 'DFW');


INSERT INTO in_flight_employee (employee_id, first_name, last_name, position, employee_status, supervisor, employee_location) VALUES
('aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'Sarah', 'Johnson', 'CAPTAIN', 'AVAILABLE', NULL, 'JFK'),
('aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 'Michael', 'Smith', 'COPILOT', 'AVAILABLE', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'JFK'),
('aaaaaaa3-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 'Emily', 'Davis', 'FLIGHT_MANAGER', 'AVAILABLE', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'JFK'),
('aaaaaaa4-aaaa-aaaa-aaaa-aaaaaaaaaaa4', 'James', 'Brown', 'FLIGHT_ATTENDANT', 'AVAILABLE', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 'JFK'),
('aaaaaaa5-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'Olivia', 'Wilson', 'CAPTAIN', 'AVAILABLE', NULL, 'ATL'),
('aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6', 'Jake', 'Martinez', 'COPILOT', 'AVAILABLE', 'aaaaaaa5-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'ATL'),
('aaaaaaa7-aaaa-aaaa-aaaa-aaaaaaaaaaa7', 'Paul', 'Martinez', 'FLIGHT_MANAGER', 'AVAILABLE', 'aaaaaaa5-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'ATL'),
('aaaaaaa8-aaaa-aaaa-aaaa-aaaaaaaaaaa8', 'Logan', 'Martinez', 'FLIGHT_ATTENDANT', 'AVAILABLE', 'aaaaaaa5-aaaa-aaaa-aaaa-aaaaaaaaaaa5', 'ATL');

INSERT INTO route (route_id, destination_airport_code, origin_airport_code) VALUES
('b1111111-1111-1111-1111-111111111111', 'LAX', 'JFK'),
('b2222222-2222-2222-2222-222222222222', 'ORD', 'LAX'),
('b3333333-3333-3333-3333-333333333333', 'ATL', 'ORD'),
('b4444444-4444-4444-4444-444444444444', 'DFW', 'ATL'),
('b5555555-5555-5555-5555-555555555555', 'JFK', 'DFW');

INSERT INTO flight (flight_id, route_id, flight_status, aircraft_id, arrival_time, departure_time) VALUES
('f1111111-1111-1111-1111-111111111111', 'b1111111-1111-1111-1111-111111111111', 'ARRIVED', '11111111-1111-1111-1111-111111111111', '2022-03-01 14:00:00', '2022-03-01 10:00:00'),
('f2222222-2222-2222-2222-222222222222', 'b2222222-2222-2222-2222-222222222222', 'ARRIVED', '22222222-2222-2222-2222-222222222222', '2023-03-01 16:30:00', '2023-03-01 13:00:00');

INSERT INTO flight_crew (flight_id, employee_id) VALUES
('f1111111-1111-1111-1111-111111111111', 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1'),
('f1111111-1111-1111-1111-111111111111', 'aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaa2'),
('f1111111-1111-1111-1111-111111111111', 'aaaaaaa3-aaaa-aaaa-aaaa-aaaaaaaaaaa3'),
('f1111111-1111-1111-1111-111111111111', 'aaaaaaa4-aaaa-aaaa-aaaa-aaaaaaaaaaa4'),

('f2222222-2222-2222-2222-222222222222', 'aaaaaaa5-aaaa-aaaa-aaaa-aaaaaaaaaaa5'),
('f2222222-2222-2222-2222-222222222222', 'aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6'),
('f2222222-2222-2222-2222-222222222222', 'aaaaaaa7-aaaa-aaaa-aaaa-aaaaaaaaaaa7'),
('f2222222-2222-2222-2222-222222222222', 'aaaaaaa8-aaaa-aaaa-aaaa-aaaaaaaaaaa8');
