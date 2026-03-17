# PHASE F4.0 — Chart System Audit Report

## Executive Summary

The FOMO platform contains **5 distinct chart rendering systems** spread across **~20,000+ lines of chart code**.
Two primary rendering technologies are used:

| Renderer | Library | Version | LOC | Modules |
|----------|---------|---------|-----|---------|
| **TradingView** | `lightweight-charts` | ^5.1.0 | ~4,500 | 15+ components |
| **Custom Canvas** | Native Canvas 2D API | — | ~5,700 | 25+ files |
| **Recharts** | `recharts` | ^3.7.0 | ~8,000+ | 50+ components |

**Recommendation: TradingView lightweight-charts v5 as Primary Renderer + Custom Canvas Fractal overlays**

---

## CRITICAL FINDING: 5 Visual Chart Types Already Implemented

### 1️⃣ Fractal Projection Chart
**Location**: `/components/fractal/chart/FractalHybridChart.jsx` (813 LOC)
**Renderer**: Custom Canvas 2D
**Features**:
- Synthetic forecast path (green dashed)
- Replay forecast path (purple dashed)  
- Hybrid combined path (solid green)
- Historical match replay
- Phase click drilldown
- Multi-asset support (BTC, ETH, SPX, DXY)
**Data Source**: `/api/fractal/v2.1/chart`, `/api/dxy/v2.1/chart`

### 2️⃣ Prediction Path Chart
**Location**: `/components/charts/TradingViewChart.jsx` (435 LOC)
**Renderer**: TradingView Lightweight Charts v5
**Features**:
- OHLC Candlesticks
- Volume histogram (togglable)
- Forecast overlay: TWO LINE SERIES (green UP / red DOWN)
- Future segment: lastClose → targetPrice
- Right offset for future predictions
- Outcome markers (W/L)
**Data Source**: `/api/ui/candles`, `/api/forecast`

### 3️⃣ AI Forecast Chart (MetaBrain)
**Location**: `/modules/meta-brain-ui/MetaBrainChart.jsx` (714 LOC)
**Renderer**: TradingView Lightweight Charts v5
**Features**:
- Real BTC candles + Volume
- History line (black) following closes up to NOW
- Forecast curve (green/red/gray by verdict) from NOW forward
- Vertical NOW separator line
- Markers: 1D, 7D, 30D labeled points
- Monotone cubic interpolation (Fritsch-Carlson)
**Data Source**: `/api/ui/candles`, `/api/meta-brain-v2/forecast-curve`

### 4️⃣ Scenario Simulation Chart
**Location**: `/components/fractal/chart/FractalChartCanvas.jsx` (988 LOC)
**Renderer**: Custom Canvas 2D
**Features**:
- Multi-mode forecast: Hybrid, Replay, Synthetic, Macro
- P10-P90 confidence bands
- Phase zone rendering (colored backgrounds)
- NOW separator
- 7D Arrow overlay
- 7D Capsule overlay
- HiDPI support (devicePixelRatio)
- Touch support (pinch zoom, drag pan)
**Data Source**: `/api/fractal/forecast`

### 5️⃣ Classic Candles + Indicators
**Location**: `/components/charts/tvChartPreset.js` (143 LOC) - Factory
**Used By**: TradingViewChart, TradingViewChartV2, LivePredictionChart, etc.
**Renderer**: TradingView Lightweight Charts v5
**Features**:
- CandlestickSeries (OHLC)
- HistogramSeries (Volume)
- LineSeries (SMA, EMA, forecast overlays)
- CrosshairMode
- createSeriesMarkers()
**Presets**: `TV_CANDLE_OPTIONS`, `TV_VOLUME_OPTIONS`

---

## 1. Existing Chart Implementations

### 1.1 TradingView Lightweight Charts (PRIMARY CANDIDATE)

**Factory**: `/components/charts/tvChartPreset.js` (143 LOC)
- Creates standardized chart instances via `createTvChart()`
- V5-compatible marker wrapper via `setSeriesMarkers()`
- Exported presets: `TV_CANDLE_OPTIONS`, `TV_VOLUME_OPTIONS`
- Used across ALL TradingView-based charts

#### Chart Modules:

