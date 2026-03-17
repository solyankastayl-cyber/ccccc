# PRD - TA Engine (FOMO Platform)

**Last Updated:** 2026-03-17

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

## Core Features Working
1. Pattern detection (ascending/descending channel, triangle, range)
2. Support/resistance levels with strength %
3. Market structure analysis (HH/HL/LH/LL counts)
4. Setup generation (trigger, invalidation, targets)
5. Timeframe switching (4H → 1Y) with full recalculation
6. Layer visibility controls

## Backlog / P1 Features
- [ ] Pattern geometry rendering on chart (lines visible but small scale)
- [ ] Chart Lab tab functionality
- [ ] Hypotheses tab functionality
- [ ] Save Idea feature
- [ ] Structure markers (BOS/CHOCH) on chart

## P2 Features
- [ ] Multi-asset comparison
- [ ] Push notifications for trigger alerts
- [ ] Historical pattern backtesting
