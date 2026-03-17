# PHASE F4.0 — TA Backend FULL Audit

## Executive Summary

**Backend Research Logic**: 14,700+ LOC across 93+ modules
**Indicators реализованы**: 32+ индикаторов
**Chart/Prediction Rendering**: 5 компонентов визуализации

---

## 1. CORE INDICATORS (Реализованные)

### 1.1 TAHypothesisBuilder (`ta_engine/hypothesis/ta_hypothesis_builder.py` - 714 LOC)

| Индикатор | Метод | LOC | Параметры |
|-----------|-------|-----|-----------|
| **SMA** | `_sma()` | 5 | period |
| **EMA** | `_ema()` | 8 | period |
| **RSI** | `_rsi()` | 25 | period=14 |
| **MACD** | `_macd()` | 12 | fast=12, slow=26, signal=9 |
| **ATR** | `_atr()` | 18 | period=14 |

### 1.2 Research Analytics Indicators (`research_analytics/indicators.py` - 547 LOC)

| Индикатор | Статус | Features |
|-----------|--------|----------|
| **SMA** | ✅ | Multi-period |
| **EMA** | ✅ | Multi-period |
| **VWAP** | ✅ | Cumulative |
| **RSI** | ✅ | Overbought/Oversold |
| **MACD** | ✅ | Line + Signal + Histogram |
| **Bollinger** | ✅ | Upper/Middle/Lower + Squeeze |
| **ATR** | ✅ | True Range |
| **Supertrend** | ✅ | Direction + Levels |
| **Volume Profile** | ✅ | POC Detection |
| **Momentum** | ✅ | Rate of Change |
| **Stochastic** | ✅ | %K + %D |
| **ADX** | ✅ | Trend Strength |
| **OBV** | ✅ | On Balance Volume |

### 1.3 Доступные индикаторы (Config)

```python
AVAILABLE_INDICATORS = [
    "sma", "ema", "vwap", "rsi", "macd", "atr",
    "bollinger", "supertrend", "volume_profile",
    "momentum", "stochastic", "adx", "obv"
]
```

### 1.4 Overlays (Config)

```python
AVAILABLE_OVERLAYS = [
    "support_resistance",   # S/R levels
    "trend_lines",          # Trend detection
    "trend_channel",        # Channel overlay
    "liquidity_zones",      # Liquidity clusters
    "patterns",             # Chart patterns
    "hypotheses",           # Hypothesis paths
    "fractals",             # Fractal projections
    "breakout_zones",       # Breakout areas
    "invalidation_lines"    # Stop/Invalid levels
]
```

---

## 2. PATTERN DETECTION (Реализованные)

### 2.1 PatternDetectionService (`research_analytics/patterns.py` - 554 LOC)

| Pattern | Метод | Features |
|---------|-------|----------|
| **Triangle** | `_detect_triangles()` | Symmetric, Ascending, Descending |
| **Channel** | `_detect_channels()` | Ascending, Descending, Horizontal |
| **Compression** | `_detect_compression()` | ATR ratio analysis |
| **Breakout** | `_detect_breakouts()` | Range breakout |
| **Support/Resistance** | `detect_support_resistance()` | Pivot clustering |
| **Liquidity Zones** | `detect_liquidity_zones()` | Volume clustering |

### 2.2 Pattern Types

```python
PATTERN_TYPES = [
    "triangle",        # Ascending, Descending, Symmetric
    "wedge",           # Rising, Falling
    "channel",         # Parallel lines
    "flag",            # Continuation
    "pennant",         # Continuation
    "head_shoulders",  # H&S, Inverse H&S
    "double_top",      # Reversal
    "double_bottom",   # Reversal
    "breakout",        # Range breakout
    "compression",     # Volatility squeeze
    "range"            # Consolidation
]
```

---

## 3. CHART RENDERING LOGIC

### 3.1 HypothesisVisualizationService (`research_analytics/hypothesis_viz.py` - 519 LOC)

**Как строится предсказание**:

```
1. Analyze Direction
   ├── EMA 20/50 Crossover
   ├── Momentum (20-bar change)
   └── Output: bullish/bearish/neutral + confidence + strength

2. Build Scenarios (3-5 штук)
   ├── Base Scenario (45% probability)
   ├── Bull Scenario (25% probability)
   ├── Bear Scenario (20% probability)
   └── Extreme Bull/Bear (10% probability)

3. Calculate Price Path
   ├── Target Price = current * (1 + target_pct)
   ├── Non-linear path with noise
   ├── Confidence bands (widen over time)
   └── ATR-based volatility

4. Calculate Key Levels
   ├── Entry Zone (ATR-based pullback)
   ├── Stop Loss (swing + ATR buffer)
   ├── Take Profit (1:2, 1:3, 1:5 R:R)
   └── Invalidation Level
```

### 3.2 Scenario Types

| Scenario | Target % | Probability | Color |
|----------|----------|-------------|-------|
| **Base (Bullish)** | +3% | 45% | #22C55E |
| **Bull** | +6% | 25% | #10B981 |
| **Bear (Counter)** | -2% | 20% | #EF4444 |
| **Extreme Bull** | +10% | 10% | #059669 |

