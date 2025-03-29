# TrailSurfNET 🏕️🌍

**Automated Trail Surface Classification Using OpenStreetMap and Satellite Imagery**

TrailSurfNET is a research project exploring the classification of hiking trail surfaces using a combination of OpenStreetMap (OSM) data and satellite imagery. The goal is to improve trail metadata quality and support applications in hiking, land management, and geospatial analysis.

## 🔍 Project Objectives

- Extract and clean trail data from OSM (UK + Ireland)
- Standardize trail surface types into high-level categories (e.g., Gravel, Dirt, Asphalt)
- Calculate total trail distances by surface type
- Prepare geometry data for satellite image extraction (e.g., Sentinel-2)
- Train convolutional neural networks (CNNs) to classify trail surfaces using remote sensing data

## 📂 Project Structure

- `Data Collection.ipynb` – SQL queries and exploratory analysis of OSM data
- `Exploratory Analysis.ipynb` – Trail length calculations, surface groupings
- `myenv/` – Virtual environment (not tracked in Git)
- `.gitignore` – Excludes virtual environment, large PBF files, cache
- `README.md` – Project overview and objectives

## 🛠️ Tech Stack

- PostgreSQL + PostGIS for spatial database and queries
- osm2pgsql for importing OSM data
- Jupyter Notebooks for data exploration and preprocessing
- Python (Pandas, NumPy, etc.) for analysis
- Satellite imagery: Sentinel-2, Landsat (planned)
- Deep learning: PyTorch / TensorFlow (planned)

## 📈 Progress

- ✅ Imported and cleaned OSM trail data for UK & Ireland
- ✅ Classified `surface` values into 8 standard `surface_group`s
- ✅ Calculated total trail distance by surface type
- ⏳ Preparing bounding boxes for satellite imagery
- ⏳ Model training with CNNs for image-based classification

## 🌍 Future Work

- Integrate Sentinel-2 imagery with trail geometries
- Train and evaluate CNN models (e.g., ResNet, VGG-16)
- Improve classification of `Unknown` surfaces
- Visualize trail quality in QGIS or web map

---

## 📜 License

This project uses open data from:
- [OpenStreetMap](https://www.openstreetmap.org/about) (ODbL)
- [Sentinel-2](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) (Copernicus, ESA)

Project code is available under the MIT License (or your preferred license).

---

## 🙌 Contributions

This is part of an MSc thesis at the National College of Ireland. Contributions, ideas, or feedback are welcome!








# Implementation Notes

## Install Postgresql DB
brew install postgresql postgis
brew services start postgresql

CREATE DATABASE osm;
\c osm
CREATE EXTENSION postgis;
CREATE EXTENSION hstore;

## Download OSM Data
wget https://download.geofabrik.de/europe/ireland-and-northern-ireland-latest.osm.pbf
wget https://download.geofabrik.de/europe/united-kingdom-latest.osm.pbf

osm2pgsql --create --slim --extra-attributes --hstore --hstore-add-index -d osm --cache 8000 united-kingdom-latest.osm.pbf ireland-and-northern-ireland-latest.osm.pbf

## Run Notebook
- `python3 -m venv myenv`
- `source myenv/bin/activate`
- `pip install -r requirements.txt`
- `jupyter notebook`

Backing up the Database
`pg_dump -U markfinlay -h localhost -p 5432 osm > osm_backup.sql`