| Module | Location | LOC | Features | Used In |
|--------|----------|-----|----------|---------|
| **TradingViewChart** | `/components/charts/TradingViewChart.jsx` | 434 | Candles, Volume, Forecast overlay (UP/DOWN), Outcomes (W/L markers), Horizon toggles | Prediction Page |
| **TradingViewChartV2** | `/components/charts/TradingViewChartV2.jsx` | 478 | Independent forecast overlays, Multi-layer support (prediction/exchange/sentiment), Color-coded layers | Price Expectation V2 |
| **LivePredictionChart** | `/components/charts/LivePredictionChart.jsx` | 662 | Real-time candles, Prediction arrows, Historical forecast tracking | Prediction Page Live |
| **ForecastOnlyChart** | `/components/charts/ForecastOnlyChart.jsx` | 323 | Forecast-only view, No candles, Line/area forecast | Forecast Table |
| **SegmentedForecastChart** | `/components/charts/SegmentedForecastChart.jsx` | 364 | Segmented forecast display, Multiple horizons | Labs Pages |
| **SentimentForecastChart** | `/components/charts/SentimentForecastChart.jsx` | 429 | Candles + sentiment overlay, Sentiment-driven forecast | Sentiment Pages |
| **SentimentForecastChartV2** | `/components/charts/SentimentForecastChartV2.jsx` | 384 | Updated sentiment chart, Better styling | Sentiment Pages V2 |
| **MetaBrainChart** | `/modules/meta-brain-ui/MetaBrainChart.jsx` | 713 | Candles + Volume + History line + Forecast curve, NOW separator, 1D/7D/30D markers, Verdict-colored forecast (green/red/gray) | Meta Brain Page |
| **BtcForecastChart** | `/components/prediction/BtcForecastChart.jsx` | 330 | BTC-specific forecast chart | Prediction Page |
| **ExchangeForecastChartV3** | `/components/prediction/ExchangeForecastChartV3.jsx` | 529 | Exchange forecast with indicators | Exchange Page |
| **ExchangeForecastChartV2** | `/components/exchange/ExchangeForecastChartV2.jsx` | 271 | Exchange forecast V2 | Exchange Dashboard |
| **OnChainForecastChartV2** | `/components/onchain/OnChainForecastChartV2.tsx` | 368 | On-chain forecast with flow data | Onchain V3 |
| **OnchainContextChart** | `/components/onchain/OnchainContextChart.tsx` | 155 | Context chart for onchain | Onchain Pages |
| **MarketChart** | `/components/market/chart/MarketChart.jsx` | 230 | Market overview chart | Market Hub |
| **PriceChart** | `/components/market/chart/PriceChart.jsx` | 164 | Simple price chart | Market Pages |

**Overlays on TradingView**:
| Overlay | Location | LOC | Function |
|---------|----------|-----|----------|
| **TruthOverlay** | `/components/market/chart/TruthOverlay.jsx` | 159 | Truth vs prediction comparison |
| **VerdictOverlay** | `/components/market/chart/VerdictOverlay.jsx` | 84 | Verdict visualization |
| **DivergenceMarkers** | `/components/market/chart/DivergenceMarkers.jsx` | 134 | Divergence point markers |
| **ChartGradients** | `/components/charts/ChartGradients.jsx` | 48 | SVG gradient defs |
| **ChartTooltip** | `/components/charts/ChartTooltip.jsx` | 83 | Custom tooltip |

---

### 1.2 Custom Canvas Fractal Engine (STRONGEST OVERLAY SYSTEM)

**Total: ~5,739 LOC across 25 files**

**Core Engine**: `/components/fractal/chart/`

| File | LOC | Function |
|------|-----|----------|
| `ChartRoot.js` | 240 | Main canvas component with zoom/pan/crosshair |
| `draw.js` | 524 | Master draw orchestrator (candles, volume, grid, axes, crosshair, overlays) |
| `FractalChartCanvas.jsx` | 988 | Full fractal chart with tooltips, forecast, phases, multi-mode |
| `FractalHybridChart.jsx` | 812 | Hybrid/Replay/Synthetic forecast chart |
| `FractalMainChart.jsx` | 185 | Main fractal chart wrapper |
| `PhaseTooltip.jsx` | 201 | Phase tooltip component |
| `ForecastSummary7d.jsx` | 98 | 7-day forecast summary |
| `types.js` | 83 | Type definitions, DEFAULT_LAYOUT, DEFAULT_THEME |
| `scales.js` | 42 | Price/coordinate scaling (priceToY, clamp) |
| `format.js` | 39 | Date/price formatters |
| `interactions.js` | 33 | Pan/zoom/reset viewport |
| `mappers.js` | 167 | Data mappers (candles, forecast, phases) |
| `api.js` | 77 | API data fetcher |

**Drawing Layers** (`/components/fractal/chart/layers/`):

