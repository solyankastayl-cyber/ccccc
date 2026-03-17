"""
Pattern Validation Engine v2
=============================

STRICT per-pattern validators with real geometric validation.

Rules:
1. Each pattern type has its own validator with specific requirements
2. If ANY requirement fails → return None (no garbage)
3. Lines are EXACTLY 2 points
4. Confidence reflects actual quality, not random numbers

Descending Triangle requirements:
- Upper boundary: descending (slope < 0)
- Lower boundary: near-horizontal (|slope| < threshold)
- Minimum 2 confirmed pivot highs on upper line
- Minimum 2 confirmed pivot lows on lower line
- Narrowing structure (apex formation)
- Price contained inside pattern most of the time
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class Pivot:
    """Swing point in price data."""
    index: int
    time: int
    value: float
    pivot_type: str  # "high" or "low"


@dataclass
class TrendLine:
    """Line built from exactly 2 pivots."""
    p1: Pivot
    p2: Pivot
    slope: float
    slope_normalized: float  # slope as % of price per day
    
    @classmethod
    def from_pivots(cls, p1: Pivot, p2: Pivot) -> 'TrendLine':
        dt = p2.time - p1.time
        if dt == 0:
            slope = 0
        else:
            slope = (p2.value - p1.value) / dt
        
        avg_price = (p1.value + p2.value) / 2
        slope_normalized = (slope * 86400) / avg_price if avg_price > 0 else 0
        
        return cls(p1=p1, p2=p2, slope=slope, slope_normalized=slope_normalized)
    
    def value_at(self, time: int) -> float:
        """Get line value at given time using linear interpolation."""
        if self.p2.time == self.p1.time:
            return self.p1.value
        return self.p1.value + self.slope * (time - self.p1.time)
    
    def to_points(self) -> List[Dict]:
        """Return exactly 2 points for rendering."""
        return [
            {"time": self.p1.time, "value": round(self.p1.value, 2)},
            {"time": self.p2.time, "value": round(self.p2.value, 2)},
        ]


class PatternValidatorV2:
    """
    Strict pattern validation with per-pattern validators.
    """
    
    # Thresholds
    HORIZONTAL_SLOPE_THRESHOLD = 0.0003  # Max normalized slope for "horizontal"
    DESCENDING_SLOPE_THRESHOLD = -0.0005  # Min slope for "descending"
    ASCENDING_SLOPE_THRESHOLD = 0.0005   # Min slope for "ascending"
    
    TOUCH_TOLERANCE = 0.012  # 1.2% tolerance for line touches
    MIN_PIVOTS_PER_LINE = 2
    MIN_TOTAL_TOUCHES = 4
    
    PRICE_CONTAINMENT_RATIO = 0.70  # 70% of candles must be inside pattern
    
    def __init__(self, timeframe: str = "1D"):
        # Pivot detection window by timeframe
        self.pivot_windows = {
            "4H": 3,
            "1D": 5,
            "7D": 7,
            "30D": 10,
        }
        self.pivot_window = self.pivot_windows.get(timeframe.upper(), 5)
        
        # Pattern detection window (number of candles to analyze)
        # Increased to make pattern more visible on chart
        self.pattern_windows = {
            "4H": 100,
            "1D": 200,  # ~6-7 months of daily data
            "7D": 150,
            "30D": 100,
        }
        self.pattern_window = self.pattern_windows.get(timeframe.upper(), 200)
    
    def find_pivots(self, candles: List[Dict]) -> Tuple[List[Pivot], List[Pivot]]:
        """
        Find pivot highs and lows in recent candles.
        Returns (pivot_highs, pivot_lows) sorted by time.
        """
        if len(candles) < self.pivot_window * 2 + 1:
            return [], []
        
        # Use only recent candles for pattern detection
        recent = candles[-self.pattern_window:] if len(candles) > self.pattern_window else candles
        
        pivot_highs = []
        pivot_lows = []
        window = self.pivot_window
        
        for i in range(window, len(recent) - window):
            c = recent[i]
            high = c['high']
            low = c['low']
            time = c.get('timestamp', c.get('time', 0))
            if time > 1e12:
                time = time // 1000
            
            # Check pivot high: must be higher than ALL surrounding candles
            is_pivot_high = True
            for j in range(1, window + 1):
                if high <= recent[i - j]['high'] or high <= recent[i + j]['high']:
                    is_pivot_high = False
                    break
            
            # Check pivot low: must be lower than ALL surrounding candles
            is_pivot_low = True
            for j in range(1, window + 1):
                if low >= recent[i - j]['low'] or low >= recent[i + j]['low']:
                    is_pivot_low = False
                    break
            
            if is_pivot_high:
                pivot_highs.append(Pivot(
                    index=i,
                    time=time,
                    value=high,
                    pivot_type="high"
                ))
            
            if is_pivot_low:
                pivot_lows.append(Pivot(
                    index=i,
                    time=time,
                    value=low,
                    pivot_type="low"
                ))
        
        return pivot_highs, pivot_lows
    
    def count_line_touches(self, line: TrendLine, candles: List[Dict], line_type: str) -> int:
        """
        Count how many candles "touch" the trendline.
        
        For upper line: check if candle high is near line
        For lower line: check if candle low is near line
        """
        touches = 0
        
        # Only check candles within the line's time range
        for c in candles:
            time = c.get('timestamp', c.get('time', 0))
            if time > 1e12:
                time = time // 1000
            
            # Skip candles outside line time range
            if time < line.p1.time or time > line.p2.time:
                continue
            
            line_value = line.value_at(time)
            
            if line_type == "high":
                price = c['high']
                # Touch = price is within tolerance of line
                if abs(price - line_value) / line_value < self.TOUCH_TOLERANCE:
                    touches += 1
            else:
                price = c['low']
                if abs(price - line_value) / line_value < self.TOUCH_TOLERANCE:
                    touches += 1
        
        return touches
    
    def check_price_containment(self, upper: TrendLine, lower: TrendLine, candles: List[Dict]) -> float:
        """
        Check what percentage of candles are contained between the two lines.
        Returns ratio (0.0 to 1.0).
        """
        inside_count = 0
        total_count = 0
        
        for c in candles:
            time = c.get('timestamp', c.get('time', 0))
            if time > 1e12:
                time = time // 1000
            
            # Only check within pattern time range
            if time < max(upper.p1.time, lower.p1.time) or time > min(upper.p2.time, lower.p2.time):
                continue
            
            total_count += 1
            
            upper_val = upper.value_at(time)
            lower_val = lower.value_at(time)
            
            # Check if candle body is mostly inside
            if c['high'] <= upper_val * 1.02 and c['low'] >= lower_val * 0.98:
                inside_count += 1
        
        return inside_count / total_count if total_count > 0 else 0
    
    def check_narrowing(self, upper: TrendLine, lower: TrendLine) -> bool:
        """
        Check if the pattern is narrowing (converging toward apex).
        """
        # Width at start
        width_start = upper.p1.value - lower.p1.value
        
        # Width at end
        width_end = upper.p2.value - lower.p2.value
        
        # For valid triangle, end width should be smaller than start
        return width_end < width_start * 0.95  # At least 5% narrower
    
    # =========================================================================
    # STRICT VALIDATORS FOR EACH PATTERN TYPE
    # =========================================================================
    
    def validate_descending_triangle(
        self,
        pivot_highs: List[Pivot],
        pivot_lows: List[Pivot],
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Validate DESCENDING TRIANGLE.
        
        Requirements:
        1. Upper boundary: DESCENDING (slope < 0)
        2. Lower boundary: NEAR-HORIZONTAL (|slope| < threshold)
        3. Minimum 2 pivot highs on upper line
        4. Minimum 2 pivot lows on lower line
        5. Narrowing structure
        6. Price containment >= 70%
        """
        # Need enough pivots
        if len(pivot_highs) < self.MIN_PIVOTS_PER_LINE:
            return None
        if len(pivot_lows) < self.MIN_PIVOTS_PER_LINE:
            return None
        
        # Use recent pivots only
        recent_highs = pivot_highs[-4:] if len(pivot_highs) > 4 else pivot_highs
        recent_lows = pivot_lows[-4:] if len(pivot_lows) > 4 else pivot_lows
        
        # Build upper line from first and last recent pivot highs
        upper_line = TrendLine.from_pivots(recent_highs[0], recent_highs[-1])
        
        # Build lower line from first and last recent pivot lows
        lower_line = TrendLine.from_pivots(recent_lows[0], recent_lows[-1])
        
        # VALIDATION 1: Upper line must be DESCENDING
        if upper_line.slope_normalized >= self.DESCENDING_SLOPE_THRESHOLD:
            return None  # Upper line is not descending enough
        
        # VALIDATION 2: Lower line must be NEAR-HORIZONTAL
        if abs(lower_line.slope_normalized) > self.HORIZONTAL_SLOPE_THRESHOLD:
            return None  # Lower line is not horizontal enough
        
        # VALIDATION 3: Check pivot touches on upper line
        upper_touches = 0
        for p in recent_highs:
            line_val = upper_line.value_at(p.time)
            if abs(p.value - line_val) / line_val < self.TOUCH_TOLERANCE:
                upper_touches += 1
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        # VALIDATION 4: Check pivot touches on lower line
        lower_touches = 0
        for p in recent_lows:
            line_val = lower_line.value_at(p.time)
            if abs(p.value - line_val) / line_val < self.TOUCH_TOLERANCE:
                lower_touches += 1
        
        if lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        # VALIDATION 5: Check narrowing
        if not self.check_narrowing(upper_line, lower_line):
            return None
        
        # VALIDATION 6: Check price containment
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        # All validations passed — calculate confidence
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + \
                         self.count_line_touches(lower_line, candles, "low")
        
        # Confidence based on quality metrics
        touch_score = min(1.0, total_touches / 6)  # Max at 6 pivots
        containment_score = containment
        candle_touch_score = min(1.0, candle_touches / 10)
        
        confidence = 0.4 + (touch_score * 0.2) + (containment_score * 0.25) + (candle_touch_score * 0.15)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": "descending_triangle",
            "direction": "bearish",
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "points": {
                "upper": upper_line.to_points(),
                "lower": lower_line.to_points(),
            },
            "breakout_level": round(lower_line.p2.value, 2),
            "invalidation": round(upper_line.p2.value, 2),
        }
    
    def validate_ascending_triangle(
        self,
        pivot_highs: List[Pivot],
        pivot_lows: List[Pivot],
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Validate ASCENDING TRIANGLE.
        
        Requirements:
        1. Upper boundary: NEAR-HORIZONTAL
        2. Lower boundary: ASCENDING (slope > 0)
        3. Min 2 pivot highs, min 2 pivot lows
        4. Narrowing structure
        5. Price containment >= 70%
        """
        if len(pivot_highs) < self.MIN_PIVOTS_PER_LINE:
            return None
        if len(pivot_lows) < self.MIN_PIVOTS_PER_LINE:
            return None
        
        recent_highs = pivot_highs[-4:] if len(pivot_highs) > 4 else pivot_highs
        recent_lows = pivot_lows[-4:] if len(pivot_lows) > 4 else pivot_lows
        
        upper_line = TrendLine.from_pivots(recent_highs[0], recent_highs[-1])
        lower_line = TrendLine.from_pivots(recent_lows[0], recent_lows[-1])
        
        # VALIDATION 1: Upper line must be NEAR-HORIZONTAL
        if abs(upper_line.slope_normalized) > self.HORIZONTAL_SLOPE_THRESHOLD:
            return None
        
        # VALIDATION 2: Lower line must be ASCENDING
        if lower_line.slope_normalized <= self.ASCENDING_SLOPE_THRESHOLD:
            return None
        
        # VALIDATION 3-4: Pivot touches
        upper_touches = sum(1 for p in recent_highs 
                           if abs(p.value - upper_line.value_at(p.time)) / upper_line.value_at(p.time) < self.TOUCH_TOLERANCE)
        lower_touches = sum(1 for p in recent_lows 
                           if abs(p.value - lower_line.value_at(p.time)) / lower_line.value_at(p.time) < self.TOUCH_TOLERANCE)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        # VALIDATION 5: Narrowing
        if not self.check_narrowing(upper_line, lower_line):
            return None
        
        # VALIDATION 6: Containment
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + \
                         self.count_line_touches(lower_line, candles, "low")
        
        confidence = 0.4 + (min(1.0, total_touches / 6) * 0.2) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.15)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": "ascending_triangle",
            "direction": "bullish",
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "points": {
                "upper": upper_line.to_points(),
                "lower": lower_line.to_points(),
            },
            "breakout_level": round(upper_line.p2.value, 2),
            "invalidation": round(lower_line.p2.value, 2),
        }
    
    def validate_symmetrical_triangle(
        self,
        pivot_highs: List[Pivot],
        pivot_lows: List[Pivot],
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Validate SYMMETRICAL TRIANGLE.
        
        Requirements:
        1. Upper boundary: DESCENDING
        2. Lower boundary: ASCENDING
        3. Similar slope magnitude (converging)
        4. Narrowing structure
        5. Price containment >= 70%
        """
        if len(pivot_highs) < self.MIN_PIVOTS_PER_LINE:
            return None
        if len(pivot_lows) < self.MIN_PIVOTS_PER_LINE:
            return None
        
        recent_highs = pivot_highs[-4:] if len(pivot_highs) > 4 else pivot_highs
        recent_lows = pivot_lows[-4:] if len(pivot_lows) > 4 else pivot_lows
        
        upper_line = TrendLine.from_pivots(recent_highs[0], recent_highs[-1])
        lower_line = TrendLine.from_pivots(recent_lows[0], recent_lows[-1])
        
        # VALIDATION 1: Upper must descend
        if upper_line.slope_normalized >= 0:
            return None
        
        # VALIDATION 2: Lower must ascend
        if lower_line.slope_normalized <= 0:
            return None
        
        # VALIDATION 3: Slopes should be roughly opposite (symmetrical)
        slope_ratio = abs(upper_line.slope_normalized) / abs(lower_line.slope_normalized) if lower_line.slope_normalized != 0 else 999
        if slope_ratio < 0.3 or slope_ratio > 3.0:
            return None  # Not symmetrical enough
        
        # VALIDATION 4-5: Touches
        upper_touches = sum(1 for p in recent_highs 
                           if abs(p.value - upper_line.value_at(p.time)) / upper_line.value_at(p.time) < self.TOUCH_TOLERANCE)
        lower_touches = sum(1 for p in recent_lows 
                           if abs(p.value - lower_line.value_at(p.time)) / lower_line.value_at(p.time) < self.TOUCH_TOLERANCE)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        # VALIDATION 6: Narrowing
        if not self.check_narrowing(upper_line, lower_line):
            return None
        
        # VALIDATION 7: Containment
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + \
                         self.count_line_touches(lower_line, candles, "low")
        
        confidence = 0.4 + (min(1.0, total_touches / 6) * 0.2) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.15)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": "symmetrical_triangle",
            "direction": "neutral",
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "points": {
                "upper": upper_line.to_points(),
                "lower": lower_line.to_points(),
            },
            "breakout_level": round((upper_line.p2.value + lower_line.p2.value) / 2, 2),
            "invalidation": None,
        }
    
    def validate_channel(
        self,
        pivot_highs: List[Pivot],
        pivot_lows: List[Pivot],
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Validate CHANNEL pattern.
        
        Requirements:
        1. Upper and lower boundaries have SAME direction (parallel)
        2. Slope difference is small (< 50% relative)
        3. Min 2 pivots on each line
        4. No narrowing (it's a channel, not triangle)
        5. Price containment >= 70%
        """
        if len(pivot_highs) < self.MIN_PIVOTS_PER_LINE:
            return None
        if len(pivot_lows) < self.MIN_PIVOTS_PER_LINE:
            return None
        
        recent_highs = pivot_highs[-4:] if len(pivot_highs) > 4 else pivot_highs
        recent_lows = pivot_lows[-4:] if len(pivot_lows) > 4 else pivot_lows
        
        upper_line = TrendLine.from_pivots(recent_highs[0], recent_highs[-1])
        lower_line = TrendLine.from_pivots(recent_lows[0], recent_lows[-1])
        
        # VALIDATION 1: Same direction (both positive or both negative)
        if upper_line.slope_normalized * lower_line.slope_normalized < 0:
            return None  # Different directions — not a channel
        
        # VALIDATION 2: Parallel check (slopes within 50% of each other)
        if upper_line.slope_normalized == 0 and lower_line.slope_normalized == 0:
            # Both horizontal — ok
            pass
        elif abs(upper_line.slope_normalized) > 0.0001 and abs(lower_line.slope_normalized) > 0.0001:
            slope_diff_ratio = abs(upper_line.slope_normalized - lower_line.slope_normalized) / \
                               max(abs(upper_line.slope_normalized), abs(lower_line.slope_normalized))
            if slope_diff_ratio > 0.5:
                return None  # Not parallel enough
        
        # VALIDATION 3-4: Touches
        upper_touches = sum(1 for p in recent_highs 
                           if abs(p.value - upper_line.value_at(p.time)) / upper_line.value_at(p.time) < self.TOUCH_TOLERANCE)
        lower_touches = sum(1 for p in recent_lows 
                           if abs(p.value - lower_line.value_at(p.time)) / lower_line.value_at(p.time) < self.TOUCH_TOLERANCE)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        # VALIDATION 5: Should NOT be narrowing (that would be triangle)
        if self.check_narrowing(upper_line, lower_line):
            return None  # It's a triangle, not channel
        
        # VALIDATION 6: Containment
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        # Determine channel type
        avg_slope = (upper_line.slope_normalized + lower_line.slope_normalized) / 2
        
        if avg_slope > 0.0003:
            channel_type = "ascending_channel"
            direction = "bullish"
        elif avg_slope < -0.0003:
            channel_type = "descending_channel"
            direction = "bearish"
        else:
            channel_type = "horizontal_channel"
            direction = "neutral"
        
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + \
                         self.count_line_touches(lower_line, candles, "low")
        
        confidence = 0.4 + (min(1.0, total_touches / 6) * 0.2) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.15)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": channel_type,
            "direction": direction,
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "points": {
                "upper": upper_line.to_points(),
                "lower": lower_line.to_points(),
            },
            "breakout_level": round(upper_line.p2.value if direction != "bearish" else lower_line.p2.value, 2),
            "invalidation": round(lower_line.p2.value if direction == "bullish" else upper_line.p2.value, 2),
        }
    
    # =========================================================================
    # MAIN DETECTION METHOD
    # =========================================================================
    
    def detect_best_pattern(self, candles: List[Dict]) -> Optional[Dict]:
        """
        Try all pattern validators and return the best valid one.
        
        Returns None if no valid pattern found.
        
        RULE: Better to return nothing than garbage.
        """
        if len(candles) < 30:
            return None
        
        # Find pivots
        pivot_highs, pivot_lows = self.find_pivots(candles)
        
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            return None
        
        patterns = []
        
        # Try each validator
        result = self.validate_descending_triangle(pivot_highs, pivot_lows, candles)
        if result:
            patterns.append(result)
        
        result = self.validate_ascending_triangle(pivot_highs, pivot_lows, candles)
        if result:
            patterns.append(result)
        
        result = self.validate_symmetrical_triangle(pivot_highs, pivot_lows, candles)
        if result:
            patterns.append(result)
        
        result = self.validate_channel(pivot_highs, pivot_lows, candles)
        if result:
            patterns.append(result)
        
        if not patterns:
            return None
        
        # Return highest confidence pattern
        patterns.sort(key=lambda p: p["confidence"], reverse=True)
        return patterns[0]


# Factory function
def get_pattern_validator_v2(timeframe: str = "1D") -> PatternValidatorV2:
    return PatternValidatorV2(timeframe)
