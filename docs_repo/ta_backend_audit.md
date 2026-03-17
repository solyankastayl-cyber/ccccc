# PHASE F4.0 — TA Backend Module Audit (Research Logic Only)

## Executive Summary

Backend модуль технического анализа содержит **122 модуля** в `/app/backend/modules/`.
Для **Research Logic** (без Trading Terminal) релевантны **~25 ключевых модулей**.

---

## 1. TA Engine Core (`/app/backend/modules/ta_engine/`)

### Файловая структура
```
ta_engine/
├── __init__.py
├── ta_routes.py              (91 LOC)
└── hypothesis/
    ├── __init__.py
    ├── ta_hypothesis_builder.py   (714 LOC) ⭐ CORE
    ├── ta_hypothesis_rules.py     (конфиги)
    ├── ta_hypothesis_tests.py
    └── ta_hypothesis_types.py
```

### ta_hypothesis_builder.py — CORE ENGINE

**Назначение**: Builds unified TA hypothesis from market data

**Компоненты анализа**:
| Компонент | Метод | Что анализирует |
|-----------|-------|-----------------|
| Trend | `_compute_trend()` | MA alignment (20/50/200), price position |
| Momentum | `_compute_momentum()` | RSI, MACD, divergence |
| Structure | `_compute_structure()` | HH/HL, BOS, ChoCh |
| Breakout | `_compute_breakout()` | Range breakout, volume confirmation |

**Технические индикаторы**:
- SMA (`_sma`)
- EMA (`_ema`)
- RSI (`_rsi`)
- MACD (`_macd`)
- ATR (`_atr`)

**Output**: `TAHypothesis` с полями:
```python
- direction: LONG/SHORT/NEUTRAL
- setup_quality: 0-1
- setup_type: BREAKOUT/CONTINUATION/REVERSAL/etc
- trend_strength: 0-1
- entry_quality: 0-1
- regime_fit: 0-1
- conviction: 0-1
- regime: TREND_UP/TREND_DOWN/RANGE/etc
- drivers: {trend, momentum, structure, breakout}
```

### API Endpoints (`ta_routes.py`)
| Endpoint | Method | Назначение |
|----------|--------|------------|
| `/api/ta-engine/status` | GET | Health check |
| `/api/ta-engine/hypothesis/{symbol}` | GET | Unified hypothesis |
| `/api/ta-engine/hypothesis/full/{symbol}` | GET | Full detailed hypothesis |
| `/api/ta-engine/hypothesis/batch` | GET | Multi-symbol batch |

---

## 2. Research Analytics (`/app/backend/modules/research_analytics/`)

### Файловая структура
```
research_analytics/
├── __init__.py
├── chart_data.py         (chart data builder)
├── fractal_viz.py        (fractal visualization)
├── hypothesis_viz.py     (hypothesis visualization)
├── indicators.py         (547 LOC) ⭐
├── patterns.py           (554 LOC) ⭐
├── research_presets.py   (presets)
└── routes.py             (API routes)
```

### indicators.py — INDICATOR SERVICE

**Доступные индикаторы**:
```python
AVAILABLE_INDICATORS = [
    "sma", "ema", "vwap", "rsi", "macd", "atr",
    "bollinger", "supertrend", "volume_profile",
    "momentum", "stochastic", "adx", "obv"
]
```

**Реализованные**:
| Индикатор | LOC | Features |
|-----------|-----|----------|
| SMA | 30 | Configurable period |
| EMA | 30 | Exponential smoothing |
| RSI | 50 | Overbought/oversold levels |
| MACD | 40 | Line + Signal + Histogram |
| Bollinger | 35 | Upper/Middle/Lower bands |
| ATR | 30 | True range averaging |
| VWAP | 25 | Cumulative TPV/Volume |
| Supertrend | 50 | Trend direction + levels |
| Volume Profile | 45 | POC detection |

**Output**: `IndicatorSeries` с values, bands, metadata

### patterns.py — PATTERN DETECTION SERVICE

**Типы паттернов**:
```python
PATTERN_TYPES = [
    "triangle", "wedge", "channel", "flag", "pennant",
    "head_shoulders", "double_top", "double_bottom",
    "breakout", "compression", "range"
]
```

**Реализованные детекторы**:
| Паттерн | Метод | Features |
|---------|-------|----------|
| Triangle | `_detect_triangles()` | Symmetric, ascending, descending |
| Channel | `_detect_channels()` | Ascending, descending, horizontal |
| Compression | `_detect_compression()` | ATR ratio analysis |
| Breakout | `_detect_breakouts()` | Range breakout detection |
| Support/Resistance | `detect_support_resistance()` | Pivot clustering |
| Liquidity Zones | `detect_liquidity_zones()` | Volume clustering |

**Output**: `DetectedPattern` с points, levels, confidence

---

## 3. Hypothesis Engine (`/app/backend/modules/hypothesis_engine/`)

### Файловая структура
```
hypothesis_engine/
├── __init__.py
├── hypothesis_engine.py           (core engine)
├── hypothesis_registry.py         (storage)
├── hypothesis_routes.py           (API)
├── hypothesis_scoring_engine.py   (scoring)
├── hypothesis_conflict_resolver.py (conflict resolution)
├── hypothesis_types.py            (types)
└── *_tests.py                     (tests)
```

**Назначение**: Multi-source hypothesis aggregation and scoring

---

## 4. Fractal Intelligence (`/app/backend/modules/fractal_intelligence/`)

