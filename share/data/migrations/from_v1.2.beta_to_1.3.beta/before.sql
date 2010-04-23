ALTER TABLE accounts_userprofile ADD COLUMN "language" varchar(2) NOT NULL DEFAULT 'fr';
ALTER TABLE site_cartype RENAME TO carpool_cartype;
ALTER TABLE site_city RENAME TO carpool_city;
ALTER TABLE site_favoriteplace RENAME TO carpool_favoriteplace;
ALTER TABLE site_trip RENAME TO carpool_trip;
ALTER TABLE site_tripdemand RENAME TO carpool_tripdemand;
ALTER TABLE site_tripoffer RENAME TO carpool_tripoffer;

ALTER INDEX "site_favoriteplace_point_id" RENAME TO "carpool_favoriteplace_point_id"
ALTER INDEX "site_trip_arrival_point_id" RENAME TO "carpool_trip_arrival_point_id";
ALTER INDEX "site_city_slug" RENAME TO "carpool_city_slug";
ALTER INDEX "site_tripdemand_passenger_car_type_id" RENAME TO "carpool_tripdemand_passenger_car_type_id";
ALTER INDEX "site_tripoffer_driver_car_type_id" RENAME TO "carpool_tripoffer_driver_car_type_id";
ALTER INDEX "site_trip_user_id" RENAME TO "carpool_trip_user_id";
ALTER INDEX "site_trip_offer_id" RENAME TO "carpool_trip_offer_id";
ALTER INDEX "site_trip_demand_id" RENAME TO "carpool_trip_demand_id";
ALTER INDEX "site_trip_departure_point_id" RENAME TO "carpool_trip_departure_point_id";
ALTER INDEX "site_tripoffer_direction_route_id" RENAME TO "carpool_tripoffer_direction_route_id";
ALTER INDEX "site_tripoffer_simple_route_id" RENAME TO "carpool_tripoffer_simple_route_id";
ALTER INDEX "site_tripoffer_route_id" RENAME TO "carpool_tripoffer_route_id";
ALTER INDEX "site_city_point_id" RENAME TO "carpool_city_point_id";

-- SEQUENCES
ALTER TABLE site_cartype_id_seq RENAME TO carpool_cartype_id_seq
ALTER TABLE site_city_id_seq RENAME TO carpool_city_id_seq;
ALTER TABLE site_favoriteplace_id_seq RENAME TO carpool_favoriteplace_id_seq;
ALTER TABLE site_trip_id_seq RENAME TO carpool_trip_id_seq;
ALTER TABLE site_tripdemand_id_seq RENAME TO carpool_tripdemand_id_seq;
ALTER TABLE site_tripoffer_id_seq RENAME TO carpool_tripoffer_id_seq;
