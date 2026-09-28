# CARGO-PILOT

## Cargo intelligence for freight, chartering and plant supply decisions

**CARGO-PILOT** is a responsive React/Vite decision-support workspace for dry-bulk cargo planning into India's East Coast ports.

It helps a user move through one simple chain:

**Market context → Cargo requirement → Charter options → Landed cost → Port risk → Inventory impact → Decision brief**

The product is intentionally designed to make assumptions visible. It does **not** pretend that sample values are live market intelligence, broker quotes or confirmed operational instructions.

> **Important:** this is a decision-support prototype. A trained Brent crude proxy and an on-demand Paradip Port Authority report reader are connected. Route freight prices, broker vessel listings, AIS tracks, bunker prices, weather and plant systems are not connected; illustrative screens remain labeled as such.

---

## 1. The problem CARGO-PILOT solves

Freight and chartering decisions often become fragmented across spreadsheets, broker messages, port updates and plant-stock calculations. That creates three practical problems:

1. **The commercial decision is separated from the operational decision.**
   A lower freight rate can become unattractive when arrival timing, congestion or demurrage is considered.

2. **Assumptions are difficult to audit.**
   A number may look authoritative even when it is only a scenario input.

3. **Inventory risk appears too late.**
   A vessel may be commercially acceptable but still leave the plant with insufficient stock cover.

CARGO-PILOT combines these views into one workflow so a user can see the relationship between **cost, timing, port conditions and inventory coverage** before taking action.

---

## 2. What the application does

### Overview / Control Tower

The overview gives an executive snapshot of the workspace:

- Freight outlook for 30, 60 or 90 days
- East Coast port scope
- Key market drivers
- Cargo requirements and review state
- Plant stock cover
- Quick charter evaluation

### Freight Forecast

The forecast page demonstrates how a market-intelligence experience can present:

- Historical observations
- Forecast values
- Scenario uncertainty bands
- Trade-lane views
- Market signal tabs
- Optional bunker overlay
- Optional prior-forecast comparison

The route-rate chart remains illustrative. A separately displayed Ridge model forecasts a Brent crude proxy five observations ahead from the local history; it is not a marine bunker or India-route freight forecast.

### Charter Recommendation

A cargo requirement can be evaluated using:

- Cargo type and volume
- Origin and destination
- Laycan start/end
- Required arrival date
- Current inventory
- Daily consumption
- Charter structure

The engine calculates three explicit charter strategies and reports:

- Vessel class
- Vessel count
- Indicative freight rate
- Freight cost
- Insurance
- Port charges
- Projected demurrage
- Total configured landed logistics cost
- ETA
- Inventory buffer
- Arrival feasibility
- Human-review requirement

### Landed Cost

The selected strategy can be inspected line by line. Assumptions are editable so the user can understand **which inputs change the result** rather than receiving a black-box total.

### Port Risk

The port workspace provides:

- Port selection
- Waiting-time proxy
- Anchorage vessel count
- Berth utilization proxy
- Weather signal
- Operational notes
- Scenario-based charter implications
- Locally recorded human-review notes

The East Coast map is schematic and explicitly marked as **not for navigation**.

### Inventory Sync

The inventory workspace connects vessel arrival timing with plant supply:

- Current inventory
- Daily consumption
- Inbound cargo
- Stock-cover calculation
- Stockout projection
- Safety-stock line
- Arrival-buffer warning

### Vessel Market

The vessel screen demonstrates a searchable market workspace with:

- Vessel class
- Capacity
- Open location
- Open date
- Indicative rate
- Vessel profile details

All listings are illustrative.

### Scenario Planning

Users can stress-test a scenario with:

- Bunker price changes
- Additional port delays
- Adjusted landed cost
- Adjusted arrival
- Inventory-buffer impact
- Saved/restored scenarios

Scenarios are stored locally in the browser for the demo.

### Reports

The reporting workspace exports CSV decision-support files for:

- Charter decision briefs
- Landed-cost comparisons
- Cargo requirements

Exports include source/methodology context so the user can distinguish **scenario analysis from verified operational data**.

---

## 3. Core decision logic

