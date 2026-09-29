<div align="center">
  <h1>🚢 CARGO-PILOT</h1>
  <p><strong>Cargo intelligence for freight, chartering and plant supply decisions</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React Vite" />
    <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit Learn" />
  </p>

  > *CARGO-PILOT turns freight market context and cargo constraints into transparent charter options, landed-cost comparisons and inventory-aware decision support — while keeping assumptions and human approval visible.*
</div>

---

## 📖 Overview

**CARGO-PILOT** is a responsive decision-support workspace designed for dry-bulk cargo planning into India's East Coast ports (Paradip, Visakhapatnam, Kolkata/Haldia, Chennai). It streamlines the entire procurement lifecycle into one cohesive flow:

<div align="center">

`Market context` ➔ `Cargo requirement` ➔ `Charter options` ➔ `Landed cost` ➔ `Port risk` ➔ `Inventory impact` ➔ `Decision brief`

</div>

### The Problem We Solve
Freight and chartering decisions are often fragmented across spreadsheets, emails, and isolated portals. This fragmentation leads to:
1. **Commercial & Operational Disconnect:** A cheap freight rate can backfire if port congestion or demurrage ruins the bottom line.
2. **Hidden Assumptions:** It's difficult to audit whether a number is a live quote or a scenario assumption.
3. **Inventory Risk:** A commercially viable vessel might arrive too late, causing plant stockouts.

**CARGO-PILOT solves this** by bringing cost, timing, port conditions, and inventory coverage into a single pane of glass.

---

## 🌟 Key Features

* 📊 **Control Tower Overview:** 30/60/90-day freight outlook, market drivers, and plant stock cover.
* 📈 **Freight Forecast Proxy:** Demonstrates forecasting with historical observations, scenario bands, and ML (trained Brent crude proxy).
* 🚢 **Charter Recommendation Engine:** Evaluates cargo origin, destination, volume, and laycan to suggest vessel strategies (e.g., Panamax, Supramax, Capesize).
* 💰 **Landed Cost Calculator:** Calculates explicit logistics costs (freight + insurance + port charges + projected demurrage).
* ⚠️ **Port Risk Assessment:** Wait-time proxies, berth utilization, weather signals, and operational notes.
* 🏭 **Inventory Sync:** Connects vessel ETA with plant daily consumption to predict stockouts and arrival buffers.
* 🔀 **Scenario Planning:** Stress-test changes in bunker fuel prices and port delays locally.
* 📑 **Reporting:** Export decision briefs, landed-cost comparisons, and cargo requirements to CSV.

---

## 🏗️ Technical Architecture

The project has been refactored into a modern, modular structure:

```text
CARGO-PILOT/
├── frontend/                  # React + Vite UI Dashboard
├── backend/                   # FastAPI server & decision logic
├── ml/                        # Jupyter notebooks, trained models, data
├── tests/                     # Separated UI (Playwright) and API (Pytest) tests
├── DEPLOYMENT.md              # Production deployment guide (Vercel + Render)
├── architecture.md            # Detailed end-to-end architecture documentation
└── documentation.md           # Project status, constraints, and data info
```

> **Important Note:** This is a decision-support **prototype**. ML models (like the Brent crude proxy) and port reports are for demonstration. Live broker quotes, real AIS tracks, and live ERP data are not connected.

---

## 🌐 Production Deployment

Ready to host CARGO-PILOT online? Follow the complete step-by-step guide in [**`DEPLOYMENT.md`**](./DEPLOYMENT.md):
* **Frontend**: Deploy to **Vercel** with automatic SPA rewrites and environment-based backend targeting.
* **Backend**: Deploy to **Render** using pre-configured `render.yaml` or direct Web Service setup.

---

## 🚀 Getting Started

Follow these steps to run the complete stack locally.

### 1. Backend (FastAPI)
The backend powers the charter calculations and connects to the ML forecasting models.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

# Start the API server on http://localhost:8000
fastapi dev main.py
```

### 2. Frontend (React/Vite)
Open a new terminal to start the UI.

```bash
cd frontend
npm install

# Start the Vite dev server on http://localhost:5173
npm run dev
```

### 3. Machine Learning (Jupyter)
To explore or retrain the market proxy models:

```bash
cd ml
pip install -r requirements.txt
jupyter notebook freight_forecast_training.ipynb
```

---

## 🧪 Testing

The logic and UI flows are rigorously tested.

```bash
# Run deterministic backend calculations tests
cd tests/backend
pytest

# Run frontend engine tests
cd frontend
npm run test:engine

# Run browser workflow (Playwright) tests
npm test
```

---

## 🎨 Design Philosophy

CARGO-PILOT embraces a **decision-first operations UX**:
* **Explain before asking:** Context is shown near controls.
* **Facts vs. Scenarios:** Assumptions are explicitly labeled.
* **Risk + Cost:** Congestion and ETA are side-by-side with freight costs.
* **Human in the Loop:** System flags risky scenarios for "Human Review".
* **Operations Visuals:** Deep navy and muted teals to reduce dashboard fatigue.

---

## 🔒 Security & Next Steps

This prototype uses `localStorage` and local files. For a production deployment, the architecture should evolve to include:
* Authenticated gateways (SSO)
* PostgreSQL for persistent scenario and audit storage
* Live APIs for verified AIS and broker quotes
* Versioned ML model deployments

Please refer to [`architecture.md`](./architecture.md) and [`documentation.md`](./documentation.md) for an in-depth view of the long-term production roadmap and ML constraints.
