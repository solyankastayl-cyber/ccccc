# PRD - TA Engine (FOMO Platform)

**Last Updated:** December 2025

## Original Problem Statement
Клонировать репозиторий FOMO, поднять bootstrap, работать с модулем теханализа. Исправить разорванную логику между backend setup engine и chart renderer.

## Architecture
- **Backend**: FastAPI + MongoDB (ta_engine module)
- **Frontend**: React + TradingView Lightweight Charts
- **Data**: Coinbase API (live prices + historical data)

## What's Been Implemented

### Session 1: Initial Setup
- Cloned repo, executed bootstrap
- TA Engine v14.2 with 15 indicators, 14 patterns
- Coinbase provider connected (BTC/ETH/SOL)
- Full historical data (2500+ daily candles since 2019)

### Session 2: Backend-Frontend Integration Fix
- **ResearchChart**: Now renders pattern geometry (upper/lower trendlines)
- **Pattern Detection**: 100-day window with linear regression for trend detection
- **Data Mapping**: Unified setup object for all UI components
- **Layer Controls**: Patterns/Levels/Structure/Targets toggles working
- **Consistency**: Debug panel, Detected Elements, and chart now read same data source

### Session 3: Backend Architecture Audit (December 2025)
- **Full Audit Document**: `/app/memory/TA_ENGINE_AUDIT.md`
- Documented all pattern detection algorithms
- Documented structure engine, level engine, indicator engine
- Documented setup builder confluence scoring system

### Session 4: Pattern Validation Engine (December 2025)
**Implemented PIVOT-BASED pattern detection with strict validation:**

#### New: `pattern_validation_engine.py`
- **Pivot detection**: Window-based swing high/low detection (5 candles for 1D)
- **Line building**: Trendlines built ONLY from pivot points
- **Validation**:
  - Minimum 3 touches required
  - Parallel check for channels (±15% slope difference)
  - 1.5% tolerance for touch detection
  - Price must be inside pattern
- **Fail-safe**: Returns `None` if no valid pattern (better than garbage)

#### Results:
- BTC 1D: Descending Triangle 85% (16 touches)
- ETH 1D: Descending Triangle 85%
- 30D: No valid pattern (fail-safe works)

#### Key changes:
- Replaced random confidence with touch-based confidence
- Timeframe-aware pivot windows (4H=3, 1D=5, 7D=7...)
- Triangle vs Channel differentiation (converging vs parallel)

## Core Features Working
1. Pattern detection (ascending/descending channel, triangle, range)
2. Support/resistance levels with strength %
3. Market structure analysis (HH/HL/LH/LL counts)
4. Setup generation (trigger, invalidation, targets)
5. Timeframe switching (1D supported, 4H requires Coinbase config)
6. Mode switching (Research/Hypothesis/Trading)
7. Asset switching (BTC/ETH/SOL)
8. Projection path with confidence corridor

## Known Issues (Non-Critical)
- Layer toggle buttons need debugging (click handler may not be firing)
- 4H timeframe returns empty (Coinbase provider limitation)

## Backlog / P1 Features
- [ ] Fix layer toggle buttons
- [ ] Zoom-to-pattern button (auto-scale chart to pattern area)
- [ ] Chart Lab tab functionality
- [ ] Hypotheses tab functionality
- [ ] Save Idea feature
- [ ] Structure markers (BOS/CHOCH) on chart

## P2 Features
- [ ] Auto TA mode (show only strongest elements)
- [ ] Multi-asset comparison
- [ ] Push notifications for trigger alerts
- [ ] Historical pattern backtesting
- [ ] 4H timeframe support (Coinbase config)