### 3.3 Price Path Generation

```python
def _create_scenario():
    # 1. Calculate target
    target_price = current_price * (1 + target_pct)
    
    # 2. Generate path points
    for i in range(num_points):
        progress = i / num_points
        
        # Non-linear + noise
        noise = np.random.normal(0, atr * 0.2)
        price = current + (target - current) * progress + noise
        
        # Confidence decreases
        confidence = 1.0 - (progress * 0.3)
        
        # Bands widen
        band_width = atr * (1 + progress * 2)
        
        path.append(PricePathPoint(
            timestamp, price, confidence
        ))
```

---

## 4. CHART OBJECT MODEL

### 4.1 ObjectTypes (`visual_objects/models.py` - 277 LOC)

```python
class ObjectType(Enum):
    # Geometry
    TREND_LINE = "trend_line"
    HORIZONTAL_LEVEL = "horizontal_level"
    ZONE = "zone"
    CHANNEL = "channel"
    TRIANGLE = "triangle"
    WEDGE = "wedge"
    RANGE_BOX = "range_box"
    RAY = "ray"
    FIBONACCI = "fibonacci"
    
    # Patterns
    BREAKOUT_PATTERN = "breakout_pattern"
    REVERSAL_PATTERN = "reversal_pattern"
    CONTINUATION_PATTERN = "continuation_pattern"
    COMPRESSION_PATTERN = "compression_pattern"
    
    # Liquidity
    SUPPORT_CLUSTER = "support_cluster"
    RESISTANCE_CLUSTER = "resistance_cluster"
    LIQUIDITY_ZONE = "liquidity_zone"
    IMBALANCE_ZONE = "imbalance_zone"
    INVALIDATION_LINE = "invalidation_line"
    TARGET_BAND = "target_band"
    
    # Hypothesis
    HYPOTHESIS_PATH = "hypothesis_path"
    CONFIDENCE_CORRIDOR = "confidence_corridor"
    SCENARIO_BRANCH = "scenario_branch"
    ENTRY_ZONE = "entry_zone"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    
    # Fractal
    FRACTAL_PROJECTION = "fractal_projection"
    FRACTAL_REFERENCE = "fractal_reference"
    FRACTAL_SIMILARITY_ZONE = "fractal_similarity_zone"
    
    # Indicators
    EMA_SERIES = "ema_series"
    SMA_SERIES = "sma_series"
    VWAP_SERIES = "vwap_series"
    BOLLINGER_BAND = "bollinger_band"
    ATR_BAND = "atr_band"
    RSI_SERIES = "rsi_series"
    MACD_SERIES = "macd_series"
    VOLUME_PROFILE = "volume_profile"
    CUSTOM_INDICATOR = "custom_indicator"
```

### 4.2 ChartObject Model

```python
class ChartObject(BaseModel):
    id: str
    type: ObjectType
    category: ObjectCategory
    symbol: str
    timeframe: str
    
    # Geometry
    points: List[GeometryPoint]       # Line/zone points
    series: List[float]               # Indicator values
    timestamps: List[str]             # Time axis
    
    # Bands
    upper_band: List[float]
    lower_band: List[float]
    middle_band: List[float]
    
    # Style
    style: ObjectStyle
    
    # Meta
    label: str
    confidence: float
    priority: int  # 1-10
```

---

## 5. CHART COMPOSER (`chart_composer/composer.py` - 292 LOC)

### 5.1 Compose Flow

```
compose(
    candles,
    volume,
    patterns,
    support_resistance,
    liquidity_zones,
    indicators,
    hypothesis,
    fractal_matches,
    market_regime
)
    ↓
1. Get preset for regime
2. Convert research → visual objects
    ├── patterns → objects
    ├── S/R → objects
    ├── liquidity → objects
    ├── fractals → objects
    └── hypothesis → objects
3. Filter by priority
4. Limit by max counts
5. Return ComposedChart
```

### 5.2 ComposedChart Response

```python
class ComposedChart(BaseModel):
    symbol: str
    timeframe: str
    market_regime: str
    capital_flow_bias: str
    
    candles: List[Dict]         # OHLCV
    volume: List[Dict]          # Volume bars
    objects: List[Dict]         # Visual objects
    indicators: List[Dict]      # Indicator series
    hypothesis: Dict            # Hypothesis data
    fractal_matches: List[Dict] # Fractal projections
    
    suggested_indicators: List[str]
    active_preset: str
    stats: Dict
```

---

## 6. HYPOTHESIS ENGINE

### 6.1 TAHypothesis Model (`ta_hypothesis_types.py`)

```python
class TAHypothesis(BaseModel):
    direction: TADirection        # LONG/SHORT/NEUTRAL
    setup_quality: float          # 0-1
    setup_type: SetupType         # BREAKOUT/CONTINUATION/REVERSAL
    trend_strength: float         # 0-1
    entry_quality: float          # 0-1
    regime_fit: float             # 0-1
    conviction: float             # 0-1
    regime: MarketRegime          # TREND_UP/DOWN/RANGE
    
    drivers: Dict[str, float]     # trend, momentum, structure, breakout
    
    # Signals
    trend_signal: TrendSignal
    momentum_signal: MomentumSignal
    structure_signal: StructureSignal
    breakout_signal: BreakoutSignal
```

