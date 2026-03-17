# API CONTRACT MAP — PHASE F0

## Backend Contract Audit
**Generated**: 2026-03-15
**Status**: READY FOR FRONTEND INTEGRATION

---

## 1. RESEARCH CONTRACTS

### 1.1 Full Chart Analysis (PRIMARY)
```
GET /api/v1/chart/full-analysis/{symbol}/{timeframe}
```
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "candles": [...],
  "volume": [...],
  "indicators": [...],
  "patterns": [...],
  "support_resistance": [...],
  "liquidity_zones": [...],
  "hypothesis": {
    "hypothesis_id": "...",
    "direction": "bullish",
    "confidence": 0.78,
    "scenarios": [...],
    "paths": [...]
  },
  "fractal_matches": [...],
  "market_regime": "TRENDING_UP",
  "capital_flow_bias": "bullish",
  "preset": {...}
}
```
**Frontend Binding:** Research Overview, Chart Lab

---

### 1.2 Research Full Payload
```
GET /api/v1/research-analytics/full-payload/{symbol}/{timeframe}
```
**Params:** `include_indicators`, `include_patterns`, `include_hypothesis`, `include_fractals`
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "candles": [...],
  "volume": [...],
  "regime": "TRENDING_UP",
  "suggested_indicators": [...],
  "suggested_overlays": [...],
  "indicators": [...],
  "patterns": [...],
  "support_resistance": [...],
  "hypothesis": {...},
  "fractal_matches": [...]
}
```
**Frontend Binding:** Research Overview

---

### 1.3 Chart Presets
```
GET /api/v1/chart/presets
GET /api/v1/chart/preset/{preset_id}
GET /api/v1/research-analytics/suggestions/{symbol}/{timeframe}
```
**Frontend Binding:** Chart Lab (preset selector)

---

## 2. HYPOTHESIS CONTRACTS

### 2.1 Hypothesis List
```
GET /api/hypothesis/list
```
**Params:** `status`, `category`
**Payload:**
```json
{
  "count": 15,
  "hypotheses": [
    {
      "hypothesis_id": "...",
      "name": "Bullish Continuation",
      "category": "DIRECTIONAL",
      "status": "ACTIVE",
      "description": "...",
      "conditions": [...],
      "expected_outcome": {...},
      "applicable_regimes": ["TREND_UP"],
      "applicable_timeframes": ["1h", "4h"],
      "applicable_symbols": ["BTC", "ETH"]
    }
  ]
}
```
**Frontend Binding:** Hypotheses Screen

---

### 2.2 Hypothesis Detail
```
GET /api/hypothesis/{hypothesis_id}
```
**Payload:**
```json
{
  "hypothesis": {
    "hypothesis_id": "...",
    "name": "...",
    "category": "DIRECTIONAL",
    "status": "ACTIVE",
    "conditions": [...],
    "expected_outcome": {
      "direction": "UP",
      "target_move_pct": 5.0,
      "time_horizon_candles": 24,
      "confidence": 0.75
    }
  }
}
```
**Frontend Binding:** Hypotheses Screen (expanded card)

---

### 2.3 Top Hypotheses
```
GET /api/hypothesis/top
```
**Params:** `limit`
**Payload:**
```json
{
  "count": 10,
  "top_hypotheses": [
    {
      "hypothesis_id": "...",
      "name": "...",
      "win_rate": 0.68,
      "profit_factor": 1.85,
      "sample_size": 125
    }
  ]
}
```
**Frontend Binding:** Hypotheses Screen (top hypothesis)

---

### 2.4 Hypothesis Registry
```
GET /api/hypothesis/registry
```
**Payload:**
```json
{
  "total": 15,
  "stats": {...},
  "categories": ["DIRECTIONAL", "REVERSAL", "MOMENTUM", ...],
  "statuses": ["DRAFT", "ACTIVE", "TESTING", ...],
  "hypotheses": [...]
}
```
**Frontend Binding:** Hypotheses Screen

---

## 3. SIGNAL CONTRACTS