The current engine is deliberately transparent and deterministic.

### Vessel capacity

The required number of vessels is calculated as:

```text
vessels required = CEILING(cargo volume / nominal vessel capacity)
```

Nominal capacities currently used by the demo engine are:

- Supramax: 58,000 DWT
- Panamax: 82,000 DWT
- Capesize: 180,000 DWT

Actual vessel suitability must be checked against DWT, draft, stowage, berth limitations, cargo density and operational availability.

### Freight

```text
freight = cargo volume × configured rate × origin factor × fuel factor × cargo factor × charter factor
```

### Insurance

```text
insurance = cargo volume × USD 0.56 / MT
```

### Port charges

```text
port charges = vessels required × USD 118,000 / vessel
```

### Projected demurrage

```text
demurrage = max(waiting days − 1 free day, 0)
            × USD 35,000 / day / vessel
            × vessels required
```

### Total configured landed logistics cost

```text
total = freight + insurance + port charges + projected demurrage
```

This excludes:

- Commodity purchase value
- Duties and taxes
- Inland transportation
- Other unmodeled handling or discharge costs

### Inventory cover

```text
inventory cover = current inventory / daily consumption
```

### Arrival buffer

```text
arrival buffer = inventory cover − days until modeled ETA
```

The recommendation engine first looks for candidates that satisfy the configured arrival/laycan conditions, maintain at least a three-day inventory buffer and avoid high scenario port risk. It then compares total configured cost. Where no fully supported option exists, the UI escalates the situation for human review instead of presenting an unsupported option as executable.

---

## 4. Why the UX is structured this way

CARGO-PILOT follows a **decision-first operations UX** rather than a dashboard-first UX.

The interface is designed around five principles:

### 1. Explain before asking the user to act

The UI shows market context, assumptions and constraints near the decision controls.

### 2. Separate facts from scenarios

Sample data is labeled as illustrative/demo data instead of being presented as live truth.

### 3. Surface operational risk next to commercial cost

A low freight rate is not treated as sufficient by itself. ETA, congestion, demurrage and inventory buffer remain visible.

### 4. Keep human approval explicit

The product generates decision support; it does not silently book vessels, email stakeholders or execute external actions.

### 5. Work across screen sizes

The application uses a responsive layout with:

- Collapsible desktop sidebar
- Mobile navigation drawer
- Mobile bottom navigation
- Responsive tables
- Touch-friendly controls
- Dialog focus management
- Reduced-motion support
- Horizontal table containment instead of page-level overflow

---

## 5. Technical architecture

The codebase is intentionally small and dependency-light.

```text
CARGO-PILOT/
├─ src/
│  ├─ main.jsx        # React app shell, pages, reusable UI and interactions
│  ├─ data.js         # Demo datasets + pure scenario/validation functions
│  ├─ styles.css      # Responsive product design system
│  └─ fonts.css       # Self-hosted font declarations
├─ public/fonts/      # Local font files + licenses
├─ tests/
│  ├─ engine.test.js  # Deterministic business-rule tests
│  └─ workflows.spec.js # Browser workflow tests
├─ index.html         # App shell, metadata and favicon
├─ vite.config.js     # React/Vite build configuration
├─ playwright.config.js # Browser test configuration
├─ package.json
└─ README.md
```

### Application flow

```text
User input
   ↓
Validation
   ↓
Pure charter engine
   ↓
Three strategy results
   ↓
Feasibility + buffer + risk checks
   ↓
Recommendation / review flag
   ↓
Cost + scenario + inventory views
   ↓
CSV decision brief
```

The central calculation path lives in pure functions in `src/data.js`. That makes the most important business rules easy to test without needing a browser.

---

## 6. Engineering hardening included in this version

The CARGO-PILOT refactor includes practical reliability improvements rather than only visual changes.

### Brand consistency

The product identity is consistently **CARGO-PILOT** in:

- Browser title and metadata
- Product shell
- Navigation context
- CSV exports
- Browser storage keys
- Documentation
- Package metadata

### Safer reusable buttons

The shared `Button` component now defaults to:

```html
<button type="button">
```

This prevents unrelated action buttons from accidentally submitting a surrounding form.