### Файловая структура
```
fractal_intelligence/
├── __init__.py
├── asset_fractal_routes.py
├── asset_fractal_service.py
├── btc_fractal_adapter.py
├── dxy_fractal_adapter.py
├── spx_fractal_adapter.py
├── fractal_context_engine.py
├── fractal_context_routes.py
└── fractal_context_types.py
```

**Назначение**: Fractal pattern matching across assets (BTC, SPX, DXY)

---

## 5. Market Data (`/app/backend/modules/market_data/`)

### Файловая структура
```
market_data/
├── __init__.py
├── candle_builder.py
├── market_data_engine.py
├── market_data_normalizer.py
├── market_data_repository.py
├── market_data_routes.py
├── market_data_types.py
├── market_snapshot_builder.py
└── stream_processors.py
```

**Назначение**: OHLCV data ingestion, normalization, storage

---

## 6. Regime Intelligence (`/app/backend/modules/regime_intelligence_v2/`)

### Файловая структура
```
regime_intelligence_v2/
├── regime_detection_engine.py      (detection)
├── regime_transition_engine.py     (transitions)
├── regime_context_engine.py        (context)
├── strategy_regime_mapping_engine.py (strategy mapping)
└── regime_types.py
```

**Market Regimes**:
- TREND_UP
- TREND_DOWN
- RANGE
- EXPANSION
- COMPRESSION

---

## 7. Alpha Interactions (`/app/backend/modules/alpha_interactions/`)

### Файловая структура
```
alpha_interactions/
├── cancellation_engine.py
├── conflict_patterns.py
├── reinforcement_patterns.py
├── synergy_engine.py
├── fractal_interaction_engine.py
└── interaction_aggregator.py
```

**Назначение**: Signal conflict/synergy detection

---

## 8. Дополнительные Research модули

| Модуль | Путь | LOC | Назначение |
|--------|------|-----|------------|
| `visual_objects` | `/modules/visual_objects/` | ~200 | Chart object builder |
| `research_memory` | `/modules/research_memory/` | ~300 | Research state persistence |
| `research_loop` | `/modules/research_loop/` | ~500 | Adaptive research cycle |
| `validation` | `/modules/validation/` | ~1500 | Backtest validation |
| `walk_forward` | `/modules/walk_forward/` | ~400 | Walk-forward testing |
| `signal_explanation` | `/modules/signal_explanation/` | ~200 | Signal explainer |

---

## 9. Data Flow Architecture

```
Market Data → Candle Builder → MongoDB
                    ↓
              TA Engine
           /     |     \
      Trend  Momentum  Structure
           \     |     /
                 ↓
          TAHypothesis
                 ↓
       Hypothesis Registry
                 ↓
         Scoring Engine
                 ↓
    Conflict Resolver (multi-source)
                 ↓
           Final Signal
```

---

## 10. Database Collections

| Collection | Назначение |
|------------|------------|
| `candles` | OHLCV data by symbol/timeframe |
| `indicators` | Computed indicator values |
| `patterns` | Detected patterns |
| `hypotheses` | Generated hypotheses |
| `hypothesis_runs` | Hypothesis run history |
| `scenarios` | Scenario simulations |

---

## 11. LOC Summary (Research Logic Only)

| Module | Files | LOC |
|--------|-------|-----|
| ta_engine | 6 | ~1,000 |
| research_analytics | 8 | ~1,500 |
| hypothesis_engine | 12 | ~2,000 |
| fractal_intelligence | 10 | ~1,500 |
| market_data | 9 | ~1,200 |
| regime_intelligence_v2 | 15 | ~2,000 |
| alpha_interactions | 15 | ~2,500 |
| validation | 18 | ~3,000 |
| **TOTAL RESEARCH** | **~93** | **~14,700** |

---

## 12. ❌ Excluded (Trading Terminal)

НЕ включено в этот аудит:
- `/modules/trading_terminal/` — торговый терминал
- `/modules/execution_*` — execution layer
- `/modules/broker_adapters/` — broker connections
- `/modules/portfolio_*` — portfolio management
- `/modules/capital_*` — capital allocation

---

## 13. API Summary (Research Only)

| Endpoint Group | Base Path | Key Endpoints |
|----------------|-----------|---------------|
| TA Engine | `/api/ta-engine` | `/hypothesis/{symbol}`, `/status` |
| Research Analytics | `/api/v1/chart` | `/full-analysis/{symbol}/{tf}` |
| Hypothesis | `/api/hypothesis` | `/list`, `/score`, `/conflicts` |
| Fractal | `/api/fractal` | `/v2.1/chart`, `/v2.1/focus-pack` |
| Patterns | `/api/patterns` | `/detect`, `/support-resistance` |
| Indicators | `/api/indicators` | `/calculate`, `/batch` |

---

## 14. Next Steps

### F4.1 — Indicator Engine Consolidation
- [ ] Unify `ta_hypothesis_builder` indicators with `research_analytics/indicators.py`
- [ ] Add missing: Stochastic, ADX, OBV

### F4.2 — Pattern Engine Enhancement
- [ ] Add Head & Shoulders detection
- [ ] Add Harmonic patterns (Gartley, Bat)
- [ ] Add Elliott Wave basic detection

### F4.3 — Hypothesis Competition Layer
- [ ] Multi-timeframe hypothesis aggregation
- [ ] Source weighting (TA vs Fractal vs Sentiment)

### F4.4 — Real-time Integration
- [ ] WebSocket hypothesis streaming
- [ ] Live pattern updates

---

*Report generated: 2026-03-16*
*Audit scope: /app/backend/modules/ (Research Logic only)*
*Excluded: Trading Terminal, Execution, Portfolio*