### 3.1 Signal Explanation
```
GET /api/v1/signal/explanation/{symbol}/{timeframe}
```
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "direction": "bullish",
  "confidence": 0.78,
  "strength": "STRONG",
  "summary": "Strong momentum continuation with volume breakout...",
  "drivers": [
    {
      "name": "Volume Breakout",
      "contribution": 0.35,
      "driver_type": "MOMENTUM",
      "description": "Volume breakout above 20-day average"
    }
  ],
  "conflicts": [
    {
      "name": "RSI Overbought",
      "severity": "LOW",
      "description": "RSI approaching overbought"
    }
  ]
}
```
**Frontend Binding:** Research Overview (Signal Explanation panel)

---

### 3.2 Signal Drivers
```
GET /api/v1/signal/drivers/{symbol}/{timeframe}
```
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "direction": "bullish",
  "confidence": 0.78,
  "strength": "STRONG",
  "drivers": [
    {"name": "Volume Breakout", "contribution": 0.35, "type": "MOMENTUM"}
  ],
  "conflicts": [
    {"name": "RSI Overbought", "severity": "LOW"}
  ],
  "summary": "..."
}
```
**Frontend Binding:** Research Overview (Drivers list)

---

## 4. FRACTAL CONTRACTS

### 4.1 Fractal State
```
GET /api/v1/fractal/state/{symbol}
```
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe_states": {
    "5m": "TREND_UP",
    "15m": "TREND_UP",
    "1h": "RANGE",
    "4h": "TREND_UP",
    "1d": "TREND_UP"
  },
  "fractal_metrics": {
    "alignment": 0.82,
    "bias": "BULLISH",
    "confidence": 0.75,
    "volatility_consistency": 0.68
  },
  "modifiers": {...}
}
```
**Frontend Binding:** Research Overview (Fractal Match panel)

---

### 4.2 Fractal Summary
```
GET /api/v1/fractal/summary/{symbol}
```
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "current": {
    "alignment": 0.82,
    "bias": "BULLISH",
    "confidence": 0.75
  },
  "state_distribution": {
    "trend_up": 3,
    "trend_down": 0,
    "range": 2,
    "volatile": 0
  },
  "historical": {...}
}
```
**Frontend Binding:** Research Overview

---

