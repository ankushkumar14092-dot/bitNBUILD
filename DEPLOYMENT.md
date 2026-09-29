# 🚀 CARGO-PILOT Deployment Guide (Vercel & Render)

This project is configured for deployment using:
- **Backend (FastAPI + ML Engine)**: Hosted on **Render** as a Python Web Service.
- **Frontend (React + Vite)**: Hosted on **Vercel** with global edge CDN and automatic SPA routing.

---

## 📋 Architecture Overview

```
                        +----------------------------+
                        |        User Browser        |
                        +--------------+-------------+
                                       |
                 +---------------------+---------------------+
                 |                                           |
                 v (Static Assets / HTML)                    v (REST API Calls)
      +----------------------+                    +----------------------+
      |   Frontend (Vercel)  |                    |   Backend (Render)   |
      | https://...vercel.app|                    | https://...onrender  |
      +----------------------+                    +----------+-----------+
                                                             |
                                                  +----------v-----------+
                                                  |   ML Models & Data   |
                                                  |  (Scikit-Learn, PDF) |
                                                  +----------------------+
```

---

## 🛠️ Step 1: Deploy Backend to Render

> [!IMPORTANT]
> Deploy the **Backend first** so you have its live URL (e.g. `https://cargo-pilot-backend.onrender.com`) before building the frontend.

### Method A: Using the Render Blueprint (`render.yaml`) — 1-Click Setup
1. Log in to [Render](https://dashboard.render.com).
2. Click **New +** ➔ **Blueprint**.
3. Select your GitHub repository (`bitNBUILD`).
4. Render will automatically read [`render.yaml`](./render.yaml), configure Python 3.11, and start the service with:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **Apply**.

### Method B: Manual Web Service Setup on Render
1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** ➔ **Web Service** and connect your GitHub repository.
3. Configure settings:
   - **Name**: `cargo-pilot-backend` (or any preferred name)
   - **Region**: Closest to your users (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Root Directory**: *(Leave empty)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Expand **Advanced** and add Environment Variables:
   - `PYTHON_VERSION`: `3.11.9`
   - `ALLOWED_ORIGINS`: `*` *(or your Vercel URL once known)*
5. Click **Create Web Service**.
6. Once deployed, copy your backend URL (e.g. `https://cargo-pilot-backend.onrender.com`).
7. Verify in your browser:
   `https://cargo-pilot-backend.onrender.com/health` ➔ returns `{"status":"ok"}`.

---

## 🎨 Step 2: Deploy Frontend to Vercel

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** ➔ **Project**.
3. Import your GitHub repository (`bitNBUILD`).
4. In the **Configure Project** screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select **`frontend`** *(Critical step!)*
   - **Build Command**: `npm run build` *(auto-detected)*
   - **Output Directory**: `dist` *(auto-detected)*
5. Expand **Environment Variables** and add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://cargo-pilot-backend.onrender.com` *(your Render backend URL without trailing slash)*
6. Click **Deploy**.
7. Vercel will build and assign your production domain (e.g. `https://cargo-pilot.vercel.app`).

> [!TIP]
> The included [`frontend/vercel.json`](./frontend/vercel.json) automatically configures SPA routing to prevent 404 errors on page refreshes.

---

## 🔒 Step 3: Production CORS Hardening (Optional)

By default, the backend allows requests from `*` and any `*.vercel.app` domain.

To restrict API access exclusively to your own Vercel domain:
1. In your **Render Dashboard** ➔ go to your Web Service ➔ **Environment**.
2. Update `ALLOWED_ORIGINS`:
   ```env
   ALLOWED_ORIGINS=https://cargo-pilot.vercel.app
   ```
3. Save changes (Render will automatically redeploy with the restricted CORS rule).

---

## 🧪 Step 4: Verification Checklist

| Test Item | URL / Action | Expected Result |
| :--- | :--- | :--- |
| **Backend Health** | `https://<backend>.onrender.com/health` | `{"status": "ok"}` |
| **Market Proxy** | `https://<backend>.onrender.com/ml/market-proxy` | JSON response with forecast metrics |
| **Port Observation** | `https://<backend>.onrender.com/port-observations/paradip` | JSON response with official dry-bulk queue |
| **Frontend UI** | `https://<frontend>.vercel.app` | Dashboard loads with KPIs and control towers |
| **Scenario Run** | In UI, click **Evaluate Charter Options** | Network tab shows `POST` to Render `/analyze` returning `200 OK` |

---

## 🔍 Troubleshooting & FAQ

### 1. "Failed to fetch" or Network Errors
- Ensure `VITE_API_URL` in Vercel has **no trailing slash** (e.g., `https://backend.onrender.com`, NOT `https://backend.onrender.com/`).
- Whenever you update environment variables in Vercel, trigger a **Redeploy** so Vite injects the new variable into the built bundle.

### 2. Render Free Tier Spin-Down (Cold Starts)
- On Render's Free tier, the service spins down after 15 minutes of inactivity.
- The first request after sleep takes ~30–50 seconds to boot up. Subsequent requests respond immediately.