| Layer | LOC | Function |
|-------|-----|----------|
| `drawCandles.js` | 42 | OHLC candle rendering |
| `drawForecast.js` | 380 | Forecast projection rendering |
| `drawHybridForecast.js` | 797 | Hybrid/Replay/Synthetic/Macro forecast |
| `drawSMA.js` | 36 | SMA indicator overlay |
| `drawPhases.js` | 49 | Phase zone rendering |
| `drawGrid.js` | 30 | Grid lines |
| `drawTimeAxis.js` | 94 | Time axis + NOW separator |
| `drawBackground.js` | 7 | Background fill |
| `draw7dArrow.js` | 184 | 7-day forecast arrow |
| `drawForecastCapsule7d.js` | 238 | 7-day forecast capsule |

**Math Utilities** (`/components/fractal/chart/math/`):

| File | LOC | Function |
|------|-----|----------|
| `scale.js` | 143 | Index/time X scaling, Y scaling, padded min/max |
| `buildAftermathForecast.js` | 218 | Forecast point construction |
| `spline.js` | 34 | Spline interpolation |

**Unique Features**:
- **Multi-mode forecast**: Hybrid, Replay, Synthetic, Macro
- **Phase rendering**: Market phases as colored zones
- **NOW separator**: Vertical line separating history from forecast
- **Multi-asset support**: BTC, ETH, SPX, DXY with per-asset formatting
- **HiDPI support**: devicePixelRatio-aware rendering
- **Touch support**: Pinch zoom, drag pan

---

### 1.3 Fractal UI Adapter

**Location**: `/fractal-ui/`

| File | Function |
|------|----------|
| `ChartAdapter.jsx` | Universal wrapper for FractalMainChart/FractalHybridChart |
| `FractalShell.jsx` | Shell component for fractal terminal |
| `index.js` | Module exports |

**Purpose**: Adapts canvas-based fractal charts to unified contract (candles, nav, continuation, bands).

---

### 1.4 FOMO AI Charts

**Location**: `/components/fomo-ai/` (~4,559 LOC total)

Key chart components:

| Module | LOC | Library | Function |
|--------|-----|---------|----------|
| `CentralChart.jsx` | 426 | Recharts | Central AI decision chart |
| `FomoAiChart.jsx` | 125 | Recharts | FOMO AI overview chart |
| `FearGreedHistoryChart.jsx` | 321 | Recharts | Fear/Greed index history |

---

### 1.5 Recharts (SECONDARY — Metrics/Analytics)

Used in **50+ components** for non-trading analytics:
- Bar charts, line charts, area charts, scatter plots, donuts
- Admin metrics dashboards
- Performance tables
- Not suitable for candlestick/trading charts

---

## 2. Libraries Used

| Library | Version | Type | Usage |
|---------|---------|------|-------|
| `lightweight-charts` | ^5.1.0 | Canvas (WebGL) | Primary trading charts |
| `recharts` | ^3.7.0 | SVG | Metrics, analytics, dashboards |
| Custom Canvas 2D | Native | Canvas 2D | Fractal engine |

**No d3, chart.js, or WebGL custom implementations found.**

---

## 3. Renderer Comparison

| Feature | TradingView LC v5 | Custom Canvas Fractal | Recharts |
|---------|-------------------|----------------------|----------|
| Candles | ✅ Native | ✅ Custom drawn | ❌ |
| Volume | ✅ Histogram | ✅ Custom drawn | ❌ |
| Indicators (SMA/EMA) | ✅ LineSeries | ✅ drawSMA | ❌ |
| Forecast overlays | ✅ LineSeries | ✅ drawForecast + drawHybridForecast | ❌ |
| Fractal projections | ⚠️ Requires custom | ✅ Native (multi-mode) | ❌ |
| Phase zones | ⚠️ Custom markers | ✅ drawPhases | ❌ |
| Scenario bands | ⚠️ Area series | ✅ P10-P90 bands | ❌ |
| Zoom/Pan | ✅ Built-in | ✅ Custom implemented | ❌ |
| Touch support | ✅ Built-in | ✅ Implemented | ❌ |
| HiDPI | ✅ Automatic | ✅ Manual DPR | ❌ |
| Performance (1000+ candles) | ✅ Excellent (GPU) | ⚠️ Good (CPU) | ❌ |
| Custom drawing | ⚠️ Plugin API | ✅ Full control | ❌ |

---

## 4. Overlay Systems

### 4.1 Forecast Overlays

