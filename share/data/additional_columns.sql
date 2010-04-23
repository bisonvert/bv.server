SELECT AddGeometryColumn('site_tripoffer', 'simple_route_proj', 27572, 'MULTILINESTRING', 2);
ALTER TABLE "site_tripoffer" ALTER "simple_route_proj" SET NOT NULL;
CREATE INDEX "site_tripoffer_simple_route_proj_id" ON "site_tripoffer" USING GIST ( "simple_route_proj" GIST_GEOMETRY_OPS );

SELECT AddGeometryColumn('site_tripoffer', 'direction_route_proj', 27572, 'LINESTRING', 2);
ALTER TABLE "site_tripoffer" ALTER "direction_route_proj" SET NOT NULL;
CREATE INDEX "site_tripoffer_direction_route_proj_id" ON "site_tripoffer" USING GIST ( "direction_route_proj" GIST_GEOMETRY_OPS );

SELECT AddGeometryColumn('site_trip', 'departure_point_proj', 27572, 'POINT', 2);
ALTER TABLE "site_trip" ALTER "departure_point_proj" SET NOT NULL;
CREATE INDEX "site_trip_departure_point_proj_id" ON "site_trip" USING GIST ( "departure_point_proj" GIST_GEOMETRY_OPS );

SELECT AddGeometryColumn('site_trip', 'arrival_point_proj', 27572, 'POINT', 2);
ALTER TABLE "site_trip" ALTER "arrival_point_proj" SET NOT NULL;
CREATE INDEX "site_trip_arrival_point_proj_id" ON "site_trip" USING GIST ( "arrival_point_proj" GIST_GEOMETRY_OPS );
