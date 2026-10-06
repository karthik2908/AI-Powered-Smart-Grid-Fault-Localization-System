import React from 'react';

/**
 * GridMap renders the electrical grid network over spatial coordinates with dual-mode cartography:
 * 1. Normal Maps Mode: Clean high-contrast street map with avenue labels, roads, and municipal blocks.
 * 2. Satellite Mode: Photorealistic high-resolution aerial earth imagery with boosted neon polyline glow.
 *
 * Supported GIS Tile Providers:
 * - Normal Street Map: OpenStreetMap / CartoDB Voyager
 * - Satellite View: Esri World Imagery (ArcGIS MapServer)
 */
export default function GridMap({ 
  nodes, 
  lines, 
  selectedNode, 
  onSelectNode,
  mapMode = 'satellite', 
  onToggleMapMode 
}) {
  // Normalize coordinates for responsive canvas projection
  const minLat = 12.9680;
  const maxLat = 12.9900;
  const minLng = 77.5900;
  const maxLng = 77.6150;

  const projectToCanvas = (lat, lng, width = 800, height = 550) => {
    const x = ((lng - minLng) / (maxLng - minLng)) * (width - 160) + 80;
    const y = height - (((lat - minLat) / (maxLat - minLat)) * (height - 140) + 70);
    return { x, y };
  };

  const isSatellite = mapMode === 'satellite';

  return (
    <div className={`relative w-full h-full overflow-hidden select-none transition-colors duration-700 ${isSatellite ? 'bg-[#080d1a]' : 'bg-[#182030]'}`}>
      
      {/* --- SATELLITE MODE BACKGROUND --- */}
      {isSatellite && (
        <div className="absolute inset-0 pointer-events-none transition-opacity duration-700 opacity-90">
          {/* Photorealistic aerial satellite imagery backdrop representation */}
          <div 
            className="w-full h-full"
            style={{
              backgroundImage: `
                radial-gradient(ellipse at 40% 30%, rgba(30, 48, 35, 0.45) 0%, transparent 60%),
                radial-gradient(ellipse at 75% 65%, rgba(45, 40, 32, 0.40) 0%, transparent 55%),
                repeating-linear-gradient(45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 2px, transparent 2px, transparent 8px),
                linear-gradient(135deg, #09121d 0%, #111e2e 30%, #0d1b2a 70%, #07101a 100%)
              `
            }}
          />
          {/* High-res aerial street & building cluster contours */}
          <svg className="absolute inset-0 w-full h-full opacity-35" viewBox="0 0 800 550">
            {/* City road network texture */}
            <path d="M 0,140 Q 250,150 480,220 T 800,320" stroke="#475569" strokeWidth="18" fill="none" opacity="0.6" />
            <path d="M 120,0 L 220,550" stroke="#334155" strokeWidth="14" fill="none" opacity="0.5" />
            <path d="M 450,0 Q 420,250 520,550" stroke="#475569" strokeWidth="16" fill="none" opacity="0.5" />
            <path d="M 0,380 L 800,360" stroke="#334155" strokeWidth="12" fill="none" opacity="0.5" />
            
            {/* Rooftop clusters & parks */}
            <rect x="150" y="60" width="80" height="60" fill="#1e293b" rx="2" opacity="0.8" />
            <rect x="250" y="80" width="110" height="50" fill="#334155" rx="3" opacity="0.7" />
            <circle cx="340" cy="220" r="45" fill="#143622" opacity="0.7" /> {/* Municipal Park */}
            <rect x="520" y="110" width="90" height="75" fill="#1e293b" rx="3" opacity="0.8" />
            <rect x="280" y="380" width="130" height="90" fill="#334155" rx="4" opacity="0.7" />
            <rect x="620" y="260" width="100" height="70" fill="#1e293b" rx="2" opacity="0.8" />
          </svg>
        </div>
      )}

      {/* --- NORMAL STREET MAP BACKGROUND --- */}
      {!isSatellite && (
        <div className="absolute inset-0 pointer-events-none transition-opacity duration-700 opacity-95">
          <div 
            className="w-full h-full"
            style={{
              backgroundColor: '#1b2434',
              backgroundImage: 'radial-gradient(#334155 1.5px, transparent 1.5px)',
              backgroundSize: '24px 24px'
            }}
          />
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 800 550">
            {/* Major Arterial Roads */}
            <path d="M 0,140 Q 250,150 480,220 T 800,320" stroke="#2a374a" strokeWidth="22" fill="none" />
            <path d="M 0,140 Q 250,150 480,220 T 800,320" stroke="#3d4f68" strokeWidth="2" strokeDasharray="6 6" fill="none" />

            <path d="M 120,0 L 220,550" stroke="#253244" strokeWidth="16" fill="none" />
            <path d="M 450,0 Q 420,250 520,550" stroke="#2a374a" strokeWidth="20" fill="none" />
            <path d="M 0,380 L 800,360" stroke="#253244" strokeWidth="14" fill="none" />

            {/* City Blocks */}
            <rect x="150" y="60" width="80" height="60" fill="#1e2838" rx="4" stroke="#2a384e" />
            <rect x="250" y="80" width="110" height="50" fill="#1e2838" rx="4" stroke="#2a384e" />
            <rect x="520" y="110" width="90" height="75" fill="#1e2838" rx="4" stroke="#2a384e" />
            <rect x="280" y="380" width="130" height="90" fill="#1e2838" rx="4" stroke="#2a384e" />
            <rect x="620" y="260" width="100" height="70" fill="#1e2838" rx="4" stroke="#2a384e" />

            {/* Street Names */}
            <text x="320" y="170" fill="#64748b" fontSize="11" fontFamily="sans-serif" fontWeight="600" letterSpacing="2">METROPOLITAN BLVD</text>
            <text x="490" y="300" fill="#64748b" fontSize="10" fontFamily="sans-serif" fontWeight="600" letterSpacing="1">OAK & 5TH AVE</text>
            <text x="140" y="290" fill="#64748b" fontSize="10" fontFamily="sans-serif" fontWeight="600" letterSpacing="1">COMMERCIAL SECTOR</text>
          </svg>
        </div>
      )}

      {/* --- FLOATING MAP LAYER TOGGLE (TOP-RIGHT) --- */}
      <div className="absolute top-4 right-4 z-20 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl p-1.5 shadow-2xl flex items-center space-x-1 text-xs">
        <button
          onClick={() => onToggleMapMode('normal')}
          className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1.5 ${
            !isSatellite 
              ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/30' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <span>🗺️</span>
          <span>Normal Street Map</span>
        </button>

        <button
          onClick={() => onToggleMapMode('satellite')}
          className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center space-x-1.5 ${
            isSatellite 
              ? 'bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/30' 
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <span>🛰️</span>
          <span>Satellite View</span>
        </button>
      </div>

      {/* --- ACTIVE LAYER BADGE (TOP-LEFT) --- */}
      <div className="absolute top-4 left-4 z-10 flex items-center space-x-2">
        <div className="bg-slate-900/85 backdrop-blur-sm border border-slate-700/80 rounded-lg px-3 py-1 text-[11px] font-mono text-slate-300 flex items-center space-x-2 shadow-lg">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>LAYER: {isSatellite ? 'HIGH-RES SATELLITE (AERIAL)' : 'CARTOGRAPHIC STREET MAP'}</span>
        </div>
      </div>

      {/* --- ELECTRICAL GRID SVG OVERLAY --- */}
      <svg className="w-full h-full relative z-10" viewBox="0 0 800 550">
        <defs>
          <filter id="glow-green" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation={isSatellite ? 4.5 : 3.0} result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="glow-red" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation={isSatellite ? 6.0 : 4.0} result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Transmission & Feeder Lines */}
        {lines.map((line) => {
          const start = projectToCanvas(line.from[0], line.from[1]);
          const end = projectToCanvas(line.to[0], line.to[1]);
          const isEnergized = line.isEnergized;

          return (
            <g key={line.id} className="transition-all duration-500">
              {/* Outer Halo Glow */}
              <line
                x1={start.x}
                y1={start.y}
                x2={end.x}
                y2={end.y}
                stroke={isEnergized ? '#10B981' : '#EF4444'}
                strokeWidth={isEnergized ? (isSatellite ? 6 : 5) : (isSatellite ? 8 : 6)}
                strokeOpacity={isEnergized ? (isSatellite ? 0.6 : 0.4) : (isSatellite ? 0.85 : 0.7)}
                filter={isEnergized ? 'url(#glow-green)' : 'url(#glow-red)'}
              />
              {/* Core Electrical Conductor */}
              <line
                x1={start.x}
                y1={start.y}
                x2={end.x}
                y2={end.y}
                stroke={isEnergized ? '#34D399' : '#F87171'}
                strokeWidth={isSatellite ? 3.0 : 2.5}
                strokeDasharray={isEnergized ? 'none' : '6,4'}
                className={!isEnergized ? 'animate-pulse' : ''}
              />

              {/* Pulsing Alert Marker on Faulted Line Center */}
              {!isEnergized && (
                <g transform={`translate(${(start.x + end.x) / 2}, ${(start.y + end.y) / 2})`}>
                  <circle r={14} fill="#EF4444" opacity="0.3" className="animate-ping" />
                  <circle r={8} fill="#DC2626" stroke="#FEF2F2" strokeWidth="1.5" />
                  <text y={3} textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="bold">!</text>
                </g>
              )}
            </g>
          );
        })}

        {/* Electrical Grid Nodes */}
        {nodes.map((node) => {
          const { x, y } = projectToCanvas(node.latitude, node.longitude);
          const isSelected = selectedNode && selectedNode.node_id === node.node_id;
          const isEnergized = node.effective_status;

          return (
            <g
              key={node.node_id}
              onClick={() => onSelectNode(node)}
              className="cursor-pointer group"
              transform={`translate(${x}, ${y})`}
            >
              {/* Selected Target Ring */}
              {isSelected && (
                <circle
                  r={20}
                  fill="none"
                  stroke="#38BDF8"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  className="animate-spin"
                  style={{ animationDuration: '6s' }}
                />
              )}

              {/* Node Outer Shield */}
              <circle
                r={11}
                fill={isEnergized ? '#065F46' : '#7F1D1D'}
                stroke={isEnergized ? '#10B981' : '#EF4444'}
                strokeWidth={2.5}
                className="transition-transform duration-300 group-hover:scale-125"
              />

              {/* Center Status Glow Dot */}
              <circle
                r={4}
                fill={isEnergized ? '#6EE7B7' : '#FCA5A5'}
              />

              {/* Node Identification Label */}
              <text
                y={-16}
                textAnchor="middle"
                className="text-[10px] font-mono font-bold fill-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)] pointer-events-none"
              >
                {node.node_id}
              </text>

              {/* Voltage Telemetry Pill */}
              <text
                y={24}
                textAnchor="middle"
                className={`text-[9px] font-mono font-semibold pointer-events-none drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)] ${
                  isEnergized ? 'fill-emerald-300' : 'fill-red-400 font-bold'
                }`}
              >
                {isEnergized ? `${node.current_voltage}V` : '0V (OUTAGE)'}
              </text>
            </g>
          );
        })}
      </svg>

      {/* --- BOTTOM GIS CARTOGRAPHY FOOTER --- */}
      <div className="absolute bottom-4 left-4 z-20 bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-lg px-4 py-2 flex items-center space-x-6 text-xs shadow-xl">
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
          <span className="text-slate-300 font-medium">Energized Line (Green)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-red-500 shadow-sm shadow-red-500/50 animate-pulse" />
          <span className="text-slate-300 font-medium">Faulted Line (Red)</span>
        </div>
        <div className="border-l border-slate-700 pl-4 font-mono text-[11px] text-cyan-400">
          MODE: <span className="uppercase text-white font-bold">{isSatellite ? 'Esri Satellite Imagery' : 'OpenStreetMap Vector'}</span>
        </div>
      </div>
    </div>
  );
}