### 6.2 Driver Composition

```python
DRIVER_WEIGHTS = {
    "trend": 0.35,
    "momentum": 0.25,
    "structure": 0.20,
    "breakout": 0.20
}

# Final direction score = weighted sum of drivers
# direction = LONG if score > threshold else SHORT if < -threshold else NEUTRAL
```

---

## 7. STRUCTURE ANALYSIS

### 7.1 Market Structure Detection

| Component | Detection | Output |
|-----------|-----------|--------|
| **Swing Highs** | `_find_swing_highs()` | List of pivot highs |
| **Swing Lows** | `_find_swing_lows()` | List of pivot lows |
| **Higher Highs** | Compare swings | Boolean |
| **Higher Lows** | Compare swings | Boolean |
| **BOS** | `_detect_bos()` | Break of Structure |
| **ChoCh** | `_detect_choch()` | Change of Character |
| **Divergence** | `_detect_divergence()` | RSI/Price divergence |

### 7.2 Structure Score

```python
score = 0.0
if higher_highs: score += 0.25
if higher_lows:  score += 0.25
if both:         score += 0.25
if recent_bos:   score += 0.25

bias = LONG if score > 0.3 else SHORT if score < -0.3 else NEUTRAL
```

---

## 8. BREAKOUT DETECTION

```python
def _compute_breakout():
    range_high = max(highs[-20:])
    range_low = min(lows[-20:])
    
    detected = price > range_high or price < range_low
    
    strength = breakout_distance / range_size
    
    volume_confirmation = current_volume > avg_volume * 1.5
    
    level_quality = tests / 3  # How many times tested
```

---

## 9. API ENDPOINTS (Research)

| Endpoint | Method | Назначение |
|----------|--------|------------|
| `/api/ta-engine/hypothesis/{symbol}` | GET | TA Hypothesis |
| `/api/ta-engine/hypothesis/full/{symbol}` | GET | Full details |
| `/api/v1/chart/full-analysis/{symbol}/{tf}` | GET | Full chart analysis |
| `/api/hypothesis/visualization` | GET | Hypothesis viz data |
| `/api/patterns/detect` | POST | Pattern detection |
| `/api/indicators/calculate` | POST | Indicator calculation |
| `/api/fractal/v2.1/chart` | GET | Fractal chart data |
| `/api/fractal/v2.1/focus-pack` | GET | Focus pack (full) |

---

## 10. RENDERING FLOW (Frontend Expected)

```
Backend Response:
{
  "candles": [...],                    // OHLCV data
  "hypothesis": {
    "direction": "bullish",
    "scenarios": [
      {
        "type": "base",
        "probability": 0.45,
        "expected_path": [              // Price path points
          {"timestamp": "...", "price": 46000, "confidence": 1.0},
          {"timestamp": "...", "price": 47000, "confidence": 0.9},
          ...
        ],
        "upper_band": [46500, 47500, ...],
        "lower_band": [45500, 46500, ...],
        "target_price": 48000,
        "color": "#22C55E"
      }
    ],
    "entry_zone": [45000, 45500],
    "stop_loss": 44000,
    "take_profit": [47000, 49000, 52000]
  },
  "objects": [
    {"type": "support_cluster", "points": [...], "style": {...}},
    {"type": "hypothesis_path", "points": [...], "upper_band": [...]}
  ]
}
```

---

## 11. LOC SUMMARY

| Module | Files | LOC | Status |
|--------|-------|-----|--------|
| `ta_engine` | 6 | ~1,000 | ✅ Core Engine |
| `research_analytics` | 8 | ~1,500 | ✅ Indicators + Patterns |
| `hypothesis_engine` | 12 | ~2,000 | ✅ Multi-source |
| `visual_objects` | 6 | ~800 | ✅ Chart Objects |
| `chart_composer` | 5 | ~600 | ✅ Composition |
| `fractal_intelligence` | 10 | ~1,500 | ✅ Fractal |
| `regime_intelligence_v2` | 15 | ~2,000 | ✅ Regime |
| `alpha_interactions` | 15 | ~2,500 | ✅ Conflicts |
| `validation` | 18 | ~3,000 | ✅ Backtest |
| **TOTAL** | **~95** | **~15,000** | — |

---

## 12. NEXT STEPS

### Missing Indicators to Add:
- CCI (Commodity Channel Index)
- Williams %R
- Ichimoku Cloud
- Parabolic SAR
- Donchian Channels
- Keltner Channels
- TEMA/DEMA
- HMA (Hull MA)

### Missing Patterns to Add:
- Head & Shoulders / Inverse
- Harmonic Patterns (Gartley, Bat, Butterfly)
- Elliott Wave (basic)
- Cup & Handle
- Rounding Bottom/Top

---

*Report: 2026-03-16*
*Scope: /app/backend/modules/ (Research Logic Only)*
*Excluded: Trading Terminal, Execution, Portfolio*
