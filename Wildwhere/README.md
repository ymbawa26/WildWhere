# WildWhere 2.0 — Wildlife Sighting Predictor

A small Flask + scikit-learn app that predicts likely wildlife by park, month, and time of day.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Then open `http://127.0.0.1:5000`.

The app now serves the web interface directly, so you no longer need to open `web/index.html` manually.
