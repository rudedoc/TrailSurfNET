# TrailSurfNET 🏕️🌍

**Automated Trail Surface Classification Using OpenStreetMap and Satellite Imagery**

TrailSurfNET is a research project exploring the classification of hiking trail surfaces using a combination of OpenStreetMap (OSM) data and satellite imagery. The goal is to improve trail metadata quality and support applications in hiking, land management, and geospatial analysis.

## 🔍 Project Objectives

- Extract and clean trail data from OSM (UK + Ireland)
- Standardize trail surface types into high-level categories (e.g., Gravel, Dirt, Asphalt)
- Calculate total trail distances by surface type
- Prepare geometry data for satellite image extraction (e.g., Sentinel-2)
- Train convolutional neural networks (CNNs) to classify trail surfaces using remote sensing data

## 🛠️ Tech Stack

- PostgreSQL + PostGIS for spatial database and queries `brew install postgresql`
- PostgreSQL exxensions required:
- - postgis `brew install postgis`
  - hstore
- osm2pgsql for importing OSM data
- Jupyter Notebooks for data exploration and preprocessing
- Python (Pandas, NumPy, etc.) for analysis
- Satellite imagery: Sentinel-2, Landsat (planned)
- Deep learning: PyTorch / TensorFlow (planned)

## 📂 Project Structure
- `setup_db.py` - builds DB and loads OSM data into DB
- `OSM Data.ipynb` – Prepares the OSM Data
- `Sentinel 2 Data.ipynb` – Collects the Satelite Data for each row in trail_segments
- `Training.ipynb` - Trains the model
- `myenv/` – Virtual environment (not tracked in Git)
- `.gitignore` – Excludes virtual environment, large PBF files, cache
- `README.md` – Project overview and objectives

## 🛠️ Setup
- make sure your DB is running! `brew services start postgresql@17`
- `python3 -m venv myenv`
- `source myenv/bin/activate`
- `pip install -r requirements.txt`
- `python setup_db.py` - run the setup script
- `jupyter notebook`

## Note on Github and Jupyter Notebooks
- in the notebook go to kernal >> Restart Kernel and Clear Outputs of All Cells
- Then do file >> save
This reduces the notebook back to is pure code and removes any cached images and data so that the notebook can be checked into github

## 📈 Progress

- ✅ Imported and cleaned OSM trail data for UK & Ireland
- ✅ Classified `surface` values into 5 standard `surface_group`s
- ✅ Balance `surface_group` Classes
- ✅ Compile trail_segments and bounding boxes for satellite imagery
- ✅ Gather Sentinel 2 Data and store PNGs in DB - 30K images
- ✅ Model training with CNNs for image-based classification
- ✅ First Complete Draft the Thesis
- ⏳ Preparation of Powerpoint
- ⏳ Preparation of Video

## 🌍 Future Work

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




