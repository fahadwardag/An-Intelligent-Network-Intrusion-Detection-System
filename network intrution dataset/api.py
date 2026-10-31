
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
FRONTEND = BASE_DIR / "frontend"

app = FastAPI(
    title="SecureGuard AI API",
    version="1.0",
    description="Cybersecurity ML/DL Portfolio API"
)


def find_file(filename, folders):
    for folder in folders:
        path = BASE_DIR / folder / filename
        if path.is_file():
            return path
    return None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/models")
def get_models():
    path = find_file(
        "model_comparison.csv",
        ["reports", "."]
    )

    if path is None:
        raise HTTPException(
            status_code=404,
            detail="model_comparison.csv not found"
        )

    df = pd.read_csv(path)

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    df = df.rename(columns={
        "f1-score": "f1",
        "f1_score": "f1",
        "model_name": "model"
    })

    if not {"model", "accuracy"}.issubset(df.columns):
        raise HTTPException(
            status_code=422,
            detail="CSV needs Model and Accuracy columns"
        )

    for column in ["accuracy", "precision", "recall", "f1"]:
        if column not in df.columns:
            df[column] = None
        else:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            )

    df = df.astype(object).where(pd.notnull(df), None)

    return {
        "total_models": len(df),
        "models": df[
            ["model", "accuracy", "precision", "recall", "f1"]
        ].to_dict(orient="records")
    }


@app.get("/api/dataset")
def get_dataset():
    path = find_file(
        "network_flow.csv",
        ["data", "data/raw", "."]
    )

    if path is None:
        raise HTTPException(
            status_code=404,
            detail="network_flow.csv not found"
        )

    # Read the dataset for statistics and a small preview
    df = pd.read_csv(path)

    label_column = next(
        (
            col for col in df.columns
            if col.strip().lower() == "label"
        ),
        None
    )

    distribution = {}

    if label_column:
        distribution = {
            str(k): int(v)
            for k, v in df[label_column]
            .value_counts().items()
        }

    preview = df.head(20).copy()
    preview = preview.astype(object)
    preview = preview.where(pd.notna(preview), None)

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "class_distribution": distribution,
        "preview": preview.to_dict(orient="records")
    }


GRAPHS = {
    "model_accuracy.png",
    "02_model_accuracy.png",
    "model_metrics.png",
    "confusion_matrix.png",
    "ann_loss.png"
}


@app.get("/api/graphs/{filename}")
def get_graph(filename: str):
    if filename not in GRAPHS:
        raise HTTPException(
            status_code=404,
            detail="Unknown graph"
        )

    names = (
        [filename, "02_model_accuracy.png"]
        if filename == "model_accuracy.png"
        else [filename]
    )

    path = None

    for name in names:
        path = find_file(name, ["reports", "."])
        if path is not None:
            break

    if path is None:
        raise HTTPException(
            status_code=404,
            detail="Graph not found"
        )

    return FileResponse(path, media_type="image/png")


@app.get("/api/download/metrics")
def download_metrics():
    path = find_file(
        "model_comparison.csv",
        ["reports", "."]
    )

    if path is None:
        raise HTTPException(
            status_code=404,
            detail="Metrics file not found"
        )

    return FileResponse(
        path,
        media_type="text/csv",
        filename="model_comparison.csv"
    )


# Mount website LAST so /api routes are matched first
app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND), html=True),
    name="frontend"
)
