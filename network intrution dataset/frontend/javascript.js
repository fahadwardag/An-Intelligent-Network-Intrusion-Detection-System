
"use strict";

// ========================================
// SECUREGUARD AI - COMPLETE JAVASCRIPT
// ========================================

// FastAPI backend
const API = "/api";

let modelData = [];
let datasetInfo = null;

// ========================================
// 1. HELPER FUNCTIONS
// ========================================

// Format accuracy, precision, recall and F1-score
function formatPercent(value) {
    if (value === null || value === undefined || value === "") {
        return "N/A";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "N/A";
    }

    const percentage = number <= 1 ? number * 100 : number;

    return percentage.toFixed(2) + "%";
}

// Update text in HTML
function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}

// ========================================
// 2. API CONNECTION
// ========================================

async function getJSON(endpoint) {
    const url = `${API}${endpoint}`;

    console.log("Requesting API:", url);

    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Accept": "application/json"
        },
        cache: "no-store"
    });

    if (!response.ok) {
        let detail = response.statusText;

        try {
            const errorData = await response.json();
            detail = errorData.detail || detail;
        } catch (error) {
            // Use the HTTP status if response isn't JSON
        }

        throw new Error(
            `${url}: HTTP ${response.status} - ${detail}`
        );
    }

    return await response.json();
}

// Check whether API is running
async function checkAPI() {
    try {
        await getJSON("/health");
        setText("api-status", "API Connected");
        return true;

    } catch (error) {
        console.error("API Connection Error:", error);
        setText("api-status", "API Error");
        return false;
    }
}

// ========================================
// 3. SIDEBAR NAVIGATION
// ========================================

function initializeNavigation() {
    const navButtons = document.querySelectorAll(".nav-link");

    navButtons.forEach(button => {

        button.addEventListener("click", () => {

            document.querySelectorAll(".nav-link")
                .forEach(nav => nav.classList.remove("active"));

            document.querySelectorAll(".page")
                .forEach(page => page.classList.remove("active"));

            button.classList.add("active");

            const pageId = button.dataset.page;
            const page = document.getElementById(pageId);

            if (page) {
                page.classList.add("active");
            }

            const titles = {
                overview: "Security Overview",
                models: "Model Comparison",
                graphs: "Evaluation Graphs",
                dataset: "Dataset Explorer"
            };

            setText(
                "page-title",
                titles[pageId] || "SecureGuard AI"
            );
        });
    });
}

// ========================================
// 4. DRAW INTERACTIVE BAR CHARTS
// ========================================

function renderBars(containerId, items, percent = true) {
    const container = document.getElementById(containerId);

    if (!container) return;

    container.replaceChildren();

    if (!items || items.length === 0) {
        container.textContent = "No chart data available.";
        return;
    }

    const values = items.map(item => {
        const number = Number(item.value);
        return Number.isFinite(number) ? number : 0;
    });

    const maximum = percent
        ? 100
        : Math.max(...values, 1);

    items.forEach(item => {

        const rawValue = Number(item.value);
        const value = Number.isFinite(rawValue)
            ? rawValue
            : 0;

        const row = document.createElement("div");
        row.className = "bar-item";

        // Model name
        const label = document.createElement("span");
        label.className = "bar-label";
        label.textContent = item.name;
        label.title = item.name;

        // Bar background
        const track = document.createElement("div");
        track.className = "bar-track";

        // Colored bar
        const fill = document.createElement("div");
        fill.className = "bar-fill";

        const normalized = percent && value <= 1
            ? value * 100
            : value;

        const width = Math.min(
            100,
            Math.max(0, normalized / maximum * 100)
        );

        fill.style.width = `${width}%`;

        track.appendChild(fill);

        // Value display
        const number = document.createElement("span");
        number.className = "bar-value";

        number.textContent = percent
            ? formatPercent(item.value)
            : value.toLocaleString();

        row.append(label, track, number);

        container.appendChild(row);
    });
}

// ========================================
// 5. MODEL COMPARISON TABLE
// ========================================

