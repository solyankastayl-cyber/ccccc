/**
 * ResearchView — Technical Analysis Research Terminal
 * ====================================================
 * 
 * Uses Setup API to display:
 * 1. Full-width chart with patterns, levels, bias
 * 2. Pattern Activation Layer
 * 3. Deep Analysis Blocks
 * 4. Save Idea functionality
 */

import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { 
  Search, 
  RefreshCw, 
  Share2, 
  Camera, 
  Bookmark,
  Loader2,
  AlertTriangle,
  ChevronDown,
  BarChart2,
  LineChart,
  Eye,
  EyeOff,
  Settings2,
  Triangle,
  Layers,
  TrendingUp,
  Target
} from 'lucide-react';

import ResearchChart from '../components/ResearchChart';
import PatternActivationLayer from '../components/PatternActivationLayer';
import DeepAnalysisBlocks from '../components/DeepAnalysisBlocks';
import setupService from '../../../services/setupService';

// ============================================
// STYLED COMPONENTS
// ============================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
  overflow-y: auto;
`;

const TopBar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #ffffff;
  border-bottom: 1px solid #eef1f5;
  flex-wrap: wrap;
  gap: 12px;
`;

const ControlsLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ControlsRight = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SearchWrapper = styled.div`
  position: relative;
`;

const SearchInput = styled.input`
  width: 160px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: 0.5px;
  
  &:focus {
    outline: none;
    border-color: #05A584;
    background: #ffffff;
  }
  
  &::placeholder {
    color: #94a3b8;
    font-weight: 500;
  }
`;

const SymbolDropdown = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
`;

const SymbolOption = styled.button`
  width: 100%;
  padding: 10px 12px;
  text-align: left;
  border: none;
  background: ${({ $active }) => $active ? '#f0f9ff' : 'transparent'};
  font-size: 13px;
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
  
  &:hover {
    background: #f8fafc;
  }
`;

const TfGroup = styled.div`
  display: flex;
  gap: 2px;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
`;

const TfButton = styled.button`
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  border: none;
  background: ${({ $active }) => $active ? '#ffffff' : 'transparent'};
  color: ${({ $active }) => $active ? '#0f172a' : '#64748b'};
  cursor: pointer;
  box-shadow: ${({ $active }) => $active ? '0 1px 3px rgba(0,0,0,0.08)' : 'none'};
  transition: all 0.15s ease;
  
  &:hover {
    color: #0f172a;
  }
`;

const ChartTypeGroup = styled.div`
  display: flex;
  gap: 2px;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
`;

const ChartTypeBtn = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  background: ${({ $active }) => $active ? '#ffffff' : 'transparent'};
  color: ${({ $active }) => $active ? '#0f172a' : '#64748b'};
  cursor: pointer;
  box-shadow: ${({ $active }) => $active ? '0 1px 3px rgba(0,0,0,0.08)' : 'none'};
  
  svg {
    width: 16px;
    height: 16px;
  }
  
  &:hover {
    color: #0f172a;
  }
`;

const ViewModeWrapper = styled.div`
  position: relative;
`;

const ViewModeButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  cursor: pointer;
  
  &:hover {
    border-color: #cbd5e1;
  }
  
  svg {
    width: 14px;
    height: 14px;
    color: #94a3b8;
  }
`;

const ViewModeDropdown = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  min-width: 140px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 50;
  overflow: hidden;
`;

const ViewModeOption = styled.button`
  display: block;
  width: 100%;
  padding: 10px 14px;
  background: ${({ $active }) => $active ? '#f8fafc' : '#ffffff'};
  border: none;
  text-align: left;
  font-size: 13px;
  font-weight: ${({ $active }) => $active ? '600' : '500'};
  color: #0f172a;
  cursor: pointer;
  
  &:hover {
    background: #f1f5f9;
  }
`;

const ActionBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #64748b;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  
  svg {
    width: 14px;
    height: 14px;
  }
  
  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &.primary {
    background: #3b82f6;
    border-color: #3b82f6;
    color: #ffffff;
    
    &:hover {
      background: #2563eb;
    }
  }
  
  &.loading svg {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const LayerToggles = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px;
  background: #f1f5f9;
  border-radius: 8px;
`;

const LayerToggleBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  border: none;
  background: ${({ $active }) => $active ? '#ffffff' : 'transparent'};
  color: ${({ $active, $color }) => $active ? $color : '#94a3b8'};
  cursor: pointer;
  box-shadow: ${({ $active }) => $active ? '0 1px 3px rgba(0,0,0,0.08)' : 'none'};
  transition: all 0.15s ease;
  
  &:hover {
    color: ${({ $color }) => $color};
  }
  
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${({ $active, $color }) => $active ? $color : '#cbd5e1'};
  }
`;

const MainContent = styled.div`
  flex: 1;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ChartSection = styled.div`
  background: #ffffff;
  border: 1px solid #eef1f5;
  border-radius: 12px;
  overflow: hidden;
`;

const ErrorBanner = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  
  svg {
    flex-shrink: 0;
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  z-index: 10;
  
  svg {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const SuccessToast = styled.div`
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  background: #05A584;
  color: #ffffff;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(5, 165, 132, 0.3);
  z-index: 1000;
  animation: slideIn 0.3s ease;
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const DebugPanel = styled.div`
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 16px 20px;
  margin: 16px 0;
  font-family: 'Gilroy', 'Inter', -apple-system, sans-serif;
  
  .debug-title {
    font-weight: 700;
    font-size: 11px;
    color: #64748b;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  
  .debug-row {
    display: flex;
    gap: 32px;
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .debug-label {
    min-width: 100px;
    font-size: 12px;
    font-weight: 500;
    color: #94a3b8;
  }
  
  .debug-value {
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
    
    &.bullish { color: #05A584; }
    &.bearish { color: #ef4444; }
    &.neutral { color: #64748b; }
  }
`;

// ============================================
// CONSTANTS
// ============================================

const SYMBOLS = [
  'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
  'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT',
  'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'LTCUSDT', 'ETCUSDT',
  'FILUSDT', 'APTUSDT', 'ARBUSDT', 'OPUSDT', 'NEARUSDT',
  'INJUSDT', 'SUIUSDT', 'AAVEUSDT', 'MKRUSDT', 'CRVUSDT',
  'TONUSDT', 'SEIUSDT', 'TIAUSDT', 'JUPUSDT', 'WIFUSDT'
];
const TIMEFRAMES = ['4h', '1d', '7d', '30d', '180d', '1y'];

// ============================================
// COMPONENT
// ============================================

const ResearchView = () => {
  // State
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('1d');
  const [chartType, setChartType] = useState('candles');
  const [viewMode, setViewMode] = useState('auto');
  const [showViewModeDropdown, setShowViewModeDropdown] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  
  // Data
  const [setupData, setSetupData] = useState(null);
  const [candles, setCandles] = useState([]);
  
  // Active elements for pattern activation
  const [activeElements, setActiveElements] = useState({});
  
  // Layer visibility toggles
  const [layerVisibility, setLayerVisibility] = useState({
    patterns: true,
    levels: true,
    structure: false,
    targets: true,
  });

  // Fetch setup data from new clean endpoint
  const fetchSetup = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/ta/setup?symbol=${symbol}&tf=${timeframe}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch setup');
      }
      
      const data = await response.json();
      setSetupData(data);
      setCandles(data.candles || []);
      
    } catch (err) {
      setError(err.message || 'Failed to load analysis');
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe]);

  // Initial load
  useEffect(() => {
    fetchSetup();
  }, [fetchSetup]);

  // Handle symbol change
  const handleSymbolSelect = (s) => {
    setSymbol(s);
    setSearchQuery('');
    setShowDropdown(false);
  };

  // Handle search - filter and show first 5
  const filteredSymbols = searchQuery
    ? SYMBOLS.filter(s => 
        s.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.replace('USDT', '').toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 5)
    : SYMBOLS.slice(0, 5);

  // Toggle element visibility
  const handleToggleElement = (elementKey) => {
    setActiveElements(prev => ({
      ...prev,
      [elementKey]: !prev[elementKey]
    }));
  };

  // Save idea
  const handleSaveIdea = async () => {
    try {
      setLoading(true);
      const result = await setupService.createIdea(symbol, timeframe);
      
      if (result.ok) {
        setToast(`Idea saved: ${result.idea.idea_id}`);
        setTimeout(() => setToast(null), 3000);
      }
    } catch (err) {
      setError('Failed to save idea');
    } finally {
      setLoading(false);
    }
  };

  // Share (placeholder)
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `${symbol} Technical Analysis`,
        text: `${setupData?.technical_bias?.toUpperCase()} bias with ${Math.round((setupData?.bias_confidence || 0) * 100)}% confidence`,
        url: window.location.href,
      });
    }
  };

  // Derived data
  // Extract data from new API format
  const pattern = setupData?.pattern;
  const levels = setupData?.levels || [];
  const structure = setupData?.structure;
  const setup = setupData?.setup;
  
  // Map to old format for components (temporary compatibility)
  const topSetup = setupData ? {
    pattern: pattern,
    levels: levels,
    direction: setup?.direction,
    confidence: setup?.confidence,
    trigger: setup?.trigger,
    invalidation: setup?.invalidation,
    targets: setup?.targets,
  } : null;
  
  const technicalBias = setup?.direction || 'neutral';
  const biasConfidence = setup?.confidence || 0;

  // Determine what to show based on view mode and layer toggles
  const showPatterns = viewMode !== 'clean' && layerVisibility.patterns;
  const showLevels = layerVisibility.levels;
  const showStructure = layerVisibility.structure;
  const showIndicators = viewMode === 'manual';

  // Toggle layer visibility
  const toggleLayer = (layer) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  return (
    <Container data-testid="research-view">
      {/* Top Control Bar */}
      <TopBar>
        <ControlsLeft>
          {/* Search Asset */}
          <SearchWrapper>
            <SearchInput
              type="text"
              placeholder="Search"
              value={showDropdown ? searchQuery : (searchQuery || '')}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              data-testid="asset-search"
            />
            {showDropdown && filteredSymbols.length > 0 && (
              <SymbolDropdown>
                {filteredSymbols.map(s => (
                  <SymbolOption
                    key={s}
                    $active={s === symbol}
                    onMouseDown={() => handleSymbolSelect(s)}
                  >
                    {s.replace('USDT', '')}
                  </SymbolOption>
                ))}
              </SymbolDropdown>
            )}
          </SearchWrapper>

          {/* Timeframe Selector */}
          <TfGroup>
            {TIMEFRAMES.map(tf => (
              <TfButton
                key={tf}
                $active={timeframe === tf}
                onClick={() => setTimeframe(tf)}
                data-testid={`tf-${tf}`}
              >
                {tf.toUpperCase()}
              </TfButton>
            ))}
          </TfGroup>

          {/* Chart Type */}
          <ChartTypeGroup>
            <ChartTypeBtn
              $active={chartType === 'candles'}
              onClick={() => setChartType('candles')}
              title="Candles"
            >
              <BarChart2 />
            </ChartTypeBtn>
            <ChartTypeBtn
              $active={chartType === 'line'}
              onClick={() => setChartType('line')}
              title="Line"
            >
              <LineChart />
            </ChartTypeBtn>
          </ChartTypeGroup>

          {/* View Mode */}
          <ViewModeWrapper>
            <ViewModeButton 
              onClick={() => setShowViewModeDropdown(!showViewModeDropdown)}
              data-testid="view-mode"
            >
              {viewMode === 'auto' ? 'Auto TA' : viewMode === 'manual' ? 'Manual Layers' : 'Clean View'}
              <ChevronDown />
            </ViewModeButton>
            {showViewModeDropdown && (
              <ViewModeDropdown>
                <ViewModeOption 
                  $active={viewMode === 'auto'} 
                  onClick={() => { setViewMode('auto'); setShowViewModeDropdown(false); }}
                >
                  Auto TA
                </ViewModeOption>
                <ViewModeOption 
                  $active={viewMode === 'manual'} 
                  onClick={() => { setViewMode('manual'); setShowViewModeDropdown(false); }}
                >
                  Manual Layers
                </ViewModeOption>
                <ViewModeOption 
                  $active={viewMode === 'clean'} 
                  onClick={() => { setViewMode('clean'); setShowViewModeDropdown(false); }}
                >
                  Clean View
                </ViewModeOption>
              </ViewModeDropdown>
            )}
          </ViewModeWrapper>
          
          {/* Layer Toggles */}
          <LayerToggles>
            <LayerToggleBtn 
              $active={layerVisibility.patterns} 
              $color="#3b82f6"
              onClick={() => toggleLayer('patterns')}
              title="Show/Hide Patterns"
            >
              <span className="dot" /> Patterns
            </LayerToggleBtn>
            <LayerToggleBtn 
              $active={layerVisibility.levels} 
              $color="#05A584"
              onClick={() => toggleLayer('levels')}
              title="Show/Hide Levels"
            >
              <span className="dot" /> Levels
            </LayerToggleBtn>
            <LayerToggleBtn 
              $active={layerVisibility.structure} 
              $color="#f59e0b"
              onClick={() => toggleLayer('structure')}
              title="Show/Hide Structure"
            >
              <span className="dot" /> Structure
            </LayerToggleBtn>
            <LayerToggleBtn 
              $active={layerVisibility.targets} 
              $color="#8b5cf6"
              onClick={() => toggleLayer('targets')}
              title="Show/Hide Targets"
            >
              <span className="dot" /> Targets
            </LayerToggleBtn>
          </LayerToggles>
        </ControlsLeft>
      </TopBar>

      {/* Main Content */}
      <MainContent>
        {/* Error Banner */}
        {error && (
          <ErrorBanner>
            <AlertTriangle size={18} />
            {error}
          </ErrorBanner>
        )}

        {/* Chart Section */}
        <ChartSection style={{ position: 'relative' }}>
          <ResearchChart
            candles={candles}
            pattern={pattern}
            levels={levels}
            setup={setup}
            chartType={chartType}
            height={400}
            showLevels={layerVisibility.levels}
            showPattern={layerVisibility.patterns}
          />
          {loading && (
            <LoadingOverlay>
              <Loader2 size={24} color="#3b82f6" />
              <span style={{ color: '#64748b', fontSize: 13 }}>Analyzing {symbol}...</span>
            </LoadingOverlay>
          )}
        </ChartSection>

        {/* Debug Panel - Setup Summary */}
        <DebugPanel data-testid="debug-panel">
          <div className="debug-title">Setup Debug</div>
          <div className="debug-row">
            <span className="debug-label">Pattern:</span>
            <span className="debug-value">{pattern?.type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'None'}</span>
            <span className="debug-label">Confidence:</span>
            <span className="debug-value">{pattern?.confidence ? `${Math.round(pattern.confidence * 100)}%` : '-'}</span>
          </div>
          <div className="debug-row">
            <span className="debug-label">Levels:</span>
            <span className="debug-value">{levels?.length || 0}</span>
            <span className="debug-label">Structure:</span>
            <span className="debug-value">{structure?.trend?.charAt(0).toUpperCase() + structure?.trend?.slice(1) || '-'}</span>
          </div>
          <div className="debug-row">
            <span className="debug-label">Direction:</span>
            <span className={`debug-value ${setup?.direction || 'neutral'}`}>{setup?.direction?.charAt(0).toUpperCase() + setup?.direction?.slice(1) || 'Neutral'}</span>
            <span className="debug-label">Setup Conf:</span>
            <span className="debug-value">{setup?.confidence ? `${Math.round(setup.confidence * 100)}%` : '-'}</span>
          </div>
          <div className="debug-row">
            <span className="debug-label">Trigger:</span>
            <span className="debug-value">{setup?.trigger?.toLocaleString() || '-'}</span>
            <span className="debug-label">Invalidation:</span>
            <span className="debug-value">{setup?.invalidation?.toLocaleString() || '-'}</span>
          </div>
          <div className="debug-row">
            <span className="debug-label">Targets:</span>
            <span className="debug-value">{setup?.targets?.map(t => t.toLocaleString()).join(' / ') || '-'}</span>
          </div>
          <div className="debug-row">
            <span className="debug-label">Timeframe:</span>
            <span className="debug-value">{timeframe.toUpperCase()}</span>
            <span className="debug-label">Candles:</span>
            <span className="debug-value">{candles?.length || 0}</span>
          </div>
        </DebugPanel>

        {/* Pattern Activation Layer */}
        <PatternActivationLayer
          setup={topSetup}
          activeElements={activeElements}
          onToggleElement={handleToggleElement}
        />

        {/* Deep Analysis Blocks */}
        <DeepAnalysisBlocks
          setup={topSetup}
          technicalBias={technicalBias}
          biasConfidence={biasConfidence}
        />
      </MainContent>

      {/* Toast */}
      {toast && <SuccessToast>{toast}</SuccessToast>}
    </Container>
  );
};

export default ResearchView;
