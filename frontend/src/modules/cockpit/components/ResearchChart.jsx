/**
 * ResearchChart — Technical Analysis Chart with Pattern Geometry
 * ==============================================================
 * 
 * Renders:
 * 1. Candles/Line price series
 * 2. Pattern geometry (channel/triangle lines)
 * 3. Support/Resistance levels
 * 4. Setup targets/trigger/invalidation
 * 
 * Layer priority:
 * - candles → pattern geometry → levels → targets
 */

import React, { useEffect, useRef } from 'react';
import styled from 'styled-components';
import { createChart, CandlestickSeries, LineSeries } from 'lightweight-charts';

const ChartWrapper = styled.div`
  position: relative;
  width: 100%;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  font-family: 'Gilroy', 'Inter', -apple-system, sans-serif;
`;

const ChartContainer = styled.div`
  width: 100%;
  height: ${({ $height }) => $height || 400}px;
`;

const BiasOverlay = styled.div`
  position: absolute;
  top: 12px;
  left: 200px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: ${({ $direction }) => 
    $direction === 'bullish' ? '#05A584' : 
    $direction === 'bearish' ? '#ef4444' : 
    '#64748b'};
  color: #ffffff;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13px;
  font-family: 'Gilroy', 'Inter', -apple-system, sans-serif;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 10;
  
  .arrow { font-size: 14px; }
  .confidence { font-size: 12px; opacity: 0.9; }
`;

const PatternLabel = styled.div`
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.95);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  font-family: 'Gilroy', 'Inter', -apple-system, sans-serif;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  z-index: 10;
  text-transform: capitalize;
  
  .confidence { margin-left: 8px; opacity: 0.85; }
`;

const COLORS = {
  bullish: '#05A584',
  bearish: '#ef4444',
  support: '#05A584',
  resistance: '#ef4444',
  trigger: '#8b5cf6',
  invalidation: '#f59e0b',
  target: '#3b82f6',
  patternUpper: '#3b82f6',
  patternLower: '#3b82f6',
};

