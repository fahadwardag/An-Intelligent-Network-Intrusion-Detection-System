
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SecureGuard AI | Intrusion Detection",
    page_icon="🛡️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

# Find files in reports/, data/, or the main project folder
def locate_file(name, folders):
    for folder in folders:
        path = BASE_DIR / folder / name if folder else BASE_DIR / name
        if path.is_file():
            return path
    return None

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

# Dashboard styling
st.markdown("""
<style>
.block-container {
    padding-top: 1.6rem;
    max-width: 1250px;
}
h1, h2, h3 {
    letter-spacing: -0.025em;
}
[data-testid="stMetric"] {
    background: rgba(120,120,120,.08);
    padding: 1rem;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SecureGuard AI")
st.caption(
    "Network Intrusion Detection | "
    "Machine Learning & Deep Learning Portfolio"
)

st.info(
    "Educational prototype trained on synthetic network data. "
    "Not a live security monitoring system."
)

# Load model comparison results
metrics_path = locate_file(
    "model_comparison.csv",
    ["reports", ""]
)

if metrics_path is None:
    st.error(
        "model_comparison.csv not found. "
        "Place it inside reports/ or next to dashboard.py."
    )
    st.code(str(BASE_DIR))
    st.stop()

metrics = load_csv(str(metrics_path)).copy()

# Correct capitalization differences in CSV column names
metrics.columns = (
    metrics.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

metrics = metrics.rename(columns={
    "f1-score": "f1",
    "f1_score": "f1",
    "model_name": "model"
})

if not {"model", "accuracy"}.issubset(metrics.columns):
    st.error(
        f"Required columns: model and accuracy. "
        f"Found: {metrics.columns.tolist()}"
    )
    st.stop()

for col in ["accuracy", "precision", "recall", "f1"]:
    if col in metrics.columns:
        metrics[col] = pd.to_numeric(
            metrics[col], errors="coerce"
        )

metrics = metrics.dropna(subset=["accuracy"])

if metrics.empty:
    st.error("No valid model accuracy scores found.")
    st.stop()

# Sidebar navigation
st.sidebar.header("Project Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Overview",
        "Model Comparison",
        "Evaluation Graphs",
        "Dataset Explorer"
    ]
)

st.sidebar.divider()
st.sidebar.caption(
    "Results are loaded from your saved CSV and PNG files."
)

# -----------------------
# PAGE 1: OVERVIEW
# -----------------------
if page == "Overview":

    st.header("Security Model Overview")

    best = metrics.loc[metrics["accuracy"].idxmax()]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Models Evaluated",
        len(metrics)
    )

    accuracy = best["accuracy"]

    if accuracy <= 1:
        accuracy_text = f"{accuracy:.2%}"
    else:
        accuracy_text = f"{accuracy:.2f}%"

    col2.metric(
        "Highest Accuracy",
        accuracy_text
    )

    col3.metric(
        "Highest-Accuracy Model",
        str(best["model"])
    )

    st.subheader("Project Description")

    st.write("""
    SecureGuard AI compares Machine Learning and
    Deep Learning models for detecting network
    intrusion patterns.

    Attack categories include:
    - BENIGN
    - DDoS
    - PortScan
    - BruteForce
    """)

    st.subheader("Model Accuracy")

    st.bar_chart(
        metrics.set_index("model")["accuracy"]
    )

    st.caption(
        "Scores are based on synthetic data, "
        "not real-world security performance."
    )

# -----------------------
# PAGE 2: MODEL COMPARISON
# -----------------------
elif page == "Model Comparison":

    st.header("Machine Learning Model Comparison")

    st.dataframe(
        metrics,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Accuracy Comparison")

    st.bar_chart(
        metrics.set_index("model")["accuracy"]
    )

    available = [
        col for col in ["precision", "recall", "f1"]
        if col in metrics.columns
    ]

    if available:
        st.subheader(
            "Precision, Recall and F1-score Comparison"
        )

        st.bar_chart(
            metrics.set_index("model")[available]
        )

    st.caption(
        "Accuracy alone does not prove reliable "
        "attack detection. Also examine per-class recall."
    )

# -----------------------
# PAGE 3: GRAPHS
# -----------------------
elif page == "Evaluation Graphs":

    st.header("Model Evaluation Graphs")

    graph_files = [
        (
            "Model Accuracy",
            ["model_accuracy.png", "02_model_accuracy.png"]
        ),
        (
            "Precision, Recall and F1-score",
            ["model_metrics.png"]
        ),
        (
            "Confusion Matrix",
            ["confusion_matrix.png"]
        ),
        (
            "ANN Training Loss",
            ["ann_loss.png"]
        )
    ]

    for title, filenames in graph_files:

        st.subheader(title)

        graph_path = None

        for filename in filenames:
            graph_path = locate_file(
                filename, ["reports", ""]
            )

            if graph_path is not None:
                break

        if graph_path is not None:
            st.image(
                str(graph_path),
                use_container_width=True
            )
        else:
            st.warning(
                f"Graph not found: {', '.join(filenames)}"
            )

# -----------------------
# PAGE 4: DATASET
# -----------------------
elif page == "Dataset Explorer":

    st.header("Network Traffic Dataset")

    data_path = locate_file(
        "network_flow.csv",
        ["data", "data/raw", ""]
    )

    if data_path is None:
        st.warning("network_flow.csv not found.")

    else:
        df = load_csv(str(data_path))

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Records",
            f"{len(df):,}"
        )

        col2.metric(
            "Total Features/Columns",
            len(df.columns)
        )

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(100),
            use_container_width=True
        )

        label_col = next(
            (
                col for col in df.columns
                if col.strip().lower() == "label"
            ),
            None
        )

        if label_col:
            st.subheader("Attack Distribution")

            st.bar_chart(
                df[label_col].value_counts()
            )

        st.caption(
            "Showing the first 100 records "
            "from the synthetic dataset."
        )

st.divider()

st.caption(
    "SecureGuard AI | ML & DL Intrusion Detection | "
    "Portfolio Demonstration"
)
