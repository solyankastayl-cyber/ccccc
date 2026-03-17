/**
 * ResearchChart — Clean Technical Analysis Chart
 * ===============================================
 * 
 * Single dashed lines via createPriceLine only (no duplicates)
 * Lines extend 1 YEAR into future
 * Current price line visible
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
};

const ResearchChart = ({
  candles = [],
  pattern = null,
  levels = [],
  setup = null,
  chartType = 'candles',
  height = 400,
  showLevels = true,
  showPattern = true,
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
        rightOffset: 80, // Space for 1 year future
      },
    });

    chartInstanceRef.current = chart;

    // Add price series with current price line
    let priceSeries;
    if (chartType === 'line') {
      priceSeries = chart.addSeries(LineSeries, {
        color: COLORS.bullish,
        lineWidth: 2,
        lastValueVisible: true,
        priceLineVisible: true, // Current price line
        priceLineWidth: 1,
        priceLineStyle: 2, // Dashed
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
        priceLineVisible: true, // Current price line
        priceLineWidth: 1,
        priceLineStyle: 2, // Dashed
      });
    }

    // Format candles
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

    // Get price range for overlap detection
    const priceRange = Math.max(...mapped.map(c => c.high)) - Math.min(...mapped.map(c => c.low));
    const threshold = priceRange * 0.03; // 3% threshold

    // Collect all lines to draw (single priceLine per level - no LineSeries)
    const linesToDraw = [];
    
    // Setup lines (higher priority)
    if (setup?.trigger) {
      linesToDraw.push({ price: setup.trigger, color: COLORS.trigger, label: 'Trigger', priority: 1 });
    }
    if (setup?.invalidation) {
      linesToDraw.push({ price: setup.invalidation, color: COLORS.invalidation, label: 'Invalidation', priority: 1 });
    }
    if (setup?.targets?.length > 0) {
      linesToDraw.push({ price: setup.targets[0], color: COLORS.target, label: 'Target 1', priority: 2 });
      if (setup.targets[1]) {
        linesToDraw.push({ price: setup.targets[1], color: COLORS.target, label: 'Target 2', priority: 3 });
      }
    }
    
    // Level lines (lower priority)
    if (showLevels && levels.length > 0) {
      const supportLevel = levels.find(l => l.type === 'support');
      const resistanceLevel = levels.find(l => l.type === 'resistance');
      
      if (supportLevel) {
        linesToDraw.push({ price: supportLevel.price, color: COLORS.support, label: 'Support', priority: 4 });
      }
      if (resistanceLevel) {
        linesToDraw.push({ price: resistanceLevel.price, color: COLORS.resistance, label: 'Resistance', priority: 4 });
      }
    }
    
    // Sort by priority and filter overlaps
    linesToDraw.sort((a, b) => a.priority - b.priority);
    const drawnPrices = [];
    
    // Draw SINGLE priceLine per level (no duplicate LineSeries)
    linesToDraw.forEach(line => {
      // Check overlap
      const tooClose = drawnPrices.some(p => Math.abs(p - line.price) < threshold);
      if (tooClose) return;
      
      drawnPrices.push(line.price);
      
      // Single dashed priceLine - extends to infinity (1 year+)
      priceSeries.createPriceLine({
        price: line.price,
        color: line.color,
        lineWidth: 1,
        lineStyle: 2, // Dashed - single line
        axisLabelVisible: true,
        title: line.label,
      });
    });

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
  }, [candles, chartType, height, levels, setup, showLevels]);

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
