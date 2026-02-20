import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { apiGet, apiPost } from '../hooks/useApi';

const CHART_TYPES = [
  { value: 'line', label: 'Line' },
  { value: 'bar', label: 'Bar' },
  { value: 'area', label: 'Area' },
  { value: 'scatter', label: 'Scatter' },
];

const COLORS = ['#ffffff', '#3b82f6', '#22c55e', '#f59e0b', '#a78bfa', '#ef4444'];

export default function Charts() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDs, setSelectedDs] = useState('');
  const [columns, setColumns] = useState([]);
  const [xCol, setXCol] = useState('');
  const [yCols, setYCols] = useState([]);
  const [chartType, setChartType] = useState('line');
  const [chartTitle, setChartTitle] = useState('');
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    apiGet('/api/charts/columns').then(d => {
      setDatasets(d || []);
    });
  }, []);

  // When dataset changes, reset column selections
  useEffect(() => {
    if (!selectedDs) { setColumns([]); return; }
    const ds = datasets.find(d => d.key === selectedDs);
    if (ds) {
      setColumns(ds.columns || []);
      setXCol('');
      setYCols([]);
      setChartData(null);
    }
  }, [selectedDs, datasets]);

  const toggleYCol = (col) => {
    setYCols(prev =>
      prev.includes(col) ? prev.filter(c => c !== col) : [...prev, col]
    );
  };

  const generate = useCallback(async () => {
    if (!selectedDs || !xCol || yCols.length === 0) return;
    setLoading(true);
    setError('');
    try {
      const res = await apiPost('/api/charts/data', {
        dataset: selectedDs,
        x_column: xCol,
        y_columns: yCols,
        limit: 5000,
      });
      if (res.error) { setError(res.error); }
      else { setChartData(res); }
    } catch (e) {
      setError('Failed to load chart data');
    }
    setLoading(false);
  }, [selectedDs, xCol, yCols]);

  const exportChart = async (fmt = 'png') => {
    setExporting(true);
    try {
      const resp = await fetch('http://localhost:5000/api/charts/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset: selectedDs,
          x_column: xCol,
          y_columns: yCols,
          chart_type: chartType,
          title: chartTitle || 'Chart',
          format: fmt,
        }),
      });
      if (!resp.ok) throw new Error('Export failed');
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chart.${fmt}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError('Export failed. Ensure plotly and kaleido are installed.');
    }
    setExporting(false);
  };

  const renderChart = () => {
    if (!chartData?.rows) return null;
    const data = chartData.rows;
    const props = {
      data,
      margin: { top: 10, right: 30, left: 10, bottom: 5 },
    };
    const xKey = chartData.x_column;
    const yKeys = chartData.y_columns || [];

    const commonChildren = (
      <>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey={xKey}
          stroke="#444"
          tick={{ fontSize: 11 }}
          angle={data.length > 30 ? -45 : 0}
          textAnchor={data.length > 30 ? 'end' : 'middle'}
          height={data.length > 30 ? 60 : 30}
        />
        <YAxis stroke="#444" tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={{
            background: '#111',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 4,
            fontSize: 12,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </>
    );

    switch (chartType) {
      case 'bar':
        return (
          <BarChart {...props}>
            {commonChildren}
            {yKeys.map((y, i) => (
              <Bar key={y} dataKey={y} fill={COLORS[i % COLORS.length]} />
            ))}
          </BarChart>
        );
      case 'area':
        return (
          <AreaChart {...props}>
            {commonChildren}
            {yKeys.map((y, i) => (
              <Area
                key={y} type="monotone" dataKey={y}
                stroke={COLORS[i % COLORS.length]}
                fill={COLORS[i % COLORS.length]}
                fillOpacity={0.15}
              />
            ))}
          </AreaChart>
        );
      case 'scatter':
        return (
          <ScatterChart {...props}>
            {commonChildren}
            {yKeys.map((y, i) => (
              <Scatter key={y} name={y} dataKey={y} fill={COLORS[i % COLORS.length]} />
            ))}
          </ScatterChart>
        );
      default:
        return (
          <LineChart {...props}>
            {commonChildren}
            {yKeys.map((y, i) => (
              <Line
                key={y} type="monotone" dataKey={y}
                stroke={COLORS[i % COLORS.length]}
                strokeWidth={2}
                dot={data.length < 60}
              />
            ))}
          </LineChart>
        );
    }
  };

  return (
    <div>
      <h2 className="page-title">Chart Builder</h2>
      <p className="page-subtitle">Generate interactive charts from any project dataset</p>

      {/* Controls */}
      <div className="card mb-24">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {/* Dataset */}
          <div>
            <label style={labelStyle}>Dataset</label>
            <select
              className="input"
              value={selectedDs}
              onChange={e => setSelectedDs(e.target.value)}
            >
              <option value="">Select a dataset...</option>
              {datasets.map(ds => (
                <option key={ds.key} value={ds.key}>
                  {ds.filename} ({ds.columns?.length || 0} cols)
                </option>
              ))}
            </select>
          </div>

          {/* Chart Type */}
          <div>
            <label style={labelStyle}>Chart Type</label>
            <div style={{ display: 'flex', gap: 8 }}>
              {CHART_TYPES.map(ct => (
                <button
                  key={ct.value}
                  className={`btn ${chartType === ct.value ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                  onClick={() => setChartType(ct.value)}
                >
                  {ct.label}
                </button>
              ))}
            </div>
          </div>

          {/* X Column */}
          <div>
            <label style={labelStyle}>X-Axis Column</label>
            <select
              className="input"
              value={xCol}
              onChange={e => setXCol(e.target.value)}
              disabled={columns.length === 0}
            >
              <option value="">Select X column...</option>
              {columns.map(c => (
                <option key={c.name} value={c.name}>{c.name} ({c.dtype})</option>
              ))}
            </select>
          </div>

          {/* Chart Title */}
          <div>
            <label style={labelStyle}>Title (optional)</label>
            <input
              className="input"
              placeholder="Chart title..."
              value={chartTitle}
              onChange={e => setChartTitle(e.target.value)}
            />
          </div>
        </div>

        {/* Y Columns */}
        {columns.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <label style={labelStyle}>Y-Axis Columns (select one or more)</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 6 }}>
              {columns.map(c => (
                <button
                  key={c.name}
                  className={`btn btn-sm ${yCols.includes(c.name) ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => toggleYCol(c.name)}
                  title={c.dtype}
                >
                  {c.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Generate */}
        <div style={{ marginTop: 20, display: 'flex', gap: 12, alignItems: 'center' }}>
          <button
            className="btn btn-primary"
            onClick={generate}
            disabled={loading || !selectedDs || !xCol || yCols.length === 0}
          >
            {loading ? 'Loading...' : 'Generate Chart'}
          </button>
          {chartData && (
            <>
              <button
                className="btn btn-secondary"
                onClick={() => exportChart('png')}
                disabled={exporting}
              >
                {exporting ? 'Exporting...' : 'Export PNG'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => exportChart('svg')}
                disabled={exporting}
              >
                Export SVG
              </button>
            </>
          )}
          {error && <span style={{ color: 'var(--accent-red)', fontSize: 13 }}>{error}</span>}
        </div>
      </div>

      {/* Chart Render Area */}
      {chartData?.rows && (
        <div className="card">
          <div className="card-header">
            <h3>{chartTitle || `${xCol} vs ${yCols.join(', ')}`}</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {chartData.rows.length} data points
            </span>
          </div>
          <div style={{ width: '100%', height: 450 }}>
            <ResponsiveContainer>
              {renderChart()}
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!chartData && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>
          Select a dataset, choose your X and Y columns, then click Generate Chart.
        </div>
      )}
    </div>
  );
}

const labelStyle = {
  display: 'block',
  fontSize: 12,
  fontWeight: 600,
  color: 'var(--text-secondary)',
  marginBottom: 6,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};