| Overlay | Source | Renderer | Data Input |
|---------|--------|----------|------------|
| Prediction Line (UP/DOWN) | TradingViewChart | LineSeries (green/red) | `/api/forecast` |
| Independent Layer Overlays | TradingViewChartV2 | Multiple LineSeries | `/api/forecast` per layer |
| MetaBrain Forecast Curve | MetaBrainChart | LineSeries (verdict-colored) | `/api/meta-brain-v2/forecast-curve` |
| Hybrid Forecast | FractalChartCanvas | Canvas drawHybridForecast | `/api/fractal/forecast` |
| Synthetic Forecast | FractalChartCanvas | Canvas drawHybridForecast | `/api/fractal/forecast` |
| Replay Forecast | FractalChartCanvas | Canvas drawHybridForecast | `/api/fractal/forecast` |
| Macro Forecast | FractalChartCanvas | Canvas drawMacroForecast | `/api/fractal/macro` |
| 7D Arrow | FractalChartCanvas | Canvas draw7dArrow | Computed |
| 7D Capsule | FractalChartCanvas | Canvas drawForecastCapsule7d | Computed |

### 4.2 Indicator Overlays

| Indicator | Renderer | Implementation |
|-----------|----------|---------------|
| SMA (200) | Canvas | `drawSMA.js` |
| Volume | Both | Histogram (TV) / Canvas bars |

### 4.3 Structural Overlays

| Overlay | Renderer | Implementation |
|---------|----------|---------------|
| Phase Zones | Canvas | `drawPhases.js` (colored background zones) |
| NOW Separator | Canvas | `drawTimeAxis.js` (vertical line) |
| Truth Overlay | TradingView | `TruthOverlay.jsx` |
| Verdict Overlay | TradingView | `VerdictOverlay.jsx` |
| Divergence Markers | TradingView | `DivergenceMarkers.jsx` |
| Outcome Markers (W/L) | TradingView | `createSeriesMarkers()` |

---

## 5. Data Pipelines

### Current Chart Data Sources

| Endpoint | Data Format | Used By |
|----------|-------------|---------|
| `/api/v1/chart/full-analysis/{symbol}/{tf}` | `{ candles[], indicators{}, patterns[], hypothesis{} }` | ResearchService → Chart Lab |
| `/api/ui/candles` | `{ candles: [{time, open, high, low, close, volume}] }` | MetaBrainChart, TradingViewChart |
| `/api/meta-brain-v2/forecast-curve` | `{ curve: [{time, value}], verdict }` | MetaBrainChart |
| `/api/fractal/*` | `{ forecast: {synthetic, hybrid, replay, macro} }` | FractalChartCanvas |
| `/api/forecast/*` | `{ predictions: [{horizon, direction, target_price}] }` | PredictionCharts |
| `/api/hypothesis/list` | `{ hypotheses[] }` | HypothesesView → Chart overlay |
| `/api/v1/fractal/summary/{symbol}` | `{ current: {bias, confidence, alignment} }` | ResearchService |

### Series Builders

| Builder | Location | Function |
|---------|----------|----------|
| `mappers.js` | Fractal chart | Maps API data → canvas coordinates |
| `scale.js` | Fractal chart | Time/price → pixel coordinate mapping |
| `tvChartPreset.js` | TradingView | Standardized chart creation |
| `researchService.js` | Research | API → ResearchState |

---

## 6. Recommended Unified Chart Base

### Primary Renderer: TradingView Lightweight Charts v5

**Why:**
- GPU-accelerated (WebGL) — handles 10,000+ candles
- Built-in zoom/pan/crosshair/touch
- Professional financial chart look
- Already used in 15+ components
- Active open-source project with plugin API
- Factory already exists (`tvChartPreset.js`)

### Overlay System: Custom Canvas (from Fractal Engine)

**Why:**
- Most sophisticated overlay system in the codebase
- 5 distinct forecast modes (Hybrid/Synthetic/Replay/Macro/7D)
- Phase zone rendering
- P10-P90 confidence bands
- NOW separator logic
- Multi-asset price formatting

### Architecture Recommendation

```
FOMO Chart Engine
├── core/
│   ├── ChartEngine.jsx          ← TradingView LC v5 wrapper
│   ├── chartConfig.js           ← Unified config (from tvChartPreset.js)
│   └── useChartData.js          ← Data hook from ResearchState
├── series/
│   ├── CandleSeries.js          ← OHLCV candle rendering
│   ├── VolumeSeries.js          ← Volume histogram
│   └── IndicatorSeries.js       ← SMA/EMA/RSI via LineSeries
├── overlays/
│   ├── ForecastOverlay.js       ← From TradingViewChart forecast logic
│   ├── FractalOverlay.js        ← From drawHybridForecast.js
│   ├── HypothesisOverlay.js     ← NEW: hypothesis paths
│   ├── ScenarioOverlay.js       ← From FractalChartCanvas scenario bands
│   ├── PhaseOverlay.js          ← From drawPhases.js
│   └── LiquidityZoneOverlay.js  ← NEW: from chart/full-analysis
└── plugins/
    ├── NowSeparator.js          ← From drawTimeAxis.js
    ├── OutcomeMarkers.js         ← From TradingViewChart markers
    └── VerdictOverlay.js         ← From market/chart/VerdictOverlay.jsx
```

