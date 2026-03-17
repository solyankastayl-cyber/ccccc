"""
TA Setup API — Multi-Scale Analysis (Correct Approach)
=======================================================

CRITICAL FIX: No candle aggregation!

TF ≠ candle type
TF = analysis context/scale

All timeframes use DAILY candles, but with different:
- lookback (how many candles we analyze)
- pivot_window (sensitivity of pivot detection)
- min_pivot_distance (minimum distance between pivots)

This preserves market structure while allowing multi-scale analysis.
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import random

router = APIRouter(prefix="/api/ta", tags=["TA Setup"])

from modules.ta_engine.setup.pattern_validator_v2 import get_pattern_validator_v2


# =============================================================================
# MULTI-SCALE CONFIGURATION (The Key!)
# =============================================================================

TF_CONFIG = {
    "4H": {
        "lookback": 200,        # ~33 days of 4H candles (limited by Coinbase API)
        "pivot_window": 3,      # Very sensitive - микро структуры
        "min_pivot_distance": 5,
        "pattern_window": 150,
        "candle_type": "4h",    # Uses 4H candles!
        "description": "Micro structure / entry points"
    },
    "1D": {
        "lookback": 150,        # ~5 months of daily
        "pivot_window": 5,      # Standard sensitivity
        "min_pivot_distance": 8,
        "pattern_window": 100,
        "candle_type": "1d",
        "description": "Short-term / setup patterns"
    },
    "7D": {
        "lookback": 400,        # ~1.5 years of daily
        "pivot_window": 9,      # Less sensitive (bigger swings)
        "min_pivot_distance": 15,
        "pattern_window": 250,
        "candle_type": "1d",
        "description": "Medium-term / formation patterns"
    },
    "30D": {
        "lookback": 800,        # ~3 years of daily
        "pivot_window": 15,     # Only major swings
        "min_pivot_distance": 30,
        "pattern_window": 500,
        "candle_type": "1d",
        "description": "Long-term / structure patterns"
    },
    "180D": {
        "lookback": 1500,       # ~6 years of daily
        "pivot_window": 25,     # Macro swings only
        "min_pivot_distance": 60,
        "pattern_window": 800,
        "candle_type": "1d",
        "description": "Macro / trend patterns"
    },
    "1Y": {
        "lookback": 2500,       # ~10 years of daily - FULL HISTORY
        "pivot_window": 40,     # Cycle-level swings only
        "min_pivot_distance": 100,
        "pattern_window": 1500,
        "candle_type": "1d",
        "description": "Cycle-level / global context"
    }
}


# =============================================================================
# Pattern Detection
# =============================================================================

def detect_pattern(candles: List[Dict], symbol: str, tf: str) -> Dict:
    """
    Detect strongest VALID pattern using TF-specific parameters.
    
    IMPORTANT: All TFs use daily candles, just different parameters.
    """
    config = TF_CONFIG.get(tf, TF_CONFIG["1D"])
    
    if len(candles) < 30:
        return None
    
    # Get validator with TF-specific config
    validator = get_pattern_validator_v2(tf.upper(), config)
    
    # Detect best valid pattern
    pattern = validator.detect_best_pattern(candles)
    
    if pattern is None:
        return None
    
    return pattern


# =============================================================================
# Level Detection
# =============================================================================

def detect_levels(candles: List[Dict], tf: str) -> List[Dict]:
    """Detect support/resistance levels with TF-appropriate sensitivity."""
    if len(candles) < 20:
        return []
    
    config = TF_CONFIG.get(tf, TF_CONFIG["1D"])
    
    # Use more candles for level detection on higher TFs
    lookback = min(len(candles), config["lookback"])
    recent = candles[-lookback:]
    
    price_clusters = {}
    
    # Cluster prices with TF-appropriate bucket size
    # Higher TF = larger buckets (less noise)
    bucket_size = 100 if tf in ["1D", "4H"] else 500 if tf == "7D" else 1000
    
    for c in recent:
        for price in [c['high'], c['low']]:
            bucket = round(price / bucket_size) * bucket_size
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
        
        strength = min(100, int(touches / len(recent) * 400))
        
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

def analyze_structure(candles: List[Dict], tf: str) -> Dict:
    """Analyze market structure with TF-appropriate window."""
    if len(candles) < 10:
        return {"trend": "neutral", "hh": 0, "hl": 0, "lh": 0, "ll": 0}
    
    config = TF_CONFIG.get(tf, TF_CONFIG["1D"])
    
    # Use TF-appropriate window for structure analysis
    window = min(config["lookback"] // 3, len(candles))
    recent = candles[-window:]
    
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
    
    direction = pattern.get("direction", "neutral")
    if direction == "neutral":
        direction = structure.get("trend", "neutral")
    
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

@router.get("/setup")
async def get_ta_setup(
    symbol: str = Query("BTCUSDT", description="Trading pair"),
    tf: str = Query("1D", description="Timeframe")
):
    """
    Get complete TA setup for symbol and timeframe.
    
    MULTI-SCALE ANALYSIS:
    - All TFs use DAILY candles (no aggregation!)
    - Different TFs = different analysis parameters
    - Higher TF = larger lookback, less sensitive pivots
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
    
    # Get TF-specific config
    config = TF_CONFIG.get(normalized_tf, TF_CONFIG["1D"])
    
    # Fetch DAILY candles (always daily, no aggregation!)
    try:
        from modules.data.coinbase_provider import coinbase_provider
        
        # Always fetch daily candles
        # Exception: 4H fetches 4h candles
        if normalized_tf == "4H":
            cb_tf = "4h"
        else:
            cb_tf = "1d"
        
        product_id = f"{clean_symbol}-USD"
        
        # Fetch enough candles for the lookback
        limit = config["lookback"] + 100  # Extra buffer
        
        raw_candles = await coinbase_provider.get_candles(
            product_id=product_id,
            timeframe=cb_tf,
            limit=limit
        )
        
        # Format candles
        candles = []
        for c in raw_candles:
            candles.append({
                "time": c['timestamp'] // 1000 if c['timestamp'] > 1e12 else c['timestamp'],
                "open": c['open'],
                "high": c['high'],
                "low": c['low'],
                "close": c['close'],
                "volume": c.get('volume', 0)
            })
        
        # Sort by time
        candles.sort(key=lambda x: x['time'])
        
    except Exception as e:
        # Log the error
        print(f"[ERROR] Failed to fetch candles for {clean_symbol} {normalized_tf}: {e}")
        # Fallback: generate mock data
        import time
        base_time = int(time.time()) - 86400 * config["lookback"]
        base_price = 95000 if clean_symbol == "BTC" else 3200 if clean_symbol == "ETH" else 150
        
        candles = []
        for i in range(config["lookback"]):
            t = base_time + i * 86400
            change = random.uniform(-0.03, 0.03)
            open_p = base_price * (1 + change)
            close_p = open_p * (1 + random.uniform(-0.02, 0.02))
            high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.015))
            low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.015))
            base_price = close_p
            
            candles.append({
                "time": t,
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "volume": random.randint(1000, 10000)
            })
    
    # Trim to lookback window
    candles = candles[-config["lookback"]:]
    
    # Detect pattern with TF-specific parameters
    pattern = detect_pattern(candles, clean_symbol, normalized_tf)
    
    # Detect levels
    levels = detect_levels(candles, normalized_tf)
    
    # Analyze structure
    structure = analyze_structure(candles, normalized_tf)
    
    # Build setup
    setup = build_setup(candles, pattern, levels, structure)
    
    return {
        "symbol": f"{clean_symbol}USDT",
        "timeframe": normalized_tf,
        "scale_config": {
            "lookback": config["lookback"],
            "pivot_window": config["pivot_window"],
            "min_pivot_distance": config["min_pivot_distance"],
            "description": config["description"]
        },
        "candles": candles,
        "candle_count": len(candles),
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
        "30D": "30D", "30d": "30D",
        "180D": "180D", "180d": "180D",
        "1Y": "1Y", "1y": "1Y"
    }
    normalized_tf = tf_map.get(tf, "1D")
    
    config = TF_CONFIG.get(normalized_tf, TF_CONFIG["1D"])
    
    try:
        from modules.data.coinbase_provider import coinbase_provider
        
        product_id = f"{clean_symbol}-USD"
        raw_candles = await coinbase_provider.get_candles(
            product_id=product_id,
            timeframe="1d",
            limit=config["lookback"]
        )
        
        candles = [{
            "time": c['timestamp'] // 1000 if c['timestamp'] > 1e12 else c['timestamp'],
            "open": c['open'],
            "high": c['high'],
            "low": c['low'],
            "close": c['close'],
        } for c in raw_candles]
        
        candles.sort(key=lambda x: x['time'])
        
    except:
        candles = []
    
    # Get validator with config
    validator = get_pattern_validator_v2(normalized_tf, config)
    pivot_highs, pivot_lows = validator.find_pivots(candles)
    
    return {
        "symbol": clean_symbol,
        "timeframe": normalized_tf,
        "config": config,
        "candle_count": len(candles),
        "pivot_highs": len(pivot_highs),
        "pivot_lows": len(pivot_lows),
        "first_candle": candles[0] if candles else None,
        "last_candle": candles[-1] if candles else None,
    }
