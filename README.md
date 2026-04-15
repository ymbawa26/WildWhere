# WildWhere

WildWhere helps people explore likely wildlife sightings by park, season, and time of day.

[Try the browser demo](https://ymbawa26.github.io/WildWhere/)

## What is in this repo

- `docs/` contains a public GitHub Pages demo that runs fully in the browser.
- `Wildwhere/` contains the Flask + scikit-learn app and trained model assets.

## Two ways to use it

### 1. Instant browser demo

Open the GitHub Pages site above to try WildWhere without installing anything.

The public demo is intentionally transparent: it uses a client-side scoring model so visitors can explore the experience right away.

### 2. Full local Flask app

```bash
cd Wildwhere
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Then open `http://127.0.0.1:5000`.

## Notes

- The local Flask app uses the trained model in `Wildwhere/models/wildlife_model.joblib` when available.
- The browser demo is public-facing and deployment-friendly for GitHub visitors.
- The Flask app is now set up to serve its own frontend, which makes future hosting on a Python platform much simpler.
