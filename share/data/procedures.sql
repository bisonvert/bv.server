CREATE OR REPLACE FUNCTION get_pourcentage_rank(route geometry, departure geometry, arrival geometry) RETURNS integer AS $$
    -- assuming type of route is LINESTRING
    DECLARE
        numpoint integer;
        dposition double precision;
        aposition double precision;
    BEGIN
        -- init
        numpoint := ST_NumPoints(route);
        IF numpoint IS NOT NULL AND numpoint > 0 THEN
            -- at least one point
            dposition := ST_line_locate_point(route, departure);
            aposition := ST_line_locate_point(route, arrival);
            -- * 20 = * 100 / 5
            IF aposition != 'Nan' AND dposition != 'Nan' THEN
                RETURN ROUND((aposition - dposition) * 20) * 5;
            ELSE
                RETURN 0;
            END IF;
        ELSE
            -- route null or empty
            RETURN 0;
        END IF;
    END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION match_date_interval_dows(date date, interval_min integer, interval_max integer, dows integer[]) RETURNS boolean AS $$
    BEGIN
        FOR i IN 0..interval_min
        LOOP
            IF EXTRACT(dow FROM date - i) = ANY (dows) THEN
                RETURN True;
            END IF;
        END LOOP;
        FOR i IN 0..interval_max
        LOOP
            IF EXTRACT(dow FROM date + i) = ANY (dows) THEN
                RETURN True;
            END IF;
        END LOOP;
        RETURN False;
    END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION match_dows(dows1 integer[], dows2 integer[]) RETURNS boolean AS $$
    BEGIN
        IF array_upper(dows1, 1) IS NULL THEN
            RETURN False;
        END IF;
        FOR i IN array_lower(dows1, 1)..array_upper(dows1, 1)
        LOOP
            IF dows1[i] = ANY (dows2) THEN
                RETURN True;
            END IF;
        END LOOP;
        RETURN False;
    END;
$$ LANGUAGE plpgsql;
