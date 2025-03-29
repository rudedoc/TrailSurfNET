# Setp Tools

## Install Postgresql DB
brew install postgresql postgis
brew services start postgresql

CREATE DATABASE osm;
\c osm
CREATE EXTENSION postgis;
CREATE EXTENSION hstore;



# Download OSM Data

wget https://download.geofabrik.de/europe/ireland-and-northern-ireland-latest.osm.pbf
wget https://download.geofabrik.de/europe/united-kingdom-latest.osm.pbf

osm2pgsql --create --slim --extra-attributes --hstore --hstore-add-index -d osm --cache 8000 united-kingdom-latest.osm.pbf ireland-and-northern-ireland-latest.osm.pbf



source myenv/bin/activate
jupyter notebook

