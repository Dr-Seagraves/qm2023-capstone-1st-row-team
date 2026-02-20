import React, { useState, useEffect } from 'react';
import { apiGet } from '../hooks/useApi';

const LOG_MODULES = ['fetch', 'clean', 'filter', 'merge', 'dashboard', 'pipeline', 'general'];

export default function Logs() {
  const [module, setModule] = useState('pipeline');
  const [logData, setLogData] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const load = () => {
    apiGet(`/api/logs/${module}?tail=300`).then(setLogData);
  };

  useEffect(() => { load(); }, [module]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, module]);

  return (
    <div>
      <h2 className="page-title">Activity Logs</h2>
      <p className="page-subtitle">View pipeline execution logs for debugging and monitoring</p>

      <div className="flex-between mb-24" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {LOG_MODULES.map(m => (
            <button
              key={m}
              className={`btn ${module === m ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              onClick={() => setModule(m)}
            >
              {m}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <label className="toggle" title="Auto-refresh every 3s">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={e => setAutoRefresh(e.target.checked)}
            />
            <span className="toggle-slider" />
          </label>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Auto-refresh</span>
          <button className="btn btn-secondary btn-sm" onClick={load}>Refresh</button>
        </div>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 13, fontWeight: 600 }}>{module}.log</span>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {logData ? `${logData.showing} / ${logData.lines} lines` : 'Loading...'}
          </span>
        </div>
        <div className="log-viewer" style={{ borderRadius: 0, border: 'none', maxHeight: 600, minHeight: 300 }}>
          {logData?.content || 'No log data available. Run a pipeline step to generate logs.'}
        </div>
      </div>
    </div>
  );
}