### 4.3 Fractal Matches (Chart)
```
GET /api/v1/research-analytics/fractal-matches/{symbol}/{timeframe}
```
**Params:** `min_similarity`, `limit`
**Payload:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "matches": [
    {
      "match_id": "...",
      "historical_period": "2024-Q1",
      "similarity": 0.85,
      "outcome": "UP",
      "outcome_pct": 12.5,
      "projection_path": [...]
    }
  ]
}
```
**Frontend Binding:** Chart Lab (fractal projections)

---

## 5. CAPITAL FLOW CONTRACTS

### 5.1 Capital Flow Summary
```
GET /api/v1/capital-flow/summary
```
**Payload:**
```json
{
  "status": "ok",
  "phase": "42.4",
  "snapshot": {
    "btc_flow_score": 0.65,
    "eth_flow_score": 0.45,
    "alt_flow_score": 0.30,
    "cash_flow_score": -0.40,
    "flow_state": "RISK_ON"
  },
  "rotation": {
    "rotation_type": "RISK_ON",
    "from_bucket": "CASH",
    "to_bucket": "BTC",
    "rotation_strength": 0.72,
    "confidence": 0.68
  },
  "score": {
    "flow_bias": "BULLISH",
    "flow_strength": 0.65,
    "flow_confidence": 0.70
  }
}
```
**Frontend Binding:** Research Overview (Capital Flow panel)

---

### 5.2 Capital Flow Rotation
```
GET /api/v1/capital-flow/rotation
```
**Frontend Binding:** Research Overview

---

## 6. PORTFOLIO CONTRACTS

### 6.1 Portfolio State
```
GET /api/v1/portfolio/state
```
**Payload:**
```json
{
  "portfolio_id": "...",
  "total_capital": 100000,
  "allocated_capital": 40000,
  "available_capital": 60000,
  "positions": [...],
  "targets": [...],
  "exposure": {...},
  "risk": {...},
  "diversification_score": 0.72
}
```
**Frontend Binding:** Trading Terminal (Portfolio tab)

---

### 6.2 Portfolio Positions
```
GET /api/v1/portfolio/positions
```
**Payload:**
```json
[
  {
    "symbol": "BTCUSDT",
    "direction": "LONG",
    "size_usd": 25000,
    "entry_price": 67000,
    "current_price": 67500,
    "unrealized_pnl_usd": 185.82,
    "unrealized_pnl_percent": 0.74,
    "risk_contribution": 0.35,
    "correlation_penalty": 0.0
  }
]
```
**Frontend Binding:** Trading Terminal (Positions table)

---

### 6.3 Portfolio Exposure
```
GET /api/v1/portfolio/exposure
```
**Payload:**
```json
{
  "long_exposure": 0.40,
  "short_exposure": 0.10,
  "net_exposure": 0.30,
  "gross_exposure": 0.50,
  "available_long_capacity": 0.30,
  "available_short_capacity": 0.20,
  "exposure_by_symbol": {...}
}
```
**Frontend Binding:** Trading Terminal (Portfolio tab)

---

### 6.4 Portfolio Risk
```
GET /api/v1/portfolio/risk
```
**Payload:**
```json
{
  "portfolio_variance": 0.0025,
  "portfolio_volatility": 0.05,
  "risk_level": "MODERATE",
  "var_95": 3200,
  "var_99": 4500,
  "risk_contribution": {...}
}
```
**Frontend Binding:** Trading Terminal (Risk tab)

---

## 7. EXECUTION CONTRACTS

### 7.1 Execution Plan
```
GET /api/v1/execution/plan/{symbol}
```
**Params:** `hypothesis_type`, `direction`, `confidence`, `reliability`, `portfolio_capital`, `allocation_weight`
**Payload:**
```json
{
  "status": "ok",
  "symbol": "BTCUSDT",
  "strategy": "MOMENTUM",
  "direction": "LONG",
  "position_size_usd": 10000,
  "position_size_adjusted": 9500,
  "entry_price": 67000,
  "stop_loss": 65500,
  "take_profit": 70000,
  "risk_level": "MEDIUM",
  "risk_reward_ratio": 2.0,
  "execution_type": "LIMIT",
  "confidence": 0.75,
  "plan_status": "APPROVED",
  "blocked_reason": null
}
```
**Frontend Binding:** Trading Terminal (Execution tab)

---

### 7.2 Execution History
```
GET /api/v1/execution/history/{symbol}
```
**Frontend Binding:** Trading Terminal (History tab)

---

### 7.3 Active Execution Plan
```
GET /api/v1/execution/active/{symbol}
```
**Frontend Binding:** Trading Terminal (Overview)

---

### 7.4 Execute Plan
```
POST /api/v1/execution/execute/{symbol}
```
**Frontend Binding:** Trading Terminal (Approve action)

---

## 8. SYSTEM CONTROL CONTRACTS

### 8.1 Cockpit State
```
GET /api/v1/control/state/{symbol}
```
**Payload:**
```json
{
  "status": "ok",
  "symbol": "BTCUSDT",
  "decision": {
    "market_state": "TRENDING",
    "dominant_scenario": "CONTINUATION",
    "recommended_strategy": "MOMENTUM",
    "recommended_direction": "LONG",
    "confidence": 0.78
  },
  "risk": {
    "risk_level": "MODERATE",
    "risk_score": 0.45,
    "max_allowed_position": 0.10,
    "stress_indicator": 0.25
  },
  "alerts": {
    "active_count": 2,
    "alerts": [...]
  },
  "intelligence": {
    "top_hypothesis": "...",
    "alpha_score": 0.72
  }
}
```
**Frontend Binding:** System Control (Overview)

---

### 8.2 Control Summary (Multi-symbol)
```
GET /api/v1/control/summary
```
**Params:** `symbols` (comma-separated)
**Payload:**
```json
{
  "status": "ok",
  "symbols_monitored": 3,
  "alerts": {
    "total": 5,
    "critical": 1
  },
  "risk_overview": {
    "high_risk": ["SOL"],
    "extreme_risk": []
  },
  "opportunities": ["BTC"],
  "system_status": "OPERATIONAL"
}
```
**Frontend Binding:** System Control (Overview)

---

### 8.3 Risk State
```
GET /api/v1/control/risk/{symbol}
```
**Frontend Binding:** System Control (Metrics tab)

---

### 8.4 Alerts
```
GET /api/v1/control/alerts/{symbol}
```
**Frontend Binding:** System Control (Alerts)

---

## 9. PATTERNS & INDICATORS

### 9.1 Patterns
```
GET /api/v1/research-analytics/patterns/{symbol}/{timeframe}
```
**Frontend Binding:** Chart Lab

---

### 9.2 Support/Resistance
```
GET /api/v1/research-analytics/support-resistance/{symbol}/{timeframe}
```
**Frontend Binding:** Chart Lab

---

### 9.3 Liquidity Zones
```
GET /api/v1/research-analytics/liquidity-zones/{symbol}/{timeframe}
```
**Frontend Binding:** Chart Lab

---

### 9.4 Indicators
```
POST /api/v1/research-analytics/indicators/{symbol}/{timeframe}
GET /api/v1/research-analytics/indicator/{name}/{symbol}/{timeframe}
```
**Frontend Binding:** Chart Lab

---

## 10. UI BINDINGS SUMMARY

### Research Overview
| Component | Endpoint |
|-----------|----------|
| Market Regime | `/chart/full-analysis` → `market_regime` |
| Capital Flow | `/capital-flow/summary` |
| Fractal Match | `/fractal/summary` |
| Signal Explanation | `/signal/explanation` |
| Top Hypothesis | `/hypothesis/top` |

### Chart Lab
| Component | Endpoint |
|-----------|----------|
| Candles | `/chart/full-analysis` → `candles` |
| Indicators | `/chart/full-analysis` → `indicators` |
| Patterns | `/chart/full-analysis` → `patterns` |
| S/R Levels | `/chart/full-analysis` → `support_resistance` |
| Hypothesis Paths | `/chart/full-analysis` → `hypothesis.paths` |
| Fractal Projections | `/research-analytics/fractal-matches` |
| Preset Selector | `/chart/presets` |

### Hypotheses Screen
| Component | Endpoint |
|-----------|----------|
| Hypothesis List | `/hypothesis/list` |
| Top Hypothesis | `/hypothesis/top` |
| Hypothesis Detail | `/hypothesis/{id}` |

### Trading Terminal
| Component | Endpoint |
|-----------|----------|
| Portfolio Metrics | `/portfolio/state` |
| Positions | `/portfolio/positions` |
| Exposure | `/portfolio/exposure` |
| Risk | `/portfolio/risk` |
| Execution Queue | `/execution/active/{symbol}` |
| History | `/execution/history/{symbol}` |

### System Control
| Component | Endpoint |
|-----------|----------|
| Service Health | `/control/summary` |
| Risk State | `/control/risk/{symbol}` |
| Alerts | `/control/alerts/{symbol}` |
| Cockpit State | `/control/state/{symbol}` |

---

## 11. NEXT STEPS

### PHASE F1 — Research Functional Integration
1. Bind `/chart/full-analysis` to Research Overview
2. Bind `/hypothesis/list` and `/hypothesis/top` to Hypotheses Screen
3. Bind `/signal/explanation` to Signal panel
4. Bind `/capital-flow/summary` to Capital Flow panel
5. Bind `/fractal/summary` to Fractal panel

### PHASE F2 — Trading Terminal Integration
1. Bind `/portfolio/state` to Portfolio Overview
2. Bind `/portfolio/positions` to Positions table
3. Bind `/execution/plan` and `/execute` to Execution actions
4. Bind `/portfolio/risk` to Risk tab

### PHASE F3 — System Control Integration
1. Bind `/control/summary` to Overview
2. Bind `/control/alerts` to Alerts panel
3. Bind `/control/risk` to Metrics

---

## 12. ENDPOINTS NOT YET CREATED (TO BUILD)

For full functionality, these endpoints need to be added:

```
GET  /api/v1/research/regime/{symbol}         - Market regime overview
GET  /api/v1/research/context/{symbol}        - Full research context
GET  /api/v1/system/services                  - All services health
GET  /api/v1/system/metrics                   - System metrics
POST /api/v1/system/kill-switch               - Emergency stop
GET  /api/v1/execution/pending                - Pending approvals queue
POST /api/v1/execution/approve/{order_id}     - Approve order
POST /api/v1/execution/reject/{order_id}      - Reject order
```

---

**END OF CONTRACT MAP**
