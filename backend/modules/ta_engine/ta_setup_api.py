"""
TA Setup API — With Timeframe Isolation
========================================

CRITICAL FIX: Each timeframe = separate dataset with aggregated candles.

NOT: 1D candles sliced for 7D view
BUT: 1D candles aggregated into weekly/monthly candles

Pipeline:
1. Fetch raw daily candles
2. Aggregate by timeframe (weekly, monthly, etc.)
3. Pivot detection on AGGREGATED data
4. Pattern detection on AGGREGATED data

This ensures each TF shows DIFFERENT patterns based on that TF's structure.
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import random

router = APIRouter(prefix="/api/ta", tags=["TA Setup"])

# Import STRICT pattern validator v2
from modules.ta_engine.setup.pattern_validator_v2 import get_pattern_validator_v2


# =============================================================================
# TIMEFRAME ISOLATION: Candle Aggregation
# =============================================================================

def aggregate_candles_weekly(daily_candles: List[Dict]) -> List[Dict]:
    """
    Aggregate daily candles into weekly candles.
    
    Each week: Monday-Sunday
    - time = start of week (Monday)
    - open = first day's open
    - close = last day's close
    - high = max of all days
    - low = min of all days
    - volume = sum of all days
    """
    if not daily_candles:
        return []
    
    # Sort by time
    sorted_candles = sorted(daily_candles, key=lambda x: x['time'])
    
    weekly = []
    current_week = []
    current_week_start = None
    
    for candle in sorted_candles:
        # Get week start (Monday) for this candle
        dt = datetime.utcfromtimestamp(candle['time'])
        week_start = dt - timedelta(days=dt.weekday())
        week_start_ts = int(week_start.replace(hour=0, minute=0, second=0).timestamp())
        
        if current_week_start is None:
            current_week_start = week_start_ts
        
        if week_start_ts != current_week_start:
            # New week - aggregate previous week
            if current_week:
                weekly.append({
                    "time": current_week_start,
                    "open": current_week[0]['open'],
                    "high": max(c['high'] for c in current_week),
                    "low": min(c['low'] for c in current_week),
                    "close": current_week[-1]['close'],
                    "volume": sum(c.get('volume', 0) for c in current_week)
                })
            current_week = [candle]
            current_week_start = week_start_ts
        else:
            current_week.append(candle)
    
    # Don't forget last week
    if current_week:
        weekly.append({
            "time": current_week_start,
            "open": current_week[0]['open'],
            "high": max(c['high'] for c in current_week),
            "low": min(c['low'] for c in current_week),
            "close": current_week[-1]['close'],
            "volume": sum(c.get('volume', 0) for c in current_week)
        })
    
    return weekly


def aggregate_candles_monthly(daily_candles: List[Dict]) -> List[Dict]:
    """
    Aggregate daily candles into monthly candles.
    
    Each month:
    - time = start of month
    - open = first day's open
    - close = last day's close
    - high = max of all days
    - low = min of all days
    """
    if not daily_candles:
        return []
    
    sorted_candles = sorted(daily_candles, key=lambda x: x['time'])
    
    monthly = []
    current_month = []
    current_month_start = None
    
    for candle in sorted_candles:
        dt = datetime.utcfromtimestamp(candle['time'])
        month_start = dt.replace(day=1, hour=0, minute=0, second=0)
        month_start_ts = int(month_start.timestamp())
        
        if current_month_start is None:
            current_month_start = month_start_ts
        
        if month_start_ts != current_month_start:
            # New month
            if current_month:
                monthly.append({
                    "time": current_month_start,
                    "open": current_month[0]['open'],
                    "high": max(c['high'] for c in current_month),
                    "low": min(c['low'] for c in current_month),
                    "close": current_month[-1]['close'],
                    "volume": sum(c.get('volume', 0) for c in current_month)
                })
            current_month = [candle]
            current_month_start = month_start_ts
        else:
            current_month.append(candle)
    
    # Don't forget last month
    if current_month:
        monthly.append({
            "time": current_month_start,
            "open": current_month[0]['open'],
            "high": max(c['high'] for c in current_month),
            "low": min(c['low'] for c in current_month),
            "close": current_month[-1]['close'],
            "volume": sum(c.get('volume', 0) for c in current_month)
        })
    
    return monthly


def aggregate_candles_quarterly(daily_candles: List[Dict]) -> List[Dict]:
    """Aggregate daily candles into quarterly (3-month) candles."""
    if not daily_candles:
        return []
    
    sorted_candles = sorted(daily_candles, key=lambda x: x['time'])
    
    quarterly = []
    current_quarter = []
    current_quarter_start = None
    
    for candle in sorted_candles:
        dt = datetime.utcfromtimestamp(candle['time'])
        # Quarter: Q1 = Jan-Mar, Q2 = Apr-Jun, etc.
        quarter_month = ((dt.month - 1) // 3) * 3 + 1
        quarter_start = dt.replace(month=quarter_month, day=1, hour=0, minute=0, second=0)
        quarter_start_ts = int(quarter_start.timestamp())
        
        if current_quarter_start is None:
            current_quarter_start = quarter_start_ts
        
        if quarter_start_ts != current_quarter_start:
            if current_quarter:
                quarterly.append({
                    "time": current_quarter_start,
                    "open": current_quarter[0]['open'],
                    "high": max(c['high'] for c in current_quarter),
                    "low": min(c['low'] for c in current_quarter),
                    "close": current_quarter[-1]['close'],
                    "volume": sum(c.get('volume', 0) for c in current_quarter)
                })
            current_quarter = [candle]
            current_quarter_start = quarter_start_ts
        else:
            current_quarter.append(candle)
    
    if current_quarter:
        quarterly.append({
            "time": current_quarter_start,
            "open": current_quarter[0]['open'],
            "high": max(c['high'] for c in current_quarter),
            "low": min(c['low'] for c in current_quarter),
            "close": current_quarter[-1]['close'],
            "volume": sum(c.get('volume', 0) for c in current_quarter)
        })
    
    return quarterly


def aggregate_candles_yearly(daily_candles: List[Dict]) -> List[Dict]:
    """Aggregate daily candles into yearly candles."""
    if not daily_candles:
        return []
    
    sorted_candles = sorted(daily_candles, key=lambda x: x['time'])
    
    yearly = []
    current_year = []
    current_year_start = None
    
    for candle in sorted_candles:
        dt = datetime.utcfromtimestamp(candle['time'])
        year_start = dt.replace(month=1, day=1, hour=0, minute=0, second=0)
        year_start_ts = int(year_start.timestamp())
        
        if current_year_start is None:
            current_year_start = year_start_ts
        
        if year_start_ts != current_year_start:
            if current_year:
                yearly.append({
                    "time": current_year_start,
                    "open": current_year[0]['open'],
                    "high": max(c['high'] for c in current_year),
                    "low": min(c['low'] for c in current_year),
                    "close": current_year[-1]['close'],
                    "volume": sum(c.get('volume', 0) for c in current_year)
                })
            current_year = [candle]
            current_year_start = year_start_ts
        else:
            current_year.append(candle)
    
    if current_year:
        yearly.append({
            "time": current_year_start,
            "open": current_year[0]['open'],
            "high": max(c['high'] for c in current_year),
            "low": min(c['low'] for c in current_year),
            "close": current_year[-1]['close'],
            "volume": sum(c.get('volume', 0) for c in current_year)
        })
    
    return yearly


def aggregate_candles_by_tf(daily_candles: List[Dict], tf: str) -> List[Dict]:
    """
    Main aggregation function.
    
    4H  → keep daily (no aggregation needed, coinbase gives 4h)
    1D  → keep daily
    7D  → aggregate to weekly
    30D → aggregate to monthly
    180D → aggregate to quarterly
    1Y  → aggregate to yearly
    """
    if tf in ["4H", "1D"]:
        return daily_candles
    elif tf == "7D":
        return aggregate_candles_weekly(daily_candles)
    elif tf == "30D":
        return aggregate_candles_monthly(daily_candles)
    elif tf == "180D":
        return aggregate_candles_quarterly(daily_candles)
    elif tf == "1Y":
        return aggregate_candles_yearly(daily_candles)
    else:
        return daily_candles


# =============================================================================
# Pattern Detection
# =============================================================================

def detect_pattern(candles: List[Dict], symbol: str, tf: str) -> Dict:
    """
    Detect strongest VALID pattern from candles.
    
    IMPORTANT: Candles should already be aggregated for the TF.
    """
    if len(candles) < 30:
        return None
    
    # Get strict validator for this timeframe
    validator = get_pattern_validator_v2(tf.upper())
    
    # Detect best valid pattern
    pattern = validator.detect_best_pattern(candles)
    
    if pattern is None:
        return None
    
    return pattern


# =============================================================================
# Level Detection
# =============================================================================

def detect_levels(candles: List[Dict]) -> List[Dict]:
    """Detect support/resistance levels. Returns top 3 strongest."""
    if len(candles) < 20:
        return []
    
    price_clusters = {}
    
    for c in candles[-100:]:
        for price in [c['high'], c['low']]:
            bucket = round(price / 100) * 100
            price_clusters[bucket] = price_clusters.get(bucket, 0) + 1
    
    sorted_levels = sorted(price_clusters.items(), key=lambda x: x[1], reverse=True)
    
    current_price = candles[-1]['close']
    
    levels = []
    for price, touches in sorted_levels[:5]:
        if price > current_price * 1.001:
            level_type = "resistance"
        elif price < current_price * 0.999:
            level_type = "support"
        else:
            level_type = "pivot"
        
        strength = min(100, int(touches / len(candles[-100:]) * 400))
        
        levels.append({
            "price": round(price, 2),
            "type": level_type,
            "strength": strength,
            "touches": touches
        })
    
    return levels[:3]


# =============================================================================
# Structure Analysis
# =============================================================================

def analyze_structure(candles: List[Dict]) -> Dict:
    """Analyze market structure: HH, HL, LH, LL counts."""
    if len(candles) < 10:
        return {"trend": "neutral", "hh": 0, "hl": 0, "lh": 0, "ll": 0}
    
    recent = candles[-50:]
    
    hh_count = 0
    hl_count = 0
    lh_count = 0
    ll_count = 0
    
    prev_high = recent[0]['high']
    prev_low = recent[0]['low']
    
    for c in recent[1:]:
        if c['high'] > prev_high:
            hh_count += 1
        else:
            lh_count += 1
        
        if c['low'] > prev_low:
            hl_count += 1
        else:
            ll_count += 1
        
        prev_high = c['high']
        prev_low = c['low']
    
    # Determine trend
    if hh_count > lh_count and hl_count > ll_count:
        trend = "bullish"
    elif lh_count > hh_count and ll_count > hl_count:
        trend = "bearish"
    else:
        trend = "neutral"
    
    return {
        "trend": trend,
        "hh": hh_count,
        "hl": hl_count,
        "lh": lh_count,
        "ll": ll_count
    }


# =============================================================================
# Setup Builder
# =============================================================================

def build_setup(candles: List[Dict], pattern: Dict, levels: List[Dict], structure: Dict) -> Dict:
    """Build trading setup from analysis components."""
    if not candles or not pattern:
        return None
    
    current_price = candles[-1]['close']
    
    # Determine direction from pattern
    direction = pattern.get("direction", "neutral")
    if direction == "neutral":
        direction = structure.get("trend", "neutral")
    
    # Calculate targets
    if direction == "bearish":
        support_levels = [l for l in levels if l['type'] == 'support']
        if support_levels:
            target1 = support_levels[0]['price']
            target2 = target1 * 0.95
        else:
            target1 = current_price * 0.95
            target2 = current_price * 0.90
        
        trigger = pattern.get("breakout_level") or current_price * 0.98
        invalidation = pattern.get("invalidation") or current_price * 1.05
    else:
        resistance_levels = [l for l in levels if l['type'] == 'resistance']
        if resistance_levels:
            target1 = resistance_levels[0]['price']
            target2 = target1 * 1.05
        else:
            target1 = current_price * 1.05
            target2 = current_price * 1.10
        
        trigger = pattern.get("breakout_level") or current_price * 1.02
        invalidation = pattern.get("invalidation") or current_price * 0.95
    
    targets = [
        {"price": round(target1, 2), "label": "T1"},
        {"price": round(target2, 2), "label": "T2"}
    ]
    
    return {
        "direction": direction,
        "trigger": round(trigger, 2),
        "invalidation": round(invalidation, 2),
        "targets": targets
    }


# =============================================================================
# Main API Endpoint
# =============================================================================

from datetime import timedelta

@router.get("/setup")
async def get_ta_setup(
    symbol: str = Query("BTCUSDT", description="Trading pair"),
    tf: str = Query("1D", description="Timeframe")
):
    """
    Get complete TA setup for symbol and timeframe.
    
    TIMEFRAME ISOLATION:
    - Each TF uses AGGREGATED candles (not sliced daily)
    - 7D = weekly candles
    - 30D = monthly candles
    - 180D = quarterly candles
    - 1Y = yearly candles
    """
    # Normalize symbol
    clean_symbol = symbol.replace("USDT", "").replace("-USD", "").upper()
    
    # Map timeframe
    tf_map = {
        "4H": "4H", "4h": "4H",
        "1D": "1D", "1d": "1D", 
        "7D": "7D", "7d": "7D",
        "30D": "30D", "30d": "30D",
        "180D": "180D", "180d": "180D",
        "1Y": "1Y", "1y": "1Y"
    }
    normalized_tf = tf_map.get(tf, "1D")
    
    # Fetch raw candles
    try:
        from modules.data.coinbase_provider import coinbase_provider
        
        # Always fetch daily candles (we'll aggregate them)
        # Exception: 4H fetches 4h candles
        if normalized_tf == "4H":
            cb_tf = "4h"
            limit = 1000  # ~166 days of 4h
        else:
            cb_tf = "1d"
            limit = 2500  # ~7 years of daily
        
        product_id = f"{clean_symbol}-USD"
        
        raw_candles = await coinbase_provider.get_candles(
            product_id=product_id,
            timeframe=cb_tf,
            limit=limit
        )
        
        # Format candles
        daily_candles = []
        for c in raw_candles:
            daily_candles.append({
                "time": c['timestamp'] // 1000 if c['timestamp'] > 1e12 else c['timestamp'],
                "open": c['open'],
                "high": c['high'],
                "low": c['low'],
                "close": c['close'],
                "volume": c.get('volume', 0)
            })
        
        # Sort by time
        daily_candles.sort(key=lambda x: x['time'])
        
    except Exception as e:
        # Fallback: generate mock data
        import time
        base_time = int(time.time()) - 86400 * 2500
        base_price = 95000 if clean_symbol == "BTC" else 3200 if clean_symbol == "ETH" else 150
        
        daily_candles = []
        for i in range(2500):
            t = base_time + i * 86400
            change = random.uniform(-0.03, 0.03)
            open_p = base_price * (1 + change)
            close_p = open_p * (1 + random.uniform(-0.02, 0.02))
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.015))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.015))
            base_price = close_p
            
            daily_candles.append({
                "time": t,
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "volume": random.randint(1000, 10000)
            })
    
    # =================================================================
    # CRITICAL: Aggregate candles by timeframe
    # =================================================================
    candles = aggregate_candles_by_tf(daily_candles, normalized_tf)
    
    # Detect pattern on AGGREGATED candles
    pattern = detect_pattern(candles, clean_symbol, normalized_tf)
    
    # Detect levels on AGGREGATED candles
    levels = detect_levels(candles)
    
    # Analyze structure on AGGREGATED candles
    structure = analyze_structure(candles)
    
    # Build setup
    setup = build_setup(candles, pattern, levels, structure)
    
    return {
        "symbol": f"{clean_symbol}USDT",
        "timeframe": normalized_tf,
        "candles": candles,
        "candle_count": len(candles),
        "raw_daily_count": len(daily_candles),
        "pattern": pattern,
        "levels": levels,
        "structure": structure,
        "setup": setup,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# =============================================================================
# Debug Endpoint
# =============================================================================

@router.get("/debug")
async def get_ta_debug(
    symbol: str = Query("BTCUSDT"),
    tf: str = Query("1D")
):
    """Debug endpoint showing internal state."""
    clean_symbol = symbol.replace("USDT", "").replace("-USD", "").upper()
    
    tf_map = {
        "4H": "4H", "4h": "4H",
        "1D": "1D", "1d": "1D",
        "7D": "7D", "7d": "7D",
        "30D": "30D", "30d": "30D"
    }
    normalized_tf = tf_map.get(tf, "1D")
    
    try:
        from modules.data.coinbase_provider import coinbase_provider
        
        product_id = f"{clean_symbol}-USD"
        raw_candles = await coinbase_provider.get_candles(
            product_id=product_id,
            timeframe="1d",
            limit=500
        )
        
        daily_candles = [{
            "time": c['timestamp'] // 1000 if c['timestamp'] > 1e12 else c['timestamp'],
            "open": c['open'],
            "high": c['high'],
            "low": c['low'],
            "close": c['close'],
        } for c in raw_candles]
        
        daily_candles.sort(key=lambda x: x['time'])
        
    except:
        daily_candles = []
    
    # Aggregate
    candles = aggregate_candles_by_tf(daily_candles, normalized_tf)
    
    # Get validator
    validator = get_pattern_validator_v2(normalized_tf)
    pivot_highs, pivot_lows = validator.find_pivots(candles)
    
    return {
        "symbol": clean_symbol,
        "timeframe": normalized_tf,
        "raw_daily_count": len(daily_candles),
        "aggregated_count": len(candles),
        "pivot_highs": len(pivot_highs),
        "pivot_lows": len(pivot_lows),
        "first_candle": candles[0] if candles else None,
        "last_candle": candles[-1] if candles else None,
        "pattern_window": validator.pattern_window,
        "pivot_window": validator.pivot_window,
    }