Form submission buttons explicitly use:

```html
<button type="submit">
```

### Safer local storage restoration

Stored form/scenario/review values are parsed defensively. Invalid or unexpected JSON falls back to safe defaults instead of turning a corrupted browser state into a render-time exception.

### Stable navigation

Hash navigation is normalized and synchronized with browser history events. Re-selecting the current page also restores the expected page interaction state without relying on a second hash change.

### Memoized decision calculations

Charter analysis is memoized with React `useMemo` so unrelated UI updates do not repeatedly recompute the complete strategy set.

### Clear model boundaries

The application does not quietly turn sample values into claims of live data. Methodology notes, demo labels and export notes make the boundary visible.

### Test-preserving refactor

The existing calculation behavior was retained while the application shell was hardened. The goal is to improve maintainability and UX without changing the meaning of the existing tested rules.

---

## 7. Validation and test coverage

### Engine tests

Run:

```bash
npm run test:engine
```

The current suite verifies:

- Default recommendation behavior
- No-feasible-strategy handling
- Earlier arrival constraints
- Inventory-review logic
- Multi-vessel capacity calculation
- Fuel and delay stress effects
- Input validation
- Forecast horizon behavior

**Current validation result in this delivery: 8/8 engine tests passing.**

### Browser workflow tests

Run:

```bash
npx playwright install --with-deps chromium
npm test
```

The browser suite covers the main user journeys, including:

- Forecast controls
- Cargo filtering and CSV export
- Recommendation generation
- Invalid constraint handling
- Landed-cost recalculation
- Scenario save/restore
- Port review persistence
- Inventory warnings
- Vessel search/profile dialogs
- Notifications
- Profile preferences
- Help/methodology dialogs
- Reports
- Desktop navigation
- Mobile navigation and overflow checks

The intended responsive checkpoints are:

```text
360 px   Mobile
390 px   Mobile workflow test
768 px   Tablet
1024 px  Small desktop/tablet landscape
1440 px  Desktop
```

---

## 8. Run locally

### Requirements

Use a current Node.js LTS release and npm.

### Install

```bash
npm ci
```

### Development

```bash
npm run dev
```

The Vite development server is configured for:

```text
http://localhost:5173
```

### Production build

```bash
npm run build
```

### Preview production build

```bash
npm run preview
```

### Tests

```bash
npm run test:engine
npm test
```

---

## 9. Browser persistence

CARGO-PILOT currently uses browser `localStorage` for the demonstration workspace.

Stored values include:

```text
cargo-pilot-form
cargo-pilot-scenarios
cargo-pilot-port-reviews
cargo-pilot-user
```

This means the demo is **single-browser and local**. Data is not shared between team members and is not a substitute for server-side persistence or an audit trail.

---

## 10. Security and production boundaries

The frontend should be treated as an untrusted client when moving toward production.

Do not put secrets, broker credentials, API keys or privileged credentials into the browser bundle.

A production architecture should use:

```text
Browser
  ↓
Authenticated application gateway
  ↓
Application/API layer
  ↓
Verified freight / vessel / port / weather / plant services
  ↓
Versioned data + audit storage
```

Recommended production controls include:

- SSO / authenticated roles
- Server-side authorization
- Server-side input validation
- Shared persistence
- Audit logs
- Observability and error reporting
- Rate limiting
- Data-source freshness tracking
- Versioned forecasting models
- Broker/operations approval workflows
- Explicit data lineage for every decision output

---

## 11. What is intentionally not connected

This prototype does not currently perform:

- Live freight-rate retrieval
- AIS vessel tracking
- Live broker availability checks
- Live bunker-price retrieval
- Live weather ingestion
- Port authority feeds outside the Paradip daily snapshot endpoint
- Plant ERP integration
- Vessel booking
- Email or external review assignment
- Authentication or SSO
- Server-side scenario storage

Those boundaries are intentional so the demo remains safe, inspectable and reproducible.

---

## 12. Suggested production evolution

A practical next architecture would evolve in these stages:

### Phase 1 — Frontend foundation

Keep the current CARGO-PILOT interaction model, but split large UI modules into feature folders and add a shared component layer.

