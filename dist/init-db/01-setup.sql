CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE TABLE IF NOT EXISTS public.properties (
     id varchar(100) NOT NULL,
     geocode_geo geography NULL,
     parcel_geo geography NULL,
     building_geo geography NULL,
     image_bounds float8[] NULL,
     image_url text NULL,
     CONSTRAINT properties_pk PRIMARY KEY (id)
);
