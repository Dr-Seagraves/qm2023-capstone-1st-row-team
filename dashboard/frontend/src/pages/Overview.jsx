import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost } from '../hooks/useApi';

export default function Overview() {
  const navigate = useNavigate();
  const [pipeline, setPipeline] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(null);

  const refresh = () =>
    Promise.all([
      apiGet('/api/pipeline/status').catch(() => null),
      apiGet('/api/charts/columns').catch(() => []),
      apiGet('/api/pipeline/progress').catch(() => null),
    ]).then(([pipe, ds, prog]) => {
      setPipeline(pipe);
      setDatasets(ds || []);
      if (prog && prog.running) {
        setProgress(prog);
        setRunning(true);
      }
      setLoading(false);
    });

  useEffect(() => { refresh(); }, []);

  // Poll while pipeline is running
  useEffect(() => {
    if (!running) return;
    const iv = setInterval(async () => {
      try {
        const p = await apiGet('/api/pipeline/progress');
        if (p && p.running) {
          setProgress(p);
        } else {
          setRunning(false);
          setProgress(null);
          refresh();
        }
        const s = await apiGet('/api/pipeline/status');
        setPipeline(s);
      } catch (e) { /* ignore */ }
    }, 1500);
    return () => clearInterval(iv);
  }, [running]);

  const runFullPipeline = async () => {
    setRunning(true);
    setProgress({ running: true, current: 0, total: 3, current_step: '' });
    try {
      await apiPost('/api/pipeline/run', {});
      await refresh();
    } catch (e) { console.error(e); }
    setRunning(false);
    setProgress(null);
  };

  const steps = pipeline?.steps || [];
  const allSuccess = steps.length > 0 && steps.every(s => s.status === 'success');
  const anyError = steps.some(s => s.status === 'error');
  const anyRun = steps.some(s => s.last_run);
  const datasetCount = datasets.length;
  const hasMaster = datasets.some(d => d.key === 'master_dataset.csv');

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: 40 }}>Loading...</div>;
  }

  return (
    <div>
      <div className="flex-between mb-24">
        <div>
          <h2 className="page-title">Overview</h2>
          <p className="page-subtitle">Project status and data readiness</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={runFullPipeline}
          disabled={running}
        >
          {running ? 'Running Pipeline...' : 'Run Full Pipeline'}
        </button>
      </div>

      {/* Progress bar when running */}
      {progress && progress.running && (
        <div className="card mb-24" style={{ padding: '16px 22px' }}>
          <div className="flex-between" style={{ marginBottom: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 600 }}>
              {progress.current_step || 'Starting...'}
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              Step {(progress.current || 0) + 1} of {progress.total || 3}
            </span>
          </div>
          <div style={{
            width: '100%', height: 8, borderRadius: 4,
            background: 'rgba(148,163,184,0.1)', overflow: 'hidden',
          }}>
            <div style={{
              height: '100%', borderRadius: 4,
              background: 'linear-gradient(90deg, #3b82f6, #ffffff)',
              width: `${progress.total ? ((progress.current + 1) / progress.total) * 100 : 0}%`,
              transition: 'width 0.6s ease',
            }} />
          </div>
        </div>
      )}

      {/* Status cards */}
      <div className="grid-3 mb-24">
        <div className="card">
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 12 }}>
            Pipeline
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <span className={`status-dot ${allSuccess ? 'online' : anyError ? 'offline' : anyRun ? 'pending' : 'offline'}`} />
            <span style={{ fontSize: 16, fontWeight: 600 }}>
              {allSuccess ? 'Complete' : anyError ? 'Errors' : anyRun ? 'Partial' : 'Not run'}
            </span>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            {steps.filter(s => s.status === 'success').length} / {steps.length} steps
          </div>
        </div>

        <div className="card">
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 12 }}>
            Datasets
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <span className={`status-dot ${datasetCount > 0 ? 'online' : 'offline'}`} />
            <span style={{ fontSize: 16, fontWeight: 600 }}>{datasetCount} files</span>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            {hasMaster ? 'master_dataset.csv ready' : 'No master dataset yet'}
          </div>
        </div>

        <div className="card">
          <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--text-muted)', marginBottom: 12 }}>
            Master Dataset
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <span className={`status-dot ${hasMaster ? 'online' : 'offline'}`} />
            <span style={{ fontSize: 16, fontWeight: 600 }}>
              {hasMaster
                ? `${datasets.find(d => d.key === 'master_dataset.csv')?.columns?.length || 0} columns`
                : 'Not built'}
            </span>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            {hasMaster ? 'Ready for charting' : 'Run pipeline to build'}
          </div>
        </div>
      </div>

      {/* Pipeline step detail */}
      {steps.length > 0 && (
        <div className="card mb-24">
          <div className="card-header">
            <h3>Pipeline Steps</h3>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/pipeline')}>
              Details
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
            {steps.map(s => (
              <div key={s.id} style={{
                padding: '14px 16px',
                background: 'rgba(255,255,255,0.02)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>{s.label}</span>
                  <span className={`badge badge-${s.status}`}>{s.status}</span>
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {s.last_run ? new Date(s.last_run * 1000).toLocaleString() : 'Never run'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick links */}
      <div className="card">
        <div className="card-header">
          <h3>Available Datasets ({datasetCount})</h3>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/charts')}>
            Open Chart Builder
          </button>
        </div>
        {datasetCount === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: '16px 0' }}>
            No datasets yet. Click <strong>Run Full Pipeline</strong> above to fetch, clean, and build your data.
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr><th>File</th><th>Location</th><th>Columns</th></tr>
            </thead>
            <tbody>
              {datasets.slice(0, 15).map(ds => (
                <tr key={ds.key}>
                  <td className="mono" style={{ fontSize: 12 }}>{ds.filename}</td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{ds.folder}</td>
                  <td style={{ fontSize: 12 }}>{ds.columns?.length || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {datasetCount > 15 && (
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
            Showing 15 of {datasetCount} datasets
          </div>
        )}
      </div>
    </div>
  );
}
