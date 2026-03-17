# FOMO Platform - TA Engine Module PRD

## Original Problem Statement
Клонировать репозиторий, поднять bootstrap, работать только с модулем теханализа.
Research page должна быть Technical Analysis Workspace, не Trading Terminal.

## Architecture Rule - 3 Independent Modes

### Mode 1 — Research (CURRENT)
**Purpose:** Pure technical analysis workspace
- Chart
- Patterns
- Levels
- Structure  
- Confluence
- Technical bias
- Idea save/share

**NOT allowed:**
- Entry/Stop/TP as dominant UI
- Trading terminal semantics
- Order execution logic

### Mode 2 — Trading Terminal (Separate)
- Execution
- Risk management
- Position sizing

### Mode 3 — Admin/System Control (Separate)
- Monitoring
- Health checks
- Configuration

## What's Been Implemented

### 2026-03-17 - Research Pipeline Complete

#### New Backend Endpoint
```
GET /api/ta/setup?symbol=BTCUSDT&tf=1D
```

**Response format:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1D",
  "candles": [...],
  "pattern": {
    "type": "ascending_channel",
    "confidence": 0.79,
    "points": {...}
  },
  "levels": [
    { "type": "resistance", "price": 97963, "strength": 0.82 },
    { "type": "support", "price": 60001, "strength": 0.76 }
  ],
  "structure": {
    "trend": "bearish",
    "hh": 1, "hl": 0, "lh": 4, "ll": 3
  },
  "setup": {
    "direction": "bullish",
    "confidence": 0.69,
    "trigger": 97963,
    "invalidation": 60001,
    "targets": [116944, 135926]
  }
}
```

#### Frontend Components
- `ResearchChart.jsx` - Clean chart without trading semantics
- `ResearchViewNew.jsx` - Research workspace with debug panel

#### Debug Panel
Shows real-time:
- Pattern + Confidence
- Levels count + Structure trend
- Direction + Setup confidence
- Trigger + Invalidation
- Targets
- Timeframe + Candles count

## Pipeline Flow

```
[USER SELECT]
   ↓
/api/ta/setup?symbol=X&tf=Y
   ↓
[TA ENGINE]
   - Pattern detection
   - Level detection
   - Structure analysis
   - Setup builder
   ↓
[CHART RENDER]
   - Candles
   - Pattern overlay
   - Levels (thin lines)
   - Bias badge
```

## Visual Priority Model

**Priority A (Always visible):**
- Strongest pattern
- Bias badge
- Support/Resistance

**Priority B (Optional):**
- Fib
- Liquidity
- Secondary patterns

**Priority C (Hidden by default):**
- Trade execution helpers
- Entry/Stop/Targets as thin reference only

## Renaming for Research Mode
| Trading Term | Research Term |
|--------------|---------------|
| Entry | Trigger Level |
| Stop | Invalidation Level |
| TP1/TP2 | Target Zone 1/2 |

## Test Results
- Backend: 100%
- Frontend: 95%
- Pipeline: Working end-to-end

## URLs
- Frontend: https://tech-analyzer-10.preview.emergentagent.com
- API: https://tech-analyzer-10.preview.emergentagent.com/api

## Backlog

### P0 (Done)
- [x] Clean Research pipeline
- [x] Debug panel
- [x] Remove trading semantics

### P1 (Next)
- [ ] Pattern line overlays on chart
- [ ] Improve pattern detection accuracy
- [ ] Add explanation block

### P2 (Future)
- [ ] AI-powered analysis
- [ ] Idea library
- [ ] Share functionality
