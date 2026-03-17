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

### Session 4: Pattern Validation Engine v2 (December 2025)
**Implemented STRICT per-pattern validators:**

#### New: `pattern_validator_v2.py`
- **Separate validators** for each pattern type:
  - `validate_descending_triangle()`: Upper descending + Lower horizontal + 2+ pivot touches + narrowing + 70% containment
  - `validate_ascending_triangle()`: Upper horizontal + Lower ascending + same validation
  - `validate_symmetrical_triangle()`: Upper descending + Lower ascending + slope symmetry
  - `validate_channel()`: Parallel slopes + no narrowing
- **Strict criteria**: If ANY validation fails → return `None`
- **Quality-based confidence**: Based on touches, containment, slope quality (not random)

#### Results:
- BTC 1D: Symmetrical Triangle 85%, 4 touches, 100% containment
- 30D: **No valid pattern** (fail-safe works!)
- No more vertical line artifacts

#### Known limitation:
- Pattern lines not visible on full chart (2019-2026 scale)
- Need zoom-to-pattern feature (P1)

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