const ResearchChart = ({
  candles = [],
  pattern = null,
  levels = [],
  setup = null,
  structure = null,
  chartType = 'candles',
  height = 400,
  showLevels = true,
  showPattern = true,
  showStructure = false,
  showTargets = true,
}) => {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    if (!chartRef.current || candles.length === 0) return;

    // Cleanup
    if (chartInstanceRef.current) {
      chartInstanceRef.current.remove();
      chartInstanceRef.current = null;
    }

    const rect = chartRef.current.getBoundingClientRect();
    
    // Create chart
    const chart = createChart(chartRef.current, {
      width: rect.width,
      height: height,
      layout: {
        background: { type: 'solid', color: '#ffffff' },
        textColor: '#64748b',
        fontFamily: "Gilroy, Inter, -apple-system, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#f1f5f9' },
        horzLines: { color: '#f1f5f9' },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: '#94a3b8', style: 2, width: 1 },
        horzLine: { color: '#94a3b8', style: 2, width: 1 },
      },
      rightPriceScale: {
        borderColor: '#e2e8f0',
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        borderColor: '#e2e8f0',
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 80,
      },
    });

    chartInstanceRef.current = chart;

    // 1. Add price series (candles/line)
    let priceSeries;
    if (chartType === 'line') {
      priceSeries = chart.addSeries(LineSeries, {
        color: COLORS.bullish,
        lineWidth: 2,
        lastValueVisible: true,
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineStyle: 2,
      });
    } else {
      priceSeries = chart.addSeries(CandlestickSeries, {
        upColor: COLORS.bullish,
        downColor: COLORS.bearish,
        borderUpColor: COLORS.bullish,
        borderDownColor: COLORS.bearish,
        wickUpColor: COLORS.bullish,
        wickDownColor: COLORS.bearish,
        lastValueVisible: true,
        priceLineVisible: true,
        priceLineWidth: 1,
        priceLineStyle: 2,
      });
    }

    // Format and set candle data
    const seen = new Set();
    const mapped = candles
      .map(c => ({
        time: c.time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
        value: c.close,
      }))
      .filter(c => c.time > 0)
      .sort((a, b) => a.time - b.time)
      .filter(c => {
        if (seen.has(c.time)) return false;
        seen.add(c.time);
        return true;
      });

    priceSeries.setData(mapped);

    // 2. RENDER PATTERN GEOMETRY (channel/triangle lines)
    if (showPattern && pattern?.points) {
      const { upper, lower } = pattern.points;
      
      // Upper trendline
      if (upper && upper.length >= 2) {
        const upperSeries = chart.addSeries(LineSeries, {
          color: COLORS.patternUpper,
          lineWidth: 2,
          lineStyle: 0, // Solid line for pattern
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerVisible: false,
        });
        
        const upperData = upper.map(pt => ({
          time: typeof pt[0] === 'number' ? pt[0] : parseInt(pt[0]),
          value: typeof pt[1] === 'number' ? pt[1] : parseFloat(pt[1]),
        })).filter(d => d.time > 0 && d.value > 0).sort((a, b) => a.time - b.time);
        
        if (upperData.length >= 2) {
          // Extend line into future
          const lastPoint = upperData[upperData.length - 1];
          const slope = (upperData[1].value - upperData[0].value) / (upperData[1].time - upperData[0].time);
          const futureTime = lastPoint.time + 30 * 86400; // +30 days
          const futureValue = lastPoint.value + slope * (futureTime - lastPoint.time);
          upperData.push({ time: futureTime, value: futureValue });
          
          upperSeries.setData(upperData);
        }
      }
      
      // Lower trendline
      if (lower && lower.length >= 2) {
        const lowerSeries = chart.addSeries(LineSeries, {
          color: COLORS.patternLower,
          lineWidth: 2,
          lineStyle: 0, // Solid line for pattern
          priceLineVisible: false,
          lastValueVisible: false,
          crosshairMarkerVisible: false,
        });
        
        const lowerData = lower.map(pt => ({
          time: typeof pt[0] === 'number' ? pt[0] : parseInt(pt[0]),
          value: typeof pt[1] === 'number' ? pt[1] : parseFloat(pt[1]),
        })).filter(d => d.time > 0 && d.value > 0).sort((a, b) => a.time - b.time);
        
        if (lowerData.length >= 2) {
          // Extend line into future
          const lastPoint = lowerData[lowerData.length - 1];
          const slope = (lowerData[1].value - lowerData[0].value) / (lowerData[1].time - lowerData[0].time);
          const futureTime = lastPoint.time + 30 * 86400;
          const futureValue = lastPoint.value + slope * (futureTime - lastPoint.time);
          lowerData.push({ time: futureTime, value: futureValue });
          
          lowerSeries.setData(lowerData);
        }
      }
    }

    // 3. RENDER LEVELS (support/resistance as thin dashed lines)
    if (showLevels && levels.length > 0) {
      const priceRange = Math.max(...mapped.map(c => c.high)) - Math.min(...mapped.map(c => c.low));
      const threshold = priceRange * 0.02;
      const drawnPrices = [];
      
      levels.forEach(level => {
        const tooClose = drawnPrices.some(p => Math.abs(p - level.price) < threshold);
        if (tooClose) return;
        drawnPrices.push(level.price);
        
        const color = level.type === 'support' ? COLORS.support : COLORS.resistance;
        
        priceSeries.createPriceLine({
          price: level.price,
          color: color,
          lineWidth: 1,
          lineStyle: 2, // Dashed
          axisLabelVisible: true,
          title: `${level.type} ${Math.round((level.strength || 0) * 100)}%`,
        });
      });
    }

    // 4. RENDER TARGETS (secondary, thin lines)
    if (showTargets && setup) {
      const targetLines = [];
      
      if (setup.trigger) {
        targetLines.push({ price: setup.trigger, color: COLORS.trigger, label: 'Trigger' });
      }
      if (setup.invalidation) {
        targetLines.push({ price: setup.invalidation, color: COLORS.invalidation, label: 'Invalidation' });
      }
      if (setup.targets?.[0]) {
        targetLines.push({ price: setup.targets[0], color: COLORS.target, label: 'T1' });
      }
      if (setup.targets?.[1]) {
        targetLines.push({ price: setup.targets[1], color: COLORS.target, label: 'T2' });
      }
      
      targetLines.forEach(line => {
        priceSeries.createPriceLine({
          price: line.price,
          color: line.color,
          lineWidth: 1,
          lineStyle: 1, // Dotted (less prominent than pattern)
          axisLabelVisible: true,
          title: line.label,
        });
      });
    }

    // Fit content
    chart.timeScale().fitContent();

    // Resize observer
    const ro = new ResizeObserver(() => {
      if (chartRef.current && chartInstanceRef.current) {
        const w = chartRef.current.clientWidth;
        if (w > 0) {
          chartInstanceRef.current.applyOptions({ width: w });
        }
      }
    });
    ro.observe(chartRef.current);

    return () => {
      ro.disconnect();
      if (chartInstanceRef.current) {
        chartInstanceRef.current.remove();
        chartInstanceRef.current = null;
      }
    };
  }, [candles, chartType, height, levels, setup, pattern, showLevels, showPattern, showTargets]);

  const direction = setup?.direction || 'neutral';
  const confidence = setup?.confidence ? Math.round(setup.confidence * 100) : 0;

  return (
    <ChartWrapper>
      <ChartContainer ref={chartRef} $height={height} />
      
      {showPattern && pattern && (
        <PatternLabel>
          {pattern.type?.replace(/_/g, ' ')}
          <span className="confidence">{Math.round((pattern.confidence || 0) * 100)}%</span>
        </PatternLabel>
      )}
      
      {setup && (
        <BiasOverlay $direction={direction}>
          <span className="arrow">
            {direction === 'bullish' ? '↑' : direction === 'bearish' ? '↓' : '→'}
          </span>
          {direction.toUpperCase()}
          <span className="confidence">{confidence}%</span>
        </BiasOverlay>
      )}
    </ChartWrapper>
  );
};

export default ResearchChart;
