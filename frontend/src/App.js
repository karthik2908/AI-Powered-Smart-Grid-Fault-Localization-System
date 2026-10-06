import React, { useState, useEffect, useCallback } from 'react';
import GridMap from './components/GridMap';

// Initial mock data matching urban grid topology for offline preview or live backend sync
const INITIAL_NODES = [
  { node_id: 'SUB-01', name: 'Metro Primary Substation (33kV/11kV)', node_type: 'SUBSTATION', parent_id: null, latitude: 12.9716, longitude: 77.5946, current_voltage: 230.2, current_current: 24.5, frequency: 50.02, local_status: true, effective_status: true },
  { node_id: 'TX-01', name: 'Commercial Sector Transformer 1', node_type: 'TRANSFORMER', parent_id: 'SUB-01', latitude: 12.9750, longitude: 77.5980, current_voltage: 228.4, current_current: 14.2, frequency: 50.01, local_status: true, effective_status: true },
  { node_id: 'FDR-02', name: 'Main Feeder Pillar 2 (Osk & 5th St)', node_type: 'FEEDER', parent_id: 'TX-01', latitude: 12.9780, longitude: 77.6020, current_voltage: 227.1, current_current: 11.8, frequency: 50.00, local_status: true, effective_status: true },
  { node_id: 'TX-03', name: 'Residential Distribution Transformer 3', node_type: 'TRANSFORMER', parent_id: 'FDR-02', latitude: 12.9820, longitude: 77.6060, current_voltage: 226.5, current_current: 9.4, frequency: 49.98, local_status: true, effective_status: true },
  { node_id: 'TAP-04', name: 'Consumer Cluster Terminal 4', node_type: 'CONSUMER_TAP', parent_id: 'TX-03', latitude: 12.9860, longitude: 77.6100, current_voltage: 225.0, current_current: 5.1, frequency: 49.99, local_status: true, effective_status: true },
];

