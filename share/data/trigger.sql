CREATE OR REPLACE FUNCTION proj_route() RETURNS trigger AS $proj_route$
    BEGIN
        NEW.simple_route_proj := ST_Transform(NEW.simple_route, 27572);
        NEW.direction_route_proj := ST_Transform(NEW.direction_route, 27572);
        RETURN NEW;
    END;
$proj_route$ LANGUAGE plpgsql;


CREATE TRIGGER proj_route BEFORE INSERT OR UPDATE ON carpool_tripoffer
    FOR EACH ROW EXECUTE PROCEDURE proj_route();

CREATE OR REPLACE FUNCTION proj_points() RETURNS trigger AS $proj_points$
    BEGIN
        NEW.departure_point_proj := ST_Transform(NEW.departure_point, 27572);
        NEW.arrival_point_proj := ST_Transform(NEW.arrival_point, 27572);
        RETURN NEW;
    END;
$proj_points$ LANGUAGE plpgsql;


CREATE TRIGGER proj_points BEFORE INSERT OR UPDATE ON carpool_trip
    FOR EACH ROW EXECUTE PROCEDURE proj_points();
