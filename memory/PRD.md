# PRD - TA Engine (FOMO Platform)

**Last Updated:** March 2026

## Original Problem Statement
Клонировать репозиторий FOMO, поднять bootstrap, работать с модулем теханализа. Реализовать Best-Fit Boundary Selection для правильного выбора anchor points. Исправить проблему с неправильным выбором pivot points для границ паттернов.

## Architecture
- **Backend**: FastAPI + MongoDB (ta_engine module)
- **Frontend**: React + TradingView Lightweight Charts
- **Data**: Coinbase API (live prices + historical data)

## What's Been Implemented

### Session 5: Best-Fit Boundary Selection (March 2026) ✅

**Ключевая доработка P0:**

#### New: Best-Fit Boundary Selection Engine в `pattern_validator_v2.py`

**Проблема (была):**
- Система брала просто первый и последний pivot high/low
- Линии паттерна не проходили через релевантные точки
- Верхняя грань треугольника визуально не сидела на верхних экстремумах

**Решение (реализовано):**

1. **generate_line_candidates()** — генерирует ВСЕ комбинации линий из pivot points
2. **score_trendline()** — скоринг каждой линии:
   - +2 за каждое касание свечи
   - +3 за каждое подтверждение pivot
   - -4 за каждое пробитие свечой
   - +bonus за time span (более длинные паттерны)
3. **find_best_line()** — выбирает линию с лучшим score

**Pipeline теперь:**
```
candles → pivots → candidate_lines → best_fit_selection → pattern_validation → render
```

**Результаты:**
- BTC 1D: Symmetrical Triangle, confidence 0.85
- Line Scores: upper=17.0, lower=10.4
- 100% тестов пройдено
- Детерминистический алгоритм (одинаковые результаты при повторных запросах)

#### Параметры:
- `TOUCH_TOLERANCE = 0.008` (0.8%)
- `MIN_PIVOT_DISTANCE = 10` (минимум 10 свечей между pivot points)
- `PRICE_CONTAINMENT_RATIO = 0.70` (70%)
- `pattern_window = 120` для 1D (локальный паттерн ~4 месяца)

### Предыдущие сессии
- Pattern Validation Engine v2 с strict per-pattern validators
- Descending/Ascending/Symmetrical Triangle validators
- Channel pattern validator
- ResearchChart component с pattern geometry rendering

## Core Features Working
1. Pattern detection with Best-Fit Boundary Selection ✅
2. Support/resistance levels with strength %
3. Market structure analysis (HH/HL/LH/LL counts)
4. Setup generation (trigger, invalidation, targets)
5. Timeframe switching (4H, 1D, 7D, 30D)
6. Asset switching (BTC/ETH/SOL)
7. Coinbase provider connected

## API Endpoints
- `GET /api/ta/setup?symbol=BTC&tf=1D` — Main TA setup endpoint
- `GET /api/ta/debug?symbol=BTC&tf=1D` — Debug endpoint
- `GET /api/health` — Health check

## Test Results
- Backend: 100% (11/11 tests passed)
- Test files: `/app/backend/ta_engine_test.py`, `/app/backend/ta_edge_case_test.py`

## Backlog / P1 Features
- [ ] Zoom-to-pattern button (auto-scale chart to pattern area)
- [ ] Fix Preview URL routing (temporary platform issue)
- [ ] Structure markers (BOS/CHOCH) on chart
- [ ] Chart Lab tab functionality
- [ ] Hypotheses tab functionality
- [ ] Save Idea feature

## P2 Features
- [ ] Auto TA mode (show only strongest elements)
- [ ] Multi-asset comparison
- [ ] Push notifications for trigger alerts
- [ ] Historical pattern backtesting
- [ ] AI explanation layer (почему именно этот паттерн)

## Next Steps
1. Визуальная проверка паттерна на chart (когда Preview URL доступен)
2. Confluence-driven pattern selection (из нескольких паттернов показываем лучший)
3. Zoom-to-pattern функциональность