function renderModelTable() {
    const tbody = document.getElementById("model-table");

    if (!tbody) return;

    tbody.replaceChildren();

    if (modelData.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.textContent = "No model results available.";

        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    modelData.forEach(model => {

        const row = document.createElement("tr");

        const values = [
            model.model,
            formatPercent(model.accuracy),
            formatPercent(model.precision),
            formatPercent(model.recall),
            formatPercent(model.f1)
        ];

        values.forEach(value => {

            const td = document.createElement("td");

            td.textContent = value ?? "N/A";

            row.appendChild(td);
        });

        tbody.appendChild(row);
    });
}

// ========================================
// 6. MODEL PERFORMANCE GRAPHS
// ========================================

function renderModelChart(metric = "accuracy") {

    const items = modelData.map(model => ({
        name: model.model,
        value: model[metric]
    }));

    renderBars("comparison-chart", items, true);
}

function initializeMetricSelection() {
    const metricSelect = document.getElementById("metric-select");

    if (!metricSelect) return;

    metricSelect.addEventListener("change", event => {
        renderModelChart(event.target.value);
    });
}

// ========================================
// 7. DATASET EXPLORER
// ========================================

function renderDataset(info) {
    setText(
        "dataset-rows",
        Number(info.total_rows).toLocaleString()
    );

    setText("dataset-columns", info.total_columns);

    const head = document.getElementById("dataset-head");
    const body = document.getElementById("dataset-body");

    if (!head || !body) return;

    head.replaceChildren();
    body.replaceChildren();

    // Table header
    const headerRow = document.createElement("tr");

    info.columns.forEach(column => {
        const th = document.createElement("th");
        th.textContent = column;

        headerRow.appendChild(th);
    });

    head.appendChild(headerRow);

    // Dataset rows
    info.preview.forEach(record => {

        const row = document.createElement("tr");

        info.columns.forEach(column => {

            const td = document.createElement("td");

            const value = record[column];

            td.textContent = value === null ||
                             value === undefined
                ? ""
                : String(value);

            row.appendChild(td);
        });

        body.appendChild(row);
    });
}

// ========================================
// 8. LOAD DASHBOARD DATA
// ========================================

async function loadDashboard() {

    const errorBox = document.getElementById("error-message");
    const apiStatus = document.getElementById("api-status");

    if (errorBox) {
        errorBox.classList.add("hidden");
    }

    if (apiStatus) {
        apiStatus.textContent = "Connecting...";
    }

    try {

        // Load saved results from FastAPI
        const [modelsResponse, dataResponse] = await Promise.all([
            getJSON("/models"),
            getJSON("/dataset")
        ]);

        modelData = modelsResponse.models || [];
        datasetInfo = dataResponse;

        if (modelData.length === 0) {
            throw new Error("No trained model results found.");
        }

        // Find the highest accuracy model
        const validModels = modelData.filter(model => {
            return model.accuracy !== null &&
                   model.accuracy !== undefined &&
                   Number.isFinite(Number(model.accuracy));
        });

        const best = [...validModels].sort((a, b) => {
            return Number(b.accuracy) - Number(a.accuracy);
        })[0];

        // Overview statistics
        setText(
            "total-records",
            Number(dataResponse.total_rows).toLocaleString()
        );

        setText("total-models", modelData.length);

        setText(
            "best-accuracy",
            best ? formatPercent(best.accuracy) : "--"
        );

        setText(
            "best-model",
            best ? best.model : "--"
        );

        // Accuracy comparison graph
        renderBars(
            "overview-chart",
            modelData.map(model => ({
                name: model.model,
                value: model.accuracy
            }))
        );

        // Network traffic distribution
        const distribution = dataResponse.class_distribution || {};

        renderBars(
            "traffic-chart",
            Object.entries(distribution).map(([name, value]) => ({
                name: name,
                value: value
            })),
            false
        );

        // Model comparison
        renderModelTable();

        const metricSelect = document.getElementById("metric-select");

        renderModelChart(
            metricSelect ? metricSelect.value : "accuracy"
        );

        // Dataset preview
        renderDataset(dataResponse);

        // Successfully connected
        if (apiStatus) {
            apiStatus.textContent = "API Connected";
        }

        console.log("SecureGuard AI loaded successfully.");

    } catch (error) {

        console.error("Dashboard Error:", error);

        if (apiStatus) {
            apiStatus.textContent = "API Error";
        }

        if (errorBox) {
            errorBox.textContent =
                "Unable to load dashboard: " + error.message;

            errorBox.classList.remove("hidden");
        }
    }
}

// ========================================
// 9. REFRESH DASHBOARD AND GRAPHS
// ========================================

function refreshDashboard() {

    loadDashboard();

    // Refresh graph images
    document.querySelectorAll(".graphs-grid img")
        .forEach(img => {

            const baseURL = img.src.split("?")[0];

            img.src = `${baseURL}?v=${Date.now()}`;
        });
}

function initializeRefreshButton() {

    const refreshButton = document.getElementById("refresh-btn");

    if (refreshButton) {
        refreshButton.addEventListener(
            "click",
            refreshDashboard
        );
    }
}

// ========================================
// 10. START APPLICATION
// ========================================

document.addEventListener("DOMContentLoaded", async () => {

    console.log("Starting SecureGuard AI...");

    initializeNavigation();
    initializeMetricSelection();
    initializeRefreshButton();

    await checkAPI();

    await loadDashboard();
});
