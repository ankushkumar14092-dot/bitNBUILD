import {dateLabelYear, portData} from './data';

// Use VITE_API_URL environment variable if set (for production split deployment on Vercel/Netlify),
// or fall back to '/api' which works with Vite proxy during local development or reverse proxying.
const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

async function request(path, options) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail || `API request failed (${response.status})`;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return body;
}

export async function getMarketProxy() {
  return request('/ml/market-proxy');
}

export async function getParadipSnapshot() {
  return request('/port-observations/paradip');
}

export async function analyzeWithBackend(form) {
  const port = portData.find(item => item.name === form.destination) || portData[0];
  const volume = Number(form.volume);
  const result = await request('/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      scenario_id: `cargo-${Date.now()}`,
      commodity: form.cargo,
      cargo_volume_tonnes: volume,
      origin: form.origin.split(',').at(-1).trim(),
      destination_port: form.destination,
      laycan_start: form.laycanStart,
      laycan_end: form.laycanEnd,
      target_arrival: form.arrival,
      inventory_tonnes: Number(form.inventory),
      daily_consumption_tonnes: Number(form.consumption),
      safety_buffer_days: 3,
      currency: 'USD',
      freight_rate_per_tonne: 25.4,
      cargo_value: volume * 90,
      insurance_rate: 0.56 / 90,
      port_charge: 118000,
      expected_delay_days: port.wait,
      demurrage_rate_per_day: 35000,
      demurrage_free_days: 1,
    }),
  });

  const feasible = result.vessel_options.filter(option => option.feasible);
  const noFeasible = feasible.length === 0;
  const mapped = result.vessel_options.map(option => {
    const eta = new Date(`${option.estimated_arrival}T00:00:00Z`);
    const laycanStart = new Date(`${option.laycan_start}T00:00:00Z`);
    const laycanEnd = new Date(`${option.laycan_end}T00:00:00Z`);
    return {
      id: option.option_id,
      vessel: option.vessel_class,
      count: Math.ceil(volume / option.capacity_tonnes),
      rate: option.freight_rate_per_tonne,
      freight: option.freight_cost,
      insurance: result.cost.insurance_cost,
      charges: result.cost.port_charges,
      demurrage: result.cost.expected_demurrage,
      total: option.landed_cost,
      eta,
      buffer: option.inventory_buffer_days,
      feasible: option.feasible,
      review: option.review_required || result.decision.human_review_required,
      risk: result.port_risk.risk_level[0] + result.port_risk.risk_level.slice(1).toLowerCase(),
      delay: port.wait,
      window: `${dateLabelYear(laycanStart)} – ${dateLabelYear(laycanEnd)}`,
      confidence: result.confidence,
      port,
      transit: Math.max(0, Math.round((eta - new Date(`${form.laycanStart}T00:00:00Z`)) / 86400000)),
      reason: option.reasons.join('; '),
      noFeasible,
      isRecommended: option.is_recommended,
      source: 'Backend scenario calculations; vessel listing is simulated',
    };
  });
  return {result, options: mapped};
}