### Phase 2 — API integration

Introduce typed same-origin `/api/...` endpoints for verified freight, vessels, port operations and plant inventory.

### Phase 3 — Data quality and lineage

Attach timestamp, source, freshness, confidence methodology and validation state to every external data point.

### Phase 4 — Decision governance

Add approvals, named reviewers, immutable scenario snapshots and audit history.

### Phase 5 — Forecasting platform

Replace deterministic demonstration series with a versioned forecasting service that can be evaluated against historical backtests and monitored for drift.

---

## 13. Design language

CARGO-PILOT uses a restrained operations-focused visual language:

- Deep navy for trust and navigation
- Muted teal for active/positive operational states
- Amber for attention and scenario warnings
- Red for blocking or elevated risk
- Warm neutral surfaces to reduce dashboard fatigue
- Compact data typography with generous spacing around decisions
- Rounded cards with clear hierarchy rather than heavy visual effects

The design goal is to feel like a modern **chartering operations control room**, not a generic analytics template.

---

## 14. Data honesty checklist

Before treating this prototype as an operational system, replace every illustrative source with a verified source and preserve the distinction between:

```text
OBSERVED DATA       → what a system actually received
SCENARIO ASSUMPTION  → what the user configured
MODEL OUTPUT        → what the calculation/forecast produced
HUMAN DECISION       → what an authorized person approved
```

That separation is one of the core product principles of CARGO-PILOT.

---

## 15. Current delivery status

### Verified in this delivery

- CARGO-PILOT branding hardened across the project
- Shared button behavior hardened
- Local-storage parsing hardened
- Navigation handling hardened
- Charter analysis memoized
- Existing engine behavior preserved
- **8/8 engine tests pass**

### Environment limitation

A full Vite/browser verification requires the project dependencies to be installed in the execution environment. The supplied sandbox copy did not have the Vite/Playwright executables available, and dependency installation timed out in the sandbox. Therefore this delivery does **not** claim that the browser build/test suite was executed successfully here.

Run the following locally after installation:

```bash
npm ci
npm run build
npm run test:engine
npm test
```

That sequence is the final acceptance check before treating the build as release-ready.

---

### Local API, trained market proxy and port snapshot

The charter form posts to the FastAPI service. The dashboard loads a locally trained Brent crude proxy, and the Paradip endpoint reads the latest daily traffic PDF listed by the Port Authority. Training code and artifacts are kept in `ml/models/`; source data stays in `ml/data/`.

Install and start the API in one terminal:

```bash
python3.13 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm run dev:api
```

To retrain the proxy, open `ml/models/freight_forecast_training.ipynb` in Jupyter and run all cells. The notebook reads the CSV from `ml/data/` and writes the model and evaluation JSON beside itself in `ml/models/`.

Start the frontend in another terminal:

```bash
npm ci
npm run dev
```

Vite proxies `/api/*` to `http://127.0.0.1:8000`. The API exposes `POST /analyze`, `GET /ml/market-proxy`, and `GET /port-observations/paradip`. The market proxy reports a five-business-day Brent estimate and chronological holdout comparison against persistence. The September 2026 local history yielded a small RMSE improvement; it is not recommended for decision use. Paradip reports provide a current anchorage snapshot, which is a vessel count and not AIS tracking, waiting-time prediction, or demurrage risk. Both endpoints fail clearly when their source is unavailable.

The historical BDI model artifact is retained for reference but its inference is disabled: its source history ends in 2009 and its prior evaluation did not beat persistence. No licensed India-route freight history, marine bunker series, or port-delay outcome labels are included. Do not treat the crude proxy or simulated charter values as a freight forecast or quote.

The backend vessel options remain simulated fixtures, and its current route-fit rule only supports Australia → Paradip; other routes return no feasible vessel option. The charter endpoint uses explicit configured scenario inputs for freight, insurance, port charges, and delay; verify these assumptions before using the result.

## CARGO-PILOT in one sentence

> **CARGO-PILOT turns freight market context and cargo constraints into transparent charter options, landed-cost comparisons and inventory-aware decision support — while keeping assumptions and human approval visible.**
