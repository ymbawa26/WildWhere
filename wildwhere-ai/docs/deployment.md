# Deployment

WildWhere AI is designed for Streamlit Community Cloud.

## Public Preview

The current public portfolio preview is deployed at:

```text
https://wildwhere-ai.vercel.app
```

## Rebuild Commands

```bash
pip install -r requirements.txt
python etl/run_pipeline.py
python models/train_model.py
```

## Streamlit Community Cloud

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, create a new app from the repository.
3. Set the app entry point to:

```text
app/main.py
```

4. Use the default Python environment from `requirements.txt`.
5. Do not add API keys. The default insight engine does not require paid services.

## Data Notes

The deployed app uses the processed CSV files committed in `data/processed/` and the model artifacts in `models/`. These are derived from real public datasets collected in Step 2. The app does not need to call GBIF, NPS, or NOAA at runtime.

## Troubleshooting

- If the app cannot find processed data, run `python etl/run_pipeline.py` and commit the processed CSVs.
- If the prediction page cannot load the model, run `python models/train_model.py` and commit `models/wildlife_model.pkl` and `models/model_metrics.json`.
- If dependency installation fails, confirm `requirements.txt` includes Streamlit, pandas, scikit-learn, plotly, and joblib.
