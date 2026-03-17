"""
Pattern Validation Engine v2 with Best-Fit Boundary Selection
==============================================================

P0 FIX: Anchor Point Selection Engine
-------------------------------------
Before validation, we now:
1. Generate ALL candidate lines from pivot combinations
2. Score each line by touch quality, pivot confirmation, candle violations
3. Select the BEST-FIT upper and lower boundaries
4. Only then run pattern validation

This fixes the issue where lines were drawn through wrong pivot points,
resulting in visually incorrect patterns.

Rules:
1. Each pattern type has its own validator with specific requirements
2. If ANY requirement fails → return None (no garbage)
3. Lines are EXACTLY 2 points
4. Confidence reflects actual quality, not random numbers
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
    score: float = 0.0  # Best-fit score
    
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
    
    def value_at_index(self, index: int, p1_index: int) -> float:
        """Get line value at given index."""
        if self.p2.index == self.p1.index:
            return self.p1.value
        slope_idx = (self.p2.value - self.p1.value) / (self.p2.index - self.p1.index)
        return self.p1.value + slope_idx * (index - self.p1.index)
    
    def to_points(self) -> List[Dict]:
        """Return exactly 2 points for rendering."""
        return [
            {"time": self.p1.time, "value": round(self.p1.value, 2)},
            {"time": self.p2.time, "value": round(self.p2.value, 2)},
        ]


class PatternValidatorV2:
    """
    Strict pattern validation with Best-Fit Boundary Selection.
    """
    
    # Thresholds
    HORIZONTAL_SLOPE_THRESHOLD = 0.0003
    DESCENDING_SLOPE_THRESHOLD = -0.0005
    ASCENDING_SLOPE_THRESHOLD = 0.0005
    
    TOUCH_TOLERANCE = 0.008  # 0.8% tolerance
    MIN_PIVOTS_PER_LINE = 2
    MIN_TOTAL_TOUCHES = 4
    MIN_PIVOT_DISTANCE = 10
    
    PRICE_CONTAINMENT_RATIO = 0.70
    
    def __init__(self, timeframe: str = "1D"):
        self.pivot_windows = {"4H": 3, "1D": 5, "7D": 7, "30D": 10}
        self.pivot_window = self.pivot_windows.get(timeframe.upper(), 5)
        
        self.pattern_windows = {"4H": 80, "1D": 120, "7D": 100, "30D": 80}
        self.pattern_window = self.pattern_windows.get(timeframe.upper(), 120)
        
        self._recent_candles: List[Dict] = []
    
    def find_pivots(self, candles: List[Dict]) -> Tuple[List[Pivot], List[Pivot]]:
        if len(candles) < self.pivot_window * 2 + 1:
            return [], []
        
        self._recent_candles = candles[-self.pattern_window:] if len(candles) > self.pattern_window else candles
        recent = self._recent_candles
        
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
            
            is_pivot_high = True
            for j in range(1, window + 1):
                if high <= recent[i - j]['high'] or high <= recent[i + j]['high']:
                    is_pivot_high = False
                    break
            
            is_pivot_low = True
            for j in range(1, window + 1):
                if low >= recent[i - j]['low'] or low >= recent[i + j]['low']:
                    is_pivot_low = False
                    break
            
            if is_pivot_high:
                pivot_highs.append(Pivot(index=i, time=time, value=high, pivot_type="high"))
            
            if is_pivot_low:
                pivot_lows.append(Pivot(index=i, time=time, value=low, pivot_type="low"))
        
        return pivot_highs, pivot_lows
    
    def generate_line_candidates(self, pivots: List[Pivot]) -> List[TrendLine]:
        lines = []
        for i in range(len(pivots)):
            for j in range(i + 1, len(pivots)):
                p1 = pivots[i]
                p2 = pivots[j]
                if abs(p2.index - p1.index) < self.MIN_PIVOT_DISTANCE:
                    continue
                line = TrendLine.from_pivots(p1, p2)
                lines.append(line)
        return lines
    
    def score_trendline(self, line: TrendLine, pivots: List[Pivot], candles: List[Dict], line_type: str) -> float:
        touch_count = 0
        pivot_confirmations = 0
        candle_violations = 0
        tolerance = self.TOUCH_TOLERANCE
        
        for i in range(line.p1.index, min(line.p2.index + 1, len(candles))):
            if i < 0 or i >= len(candles):
                continue
            candle = candles[i]
            expected_price = line.value_at_index(i, line.p1.index)
            
            if line_type == "high":
                price = candle['high']
                distance = abs(price - expected_price) / expected_price if expected_price > 0 else 1
                if distance < tolerance:
                    touch_count += 1
                if price > expected_price * (1 + tolerance * 1.5):
                    candle_violations += 1
            else:
                price = candle['low']
                distance = abs(price - expected_price) / expected_price if expected_price > 0 else 1
                if distance < tolerance:
                    touch_count += 1
                if price < expected_price * (1 - tolerance * 1.5):
                    candle_violations += 1
        
        for pivot in pivots:
            if pivot.index < line.p1.index or pivot.index > line.p2.index:
                continue
            expected_price = line.value_at_index(pivot.index, line.p1.index)
            dist = abs(pivot.value - expected_price) / expected_price if expected_price > 0 else 1
            if dist < tolerance:
                pivot_confirmations += 1
        
        time_span = line.p2.index - line.p1.index
        time_bonus = min(time_span / 50, 2.0)
        
        score = touch_count * 2 + pivot_confirmations * 3 - candle_violations * 4 + time_bonus
        return score
    
    def find_best_line(self, pivots: List[Pivot], candles: List[Dict], line_type: str, slope_constraint: Optional[str] = None) -> Optional[TrendLine]:
        if len(pivots) < 2:
            return None
        
        candidates = self.generate_line_candidates(pivots)
        if not candidates:
            return None
        
        best_line = None
        best_score = float('-inf')
        
        for line in candidates:
            if slope_constraint == "descending":
                if line.slope_normalized >= 0:
                    continue
            elif slope_constraint == "ascending":
                if line.slope_normalized <= 0:
                    continue
            elif slope_constraint == "horizontal":
                if abs(line.slope_normalized) > self.HORIZONTAL_SLOPE_THRESHOLD:
                    continue
            
            score = self.score_trendline(line, pivots, candles, line_type)
            if score > best_score:
                best_score = score
                best_line = line
                best_line.score = score
        
        if best_line and best_score < 2:
            return None
        
        return best_line
    
    def count_line_touches(self, line: TrendLine, candles: List[Dict], line_type: str) -> int:
        touches = 0
        for i in range(line.p1.index, min(line.p2.index + 1, len(candles))):
            if i < 0 or i >= len(candles):
                continue
            c = candles[i]
            line_value = line.value_at_index(i, line.p1.index)
            if line_type == "high":
                price = c['high']
            else:
                price = c['low']
            if abs(price - line_value) / line_value < self.TOUCH_TOLERANCE:
                touches += 1
        return touches
    
    def check_price_containment(self, upper: TrendLine, lower: TrendLine, candles: List[Dict]) -> float:
        inside_count = 0
        total_count = 0
        start_idx = max(upper.p1.index, lower.p1.index)
        end_idx = min(upper.p2.index, lower.p2.index)
        
        for i in range(start_idx, end_idx + 1):
            if i < 0 or i >= len(candles):
                continue
            total_count += 1
            c = candles[i]
            upper_val = upper.value_at_index(i, upper.p1.index)
            lower_val = lower.value_at_index(i, lower.p1.index)
            if c['high'] <= upper_val * 1.02 and c['low'] >= lower_val * 0.98:
                inside_count += 1
        
        return inside_count / total_count if total_count > 0 else 0
    
    def check_narrowing(self, upper: TrendLine, lower: TrendLine) -> bool:
        width_start = upper.p1.value - lower.p1.value
        width_end = upper.p2.value - lower.p2.value
        return width_end < width_start * 0.95
    
    def count_pivot_touches(self, line: TrendLine, pivots: List[Pivot]) -> int:
        touches = 0
        for p in pivots:
            if p.index < line.p1.index or p.index > line.p2.index:
                continue
            line_val = line.value_at_index(p.index, line.p1.index)
            if abs(p.value - line_val) / line_val < self.TOUCH_TOLERANCE:
                touches += 1
        return touches
    
    def validate_descending_triangle(self, pivot_highs: List[Pivot], pivot_lows: List[Pivot], candles: List[Dict]) -> Optional[Dict]:
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            return None
        
        recent_highs = pivot_highs[-5:] if len(pivot_highs) > 5 else pivot_highs
        recent_lows = pivot_lows[-5:] if len(pivot_lows) > 5 else pivot_lows
        
        upper_line = self.find_best_line(recent_highs, candles, "high", slope_constraint="descending")
        lower_line = self.find_best_line(recent_lows, candles, "low", slope_constraint="horizontal")
        
        if not upper_line or not lower_line:
            return None
        
        upper_touches = self.count_pivot_touches(upper_line, recent_highs)
        lower_touches = self.count_pivot_touches(lower_line, recent_lows)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        if not self.check_narrowing(upper_line, lower_line):
            return None
        
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + self.count_line_touches(lower_line, candles, "low")
        
        touch_score = min(1.0, total_touches / 6)
        line_score = min(1.0, (upper_line.score + lower_line.score) / 20)
        confidence = 0.4 + (touch_score * 0.15) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.1) + (line_score * 0.1)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": "descending_triangle",
            "direction": "bearish",
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "line_scores": {"upper": round(upper_line.score, 1), "lower": round(lower_line.score, 1)},
            "points": {"upper": upper_line.to_points(), "lower": lower_line.to_points()},
            "breakout_level": round(lower_line.p2.value, 2),
            "invalidation": round(upper_line.p2.value, 2),
        }
    
    def validate_ascending_triangle(self, pivot_highs: List[Pivot], pivot_lows: List[Pivot], candles: List[Dict]) -> Optional[Dict]:
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            return None
        
        recent_highs = pivot_highs[-5:] if len(pivot_highs) > 5 else pivot_highs
        recent_lows = pivot_lows[-5:] if len(pivot_lows) > 5 else pivot_lows
        
        upper_line = self.find_best_line(recent_highs, candles, "high", slope_constraint="horizontal")
        lower_line = self.find_best_line(recent_lows, candles, "low", slope_constraint="ascending")
        
        if not upper_line or not lower_line:
            return None
        
        upper_touches = self.count_pivot_touches(upper_line, recent_highs)
        lower_touches = self.count_pivot_touches(lower_line, recent_lows)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        if not self.check_narrowing(upper_line, lower_line):
            return None
        
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + self.count_line_touches(lower_line, candles, "low")
        
        touch_score = min(1.0, total_touches / 6)
        line_score = min(1.0, (upper_line.score + lower_line.score) / 20)
        confidence = 0.4 + (touch_score * 0.15) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.1) + (line_score * 0.1)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": "ascending_triangle",
            "direction": "bullish",
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "line_scores": {"upper": round(upper_line.score, 1), "lower": round(lower_line.score, 1)},
            "points": {"upper": upper_line.to_points(), "lower": lower_line.to_points()},
            "breakout_level": round(upper_line.p2.value, 2),
            "invalidation": round(lower_line.p2.value, 2),
        }
    
    def validate_symmetrical_triangle(self, pivot_highs: List[Pivot], pivot_lows: List[Pivot], candles: List[Dict]) -> Optional[Dict]:
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            return None
        
        recent_highs = pivot_highs[-5:] if len(pivot_highs) > 5 else pivot_highs
        recent_lows = pivot_lows[-5:] if len(pivot_lows) > 5 else pivot_lows
        
        upper_line = self.find_best_line(recent_highs, candles, "high", slope_constraint="descending")
        lower_line = self.find_best_line(recent_lows, candles, "low", slope_constraint="ascending")
        
        if not upper_line or not lower_line:
            return None
        
        if lower_line.slope_normalized == 0:
            return None
        slope_ratio = abs(upper_line.slope_normalized) / abs(lower_line.slope_normalized)
        if slope_ratio < 0.3 or slope_ratio > 3.0:
            return None
        
        upper_touches = self.count_pivot_touches(upper_line, recent_highs)
        lower_touches = self.count_pivot_touches(lower_line, recent_lows)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        if not self.check_narrowing(upper_line, lower_line):
            return None
        
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
        total_touches = upper_touches + lower_touches
        candle_touches = self.count_line_touches(upper_line, candles, "high") + self.count_line_touches(lower_line, candles, "low")
        
        touch_score = min(1.0, total_touches / 6)
        line_score = min(1.0, (upper_line.score + lower_line.score) / 20)
        confidence = 0.4 + (touch_score * 0.15) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.1) + (line_score * 0.1)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": "symmetrical_triangle",
            "direction": "neutral",
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "slope_ratio": round(slope_ratio, 2),
            "line_scores": {"upper": round(upper_line.score, 1), "lower": round(lower_line.score, 1)},
            "points": {"upper": upper_line.to_points(), "lower": lower_line.to_points()},
            "breakout_level": round((upper_line.p2.value + lower_line.p2.value) / 2, 2),
            "invalidation": None,
        }
    
    def validate_channel(self, pivot_highs: List[Pivot], pivot_lows: List[Pivot], candles: List[Dict]) -> Optional[Dict]:
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            return None
        
        recent_highs = pivot_highs[-5:] if len(pivot_highs) > 5 else pivot_highs
        recent_lows = pivot_lows[-5:] if len(pivot_lows) > 5 else pivot_lows
        
        upper_line = self.find_best_line(recent_highs, candles, "high")
        lower_line = self.find_best_line(recent_lows, candles, "low")
        
        if not upper_line or not lower_line:
            return None
        
        if upper_line.slope_normalized * lower_line.slope_normalized < -0.00001:
            return None
        
        if abs(upper_line.slope_normalized) > 0.0001 or abs(lower_line.slope_normalized) > 0.0001:
            max_slope = max(abs(upper_line.slope_normalized), abs(lower_line.slope_normalized))
            if max_slope > 0:
                slope_diff_ratio = abs(upper_line.slope_normalized - lower_line.slope_normalized) / max_slope
                if slope_diff_ratio > 0.5:
                    return None
        
        upper_touches = self.count_pivot_touches(upper_line, recent_highs)
        lower_touches = self.count_pivot_touches(lower_line, recent_lows)
        
        if upper_touches < self.MIN_PIVOTS_PER_LINE or lower_touches < self.MIN_PIVOTS_PER_LINE:
            return None
        
        if self.check_narrowing(upper_line, lower_line):
            return None
        
        containment = self.check_price_containment(upper_line, lower_line, candles)
        if containment < self.PRICE_CONTAINMENT_RATIO:
            return None
        
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
        candle_touches = self.count_line_touches(upper_line, candles, "high") + self.count_line_touches(lower_line, candles, "low")
        
        touch_score = min(1.0, total_touches / 6)
        line_score = min(1.0, (upper_line.score + lower_line.score) / 20)
        confidence = 0.4 + (touch_score * 0.15) + (containment * 0.25) + (min(1.0, candle_touches / 10) * 0.1) + (line_score * 0.1)
        confidence = round(min(0.85, confidence), 2)
        
        return {
            "type": channel_type,
            "direction": direction,
            "confidence": confidence,
            "touches": total_touches,
            "candle_touches": candle_touches,
            "containment": round(containment, 2),
            "line_scores": {"upper": round(upper_line.score, 1), "lower": round(lower_line.score, 1)},
            "points": {"upper": upper_line.to_points(), "lower": lower_line.to_points()},
            "breakout_level": round(upper_line.p2.value if direction != "bearish" else lower_line.p2.value, 2),
            "invalidation": round(lower_line.p2.value if direction == "bullish" else upper_line.p2.value, 2),
        }
    
    def detect_best_pattern(self, candles: List[Dict]) -> Optional[Dict]:
        if len(candles) < 30:
            return None
        
        pivot_highs, pivot_lows = self.find_pivots(candles)
        
        if len(pivot_highs) < 2 or len(pivot_lows) < 2:
            return None
        
        recent_candles = self._recent_candles if self._recent_candles else candles[-self.pattern_window:]
        
        patterns = []
        
        result = self.validate_descending_triangle(pivot_highs, pivot_lows, recent_candles)
        if result:
            patterns.append(result)
        
        result = self.validate_ascending_triangle(pivot_highs, pivot_lows, recent_candles)
        if result:
            patterns.append(result)
        
        result = self.validate_symmetrical_triangle(pivot_highs, pivot_lows, recent_candles)
        if result:
            patterns.append(result)
        
        result = self.validate_channel(pivot_highs, pivot_lows, recent_candles)
        if result:
            patterns.append(result)
        
        if not patterns:
            return None
        
        patterns.sort(key=lambda p: (p["confidence"], p.get("line_scores", {}).get("upper", 0) + p.get("line_scores", {}).get("lower", 0)), reverse=True)
        return patterns[0]


def get_pattern_validator_v2(timeframe: str = "1D") -> PatternValidatorV2:
    return PatternValidatorV2(timeframe)