### Migration Priority

| Priority | Source Module | Target | Effort |
|----------|-------------|--------|--------|
| P0 | `tvChartPreset.js` | `core/chartConfig.js` | Extract as-is |
| P0 | `TradingViewChart.jsx` | `core/ChartEngine.jsx` | Generalize |
| P1 | `drawHybridForecast.js` | `overlays/FractalOverlay.js` | Adapt to TV plugin API |
| P1 | `MetaBrainChart.jsx` forecast logic | `overlays/ForecastOverlay.js` | Extract |
| P2 | `drawPhases.js` | `overlays/PhaseOverlay.js` | Canvas → TV plugin |
| P2 | `TradingViewChart.jsx` markers | `plugins/OutcomeMarkers.js` | Extract |
| P3 | New | `overlays/HypothesisOverlay.js` | New from hypothesis data |
| P3 | New | `overlays/LiquidityZoneOverlay.js` | New from chart objects |

---

## 7. What NOT to Do

- ❌ **Do NOT install a new chart library** (three renderers are enough)
- ❌ **Do NOT rewrite the fractal canvas engine** (5,700 LOC of working code)
- ❌ **Do NOT build a new candlestick renderer** (TradingView does it better)
- ❌ **Do NOT migrate recharts charts** (they serve a different purpose: metrics/analytics)
- ❌ **Do NOT delete any existing chart code yet** (first consolidate, then deprecate)

---

## 8. LOC Summary

| System | Files | Total LOC |
|--------|-------|-----------|
| TradingView charts | 15 | ~4,500 |
| Canvas Fractal engine | 25 | ~5,739 |
| Chart utilities (gradients, tooltips, theme) | 5 | ~400 |
| Fractal UI adapter | 3 | ~200 |
| Market chart overlays | 5 | ~771 |
| FOMO AI charts (Recharts) | 3 | ~872 |
| Recharts analytics (50+ components) | 50+ | ~8,000+ |
| **TOTAL CHART CODE** | **~100+** | **~20,000+** |

---

## 9. Production-Ready Charts Summary

### Already Working (Just Need Integration):

| Chart Type | Component | LOC | Status |
|------------|-----------|-----|--------|
| Classic Candles + Volume | `TradingViewChart.jsx` | 434 | ✅ Production |
| Independent Forecast Layers | `TradingViewChartV2.jsx` | 478 | ✅ Production |
| MetaBrain Forecast Curve | `MetaBrainChart.jsx` | 713 | ✅ Production |
| Fractal Multi-Mode | `FractalChartCanvas.jsx` | 988 | ✅ Production |
| Fractal Hybrid/Replay | `FractalHybridChart.jsx` | 812 | ✅ Production |
| Segmented Forecast | `SegmentedForecastChart.jsx` | 364 | ✅ Production |
| Sentiment Forecast | `SentimentForecastChart.jsx` | 429 | ✅ Production |
| Exchange Forecast V3 | `ExchangeForecastChartV3.jsx` | 529 | ✅ Production |
| Live Prediction | `LivePredictionChart.jsx` | 662 | ✅ Production |

### Key Insight
**~95% of chart functionality is already implemented.**  
The charts just need to be connected to the unified Chart Lab / Tech Analysis module.

---

## 10. Next Steps (F4.1 - F4.5)

### F4.1 — Renderer Selection
- [x] TradingView LC v5 confirmed as primary renderer
- [ ] Design TV Plugin API for custom overlays

### F4.2 — Chart Engine Consolidation
- [ ] Create unified `ChartEngine.jsx` from `tvChartPreset.js`
- [ ] Extract reusable hooks: `useChartData`, `useForecast`

### F4.3 — Overlay Integration
- [ ] Port `drawHybridForecast.js` → TV Plugin
- [ ] Port `drawPhases.js` → TV Plugin
- [ ] Create `HypothesisOverlay` (new)

### F4.4 — Indicator Engine
- [ ] Unify SMA/EMA/RSI rendering
- [ ] Add MACD, Bollinger Bands support

### F4.5 — Chart Performance Optimization
- [ ] Implement virtualization for 10k+ candles
- [ ] Add WebWorker for heavy calculations

---

*Report updated: 2026-03-16*
*Audit scope: /app/frontend/src/*
*Status: AUDIT COMPLETE — No code modified*