export default function App() {
  // Authentication & 2FA State
  const [isAuthenticated, setIsAuthenticated] = useState(true); // default true for demo presentation
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showOtpModal, setShowOtpModal] = useState(false);
  const [username, setUsername] = useState('OpID_admin_04');
  const [password, setPassword] = useState('••••••••••••');
  const [otpDigits, setOtpDigits] = useState(['7', '4', '0', '9', '2', '1']);
  const [otpTimer, setOtpTimer] = useState(285);

  // Grid Map & Telemetry State
  const [nodes, setNodes] = useState(INITIAL_NODES);
  const [lines, setLines] = useState([]);
  const [selectedNode, setSelectedNode] = useState(INITIAL_NODES[2]); // FDR-02 default selected
  const [alerts, setAlerts] = useState([
    { id: 1, type: 'CABLE_CUT', title: 'FAULT DETECTED: Feeder 2 Outage', node_id: 'FDR-02', area: 'Oak & 5th St', time: '14:32:01 UTC', severity: 'CRITICAL', details: 'Zero potential detected. Downstream nodes isolated via Zip-Line logic.' },
    { id: 2, type: 'OVERLOAD', title: 'Warning: High Load at TX-01', node_id: 'TX-01', area: 'Commercial Zone', time: '14:20:15 UTC', severity: 'WARNING', details: 'Current approaching 92% of continuous thermal capacity.' },
  ]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [mapMode, setMapMode] = useState('satellite'); // 'normal' | 'satellite'

  // Compute Recursive Zip-Line Status for all nodes and lines
  const recalculateZipLineTopology = useCallback((currentNodes) => {
    const nodeMap = new Map();
    currentNodes.forEach(n => nodeMap.set(n.node_id, { ...n }));

    // Evaluate recursive effective status
    const evaluateEffective = (nodeId) => {
      const node = nodeMap.get(nodeId);
      if (!node) return false;
      if (!node.local_status) return false;
      if (!node.parent_id) return node.local_status;
      return node.local_status && evaluateEffective(node.parent_id);
    };

    const updatedNodes = currentNodes.map(node => {
      const effective = evaluateEffective(node.node_id);
      return { ...node, effective_status: effective };
    });

    // Reconstruct connection lines with Green/Red status
    const updatedLines = [];
    const updatedMap = new Map();
    updatedNodes.forEach(n => updatedMap.set(n.node_id, n));

    updatedNodes.forEach(node => {
      if (node.parent_id && updatedMap.has(node.parent_id)) {
        const parent = updatedMap.get(node.parent_id);
        const isEnergized = parent.effective_status && node.effective_status;
        updatedLines.push({
          id: `line-${parent.node_id}-${node.node_id}`,
          from: [parent.latitude, parent.longitude],
          to: [node.latitude, node.longitude],
          isEnergized,
          color: isEnergized ? '#10B981' : '#EF4444' // Emerald / Red
        });
      }
    });

    setNodes(updatedNodes);
    setLines(updatedLines);
  }, []);

  useEffect(() => {
    recalculateZipLineTopology(INITIAL_NODES);
  }, [recalculateZipLineTopology]);

  // Fault Simulation Handlers
  const triggerSimulation = (scenario, targetNodeId) => {
    setIsSimulating(true);
    setNodes(prev => {
      const updated = prev.map(n => {
        if (n.node_id === targetNodeId) {
          if (scenario === 'CABLE_CUT') {
            return { ...n, local_status: false, current_voltage: 0.0, current_current: 0.0 };
          } else if (scenario === 'SHORT_CIRCUIT') {
            return { ...n, local_status: false, current_voltage: 18.0, current_current: 48.2 };
          }
        }
        return n;
      });
      recalculateZipLineTopology(updated);
      return updated;
    });

    // Append Alert
    const newAlert = {
      id: Date.now(),
      type: scenario,
      title: scenario === 'CABLE_CUT' ? `CRITICAL: Cable Discontinuity at ${targetNodeId}` : `CRITICAL: Short Circuit Surge at ${targetNodeId}`,
      node_id: targetNodeId,
      area: 'Distribution Sector 4',
      time: new Date().toLocaleTimeString() + ' UTC',
      severity: 'CRITICAL',
      details: scenario === 'CABLE_CUT' ? 'AI Model diagnosed Cable Cut with 99.2% confidence.' : 'Surge current 48.2A detected. Breaker isolation triggered.'
    };
    setAlerts(prev => [newAlert, ...prev]);
    setTimeout(() => setIsSimulating(false), 300);
  };

  const resetGrid = () => {
    setNodes(INITIAL_NODES);
    recalculateZipLineTopology(INITIAL_NODES);
    setAlerts([]);
  };

  const energizedCount = nodes.filter(n => n.effective_status).length;
  const gridHealth = Math.round((energizedCount / nodes.length) * 100);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between z-20">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/20 border border-emerald-500 flex items-center justify-center text-emerald-400 font-bold text-xl">
            ⚡
          </div>
          <div>
            <h1 className="text-base font-bold tracking-wide text-white">
              AI-Powered Smart Grid Fault Localization System
            </h1>
            <p className="text-xs text-slate-400">Urban Low-Voltage Feeder & Substation Telemetry Network</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className={`flex items-center px-3 py-1 rounded-full text-xs font-semibold ${gridHealth === 100 ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800' : 'bg-red-950/80 text-red-400 border border-red-800 animate-pulse'}`}>
            <span className={`w-2 h-2 rounded-full mr-2 ${gridHealth === 100 ? 'bg-emerald-400' : 'bg-red-500'}`} />
            {gridHealth === 100 ? 'ALL FEEDERS ENERGIZED' : `GRID FAULT ACTIVE (${gridHealth}% HEALTH)`}
          </div>

          <div className="text-xs text-slate-400 border-l border-slate-800 pl-4 font-mono">
            OPERATOR: <span className="text-cyan-400 font-semibold">{username}</span> (2FA SECURED)
          </div>

          <button
            onClick={() => setShowLoginModal(true)}
            className="text-xs px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            2FA Security Auth
          </button>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left GIS Leaflet Map Viewport */}
        <div className="flex-1 relative bg-slate-900 flex flex-col">
          {/* Simulation & Control Bar */}
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-700/80 rounded-xl p-3 shadow-2xl flex items-center space-x-3">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Test Simulations:</span>
            <button
              onClick={() => triggerSimulation('CABLE_CUT', 'FDR-02')}
              className="px-3 py-1 text-xs rounded-lg font-medium bg-red-600/20 text-red-400 border border-red-500/50 hover:bg-red-600 hover:text-white transition"
            >
              Simulate Cable Cut (Node FDR-02)
            </button>
            <button
              onClick={() => triggerSimulation('SHORT_CIRCUIT', 'TX-03')}
              className="px-3 py-1 text-xs rounded-lg font-medium bg-amber-600/20 text-amber-400 border border-amber-500/50 hover:bg-amber-600 hover:text-white transition"
            >
              Simulate Short Circuit (Node TX-03)
            </button>
            <button
              onClick={resetGrid}
              className="px-3 py-1 text-xs rounded-lg font-medium bg-emerald-600/20 text-emerald-400 border border-emerald-500/50 hover:bg-emerald-600 hover:text-white transition"
            >
              Reset Normal
            </button>
          </div>

          {/* Interactive GIS Map */}
          <div className="flex-1 w-full h-full">
            <GridMap
              nodes={nodes}
              lines={lines}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              mapMode={mapMode}
              onToggleMapMode={setMapMode}
            />
          </div>

          {/* Bottom Map Legend */}
          <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg px-4 py-2 flex items-center space-x-5 text-xs">
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
              <span className="text-slate-300">Active / Energized Line</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500 shadow-sm shadow-red-500/50 animate-pulse" />
              <span className="text-slate-300">Faulted / De-energized Line</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="text-cyan-400 font-mono">⚡ Zip-Line Recursive Hierarchy</span>
            </div>
          </div>
        </div>

        {/* Right Telemetry & Operations Sidebar */}
        <aside className="w-96 border-l border-slate-800 bg-slate-900/95 flex flex-col p-5 overflow-y-auto space-y-6">
          {/* Key Metrics Gauges */}
          <div>
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">System Overview</h2>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
                <span className="text-xs text-slate-400">Line Voltage</span>
                <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">230.1 V</div>
                <div className="text-[10px] text-slate-500">Nominal: 230V ±5%</div>
              </div>
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
                <span className="text-xs text-slate-400">Current Load</span>
                <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">15.2 A</div>
                <div className="text-[10px] text-slate-500">Continuous rating: 30A</div>
              </div>
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
                <span className="text-xs text-slate-400">Grid Frequency</span>
                <div className="text-xl font-bold text-emerald-400 font-mono mt-1">50.08 Hz</div>
                <div className="text-[10px] text-slate-500">Synchronous Band: 50Hz</div>
              </div>
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-3">
                <span className="text-xs text-slate-400">Estimated MTTR</span>
                <div className="text-xl font-bold text-amber-400 font-mono mt-1">01h 45m</div>
                <div className="text-[10px] text-slate-500">Down from 4h 30m</div>
              </div>
            </div>
          </div>

          {/* Selected Node Telemetry Inspector */}
          {selectedNode && (
            <div className="bg-slate-800/40 border border-slate-700/80 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-cyan-400 font-mono">{selectedNode.node_id}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${selectedNode.effective_status ? 'bg-emerald-950 text-emerald-400 border border-emerald-700' : 'bg-red-950 text-red-400 border border-red-700'}`}>
                  {selectedNode.effective_status ? 'ENERGIZED' : 'DE-ENERGIZED'}
                </span>
              </div>
              <h3 className="text-sm font-semibold text-white">{selectedNode.name}</h3>
              <p className="text-xs text-slate-400 mt-0.5">Parent Node: <span className="font-mono text-slate-300">{selectedNode.parent_id || 'Root Substation'}</span></p>

              <div className="mt-4 space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-700/50">
                  <span className="text-slate-400">Measured Voltage:</span>
                  <span className="font-mono font-semibold text-white">{selectedNode.current_voltage} V</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-700/50">
                  <span className="text-slate-400">Measured Current:</span>
                  <span className="font-mono font-semibold text-white">{selectedNode.current_current} A</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-700/50">
                  <span className="text-slate-400">Sensor Status:</span>
                  <span className={`font-semibold ${selectedNode.local_status ? 'text-emerald-400' : 'text-red-400'}`}>
                    {selectedNode.local_status ? 'Healthy Continuity' : 'Trip / Loss Detected'}
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Effective Status:</span>
                  <span className={`font-semibold ${selectedNode.effective_status ? 'text-emerald-400' : 'text-red-400'}`}>
                    {selectedNode.effective_status ? 'Supplying Power' : 'Downstream Outage (Zip-Line)'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Live Alert Dispatch Panel */}
          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Live Outage Alerts ({alerts.length})</h2>
              {alerts.length > 0 && (
                <button onClick={() => setAlerts([])} className="text-[11px] text-slate-400 hover:text-slate-200">Clear</button>
              )}
            </div>

            <div className="space-y-3 overflow-y-auto pr-1">
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
                  No active grid faults detected. Grid telemetry nominal.
                </div>
              ) : (
                alerts.map(a => (
                  <div key={a.id} className="p-3 rounded-xl bg-red-950/30 border border-red-800/60 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-red-400">{a.title}</span>
                      <span className="text-[10px] text-slate-400 font-mono">{a.time}</span>
                    </div>
                    <p className="text-slate-300 text-[11px] leading-relaxed">{a.details}</p>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                      <span>Area: <span className="text-white">{a.area}</span></span>
                      <span className="text-emerald-400 font-semibold cursor-pointer hover:underline">Dispatch Crew →</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>
      </div>

      {/* 2FA Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-lg text-white">Operator 2FA Authentication</h3>
              <button onClick={() => setShowLoginModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            <p className="text-xs text-slate-400">Two-Factor Authentication is enforced for all grid switching operations.</p>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-300">Operator ID</label>
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  className="w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                />
              </div>
              <div>
                <label className="text-xs text-slate-300">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
                />
              </div>
              <button
                onClick={() => { setShowLoginModal(false); setShowOtpModal(true); }}
                className="w-full py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm transition"
              >
                Sign In & Request OTP 🔒
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 2FA OTP Modal */}
      {showOtpModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-cyan-500/40 rounded-2xl p-6 shadow-2xl text-center space-y-5">
            <div className="w-12 h-12 mx-auto rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xl font-bold border border-cyan-500/40">
              🔑
            </div>
            <div>
              <h3 className="font-bold text-lg text-white">Two-Factor Verification</h3>
              <p className="text-xs text-slate-400 mt-1">A 6-digit code has been dispatched to operator email.</p>
            </div>

            <div className="flex justify-center space-x-2">
              {otpDigits.map((digit, i) => (
                <input
                  key={i}
                  type="text"
                  maxLength={1}
                  value={digit}
                  readOnly
                  className="w-11 h-13 text-center text-xl font-bold bg-slate-800 border-2 border-cyan-500/60 rounded-xl text-cyan-300 focus:outline-none"
                />
              ))}
            </div>

            <p className="text-xs text-slate-400 font-mono">Code expires in <span className="text-cyan-400">04:45</span></p>

            <button
              onClick={() => { setShowOtpModal(false); alert('2FA Authenticated Successfully. Operator session authorized.'); }}
              className="w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-cyan-500/30"
            >
              Verify & Access Grid Console
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
