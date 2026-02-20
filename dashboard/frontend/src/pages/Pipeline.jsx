import React, { useState, useEffect } from 'react';
import { apiGet, apiPost } from '../hooks/useApi';

export default function Pipeline() {
  const [steps, setSteps] = useState([]);
  const [runningStep, setRunningStep] = useState(null);
  const [expandedLog, setExpandedLog] = useState(null);
  const [progress, setProgress] = useState(null);
  const [toast, setToast] = useState(null);

  const refresh = () => apiGet('/api/pipeline/status').then(d => setSteps(d.steps || []));

  useEffect(() => {
    refresh();

    // Restore progress state from server on mount (handles tab navigation)
    apiGet('/api/pipeline/progress').then(p => {
      if (p && p.running) {
        setProgress(p);
        setRunningStep('all');
      }
    }).catch(() => {});
  }, []);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Pipeline runners
  const runStep = async (stepId) => {
    setRunningStep(stepId);
    try {
      await apiPost('/api/pipeline/run', { step: stepId });
      await refresh();
    } catch (e) { console.error(e); }
    setRunningStep(null);
  };

  const runAll = async () => {
    setRunningStep('all');
    setProgress({ running: true, current: 0, total: steps.length || 3, current_step: '' });
    try {
      await apiPost('/api/pipeline/run', {});
      await refresh();
    } catch (e) { console.error(e); }
    setProgress(null);
    setRunningStep(null);
  };

  // Poll progress while pipeline is running
  useEffect(() => {
    if (runningStep !== 'all') return;
    const interval = setInterval(async () => {
      try {
        const p = await apiGet('/api/pipeline/progress');
        if (p && p.running) {
          setProgress(p);
        } else {
          // Pipeline finished — clear running state, keep last step statuses
          setProgress(null);
          setRunningStep(null);
        }
        // Also refresh step statuses so badges update live
        const s = await apiGet('/api/pipeline/status');
        setSteps(s.steps || []);
      } catch (e) { /* ignore */ }
    }, 1500);
    return () => clearInterval(interval);
  }, [runningStep]);

  return (
    <div>
      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>{toast.msg}</div>
        </div>
      )}

      {/* Pipeline Steps */}
      <div className="flex-between mb-24">
        <div>
          <h2 className="page-title">Pipeline Runner</h2>
          <p className="page-subtitle">Execute the data pipeline: Fetch → Clean → Build Dataset</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={runAll}
          disabled={!!runningStep}
        >
          {runningStep === 'all' ? 'Running All...' : 'Run Full Pipeline'}
        </button>
      </div>

      {/* Progress bar */}
      {progress && progress.running && (
        <div className="card mb-24" style={{ padding: '16px 22px' }}>
          <div className="flex-between" style={{ marginBottom: 8 }}>
            <span style={{ fontSize: 13, fontWeight: 600 }}>
              Running: {progress.current_step || '...'}
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              Step {progress.current + 1} of {progress.total}
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

      <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap', marginBottom: 32 }}>
        {steps.map((step, idx) => (
          <React.Fragment key={step.id}>
            {idx > 0 && (
              <div style={{
                display: 'flex', alignItems: 'center', color: 'var(--text-muted)',
                fontSize: 24, paddingTop: 40, alignSelf: 'flex-start'
              }}>→</div>
            )}
            <div className="card" style={{ flex: '1 1 220px', minWidth: 220, maxWidth: 340 }}>
              <div className="flex-between mb-16">
                <h3 style={{ fontSize: 15 }}>{step.label}</h3>
                <span className={`badge badge-${step.status}`}>{step.status}</span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
                {step.description}
              </p>
              {step.last_run && (
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>
                  Last run: {new Date(step.last_run * 1000).toLocaleString()}
                </p>
              )}
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => runStep(step.id)}
                  disabled={!!runningStep}
                >
                  {runningStep === step.id ? 'Running...' : 'Run'}
                </button>
                {step.output && (
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => setExpandedLog(expandedLog === step.id ? null : step.id)}
                  >
                    {expandedLog === step.id ? 'Hide Log' : 'View Log'}
                  </button>
                )}
              </div>
              {expandedLog === step.id && step.output && (
                <div className="log-viewer" style={{ marginTop: 12 }}>{step.output}</div>
              )}
            </div>
          </React.Fragment>
        ))}
      </div>

      {steps.length === 0 && (
        <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40, marginBottom: 32 }}>
          Loading pipeline status...
        </div>
      )}
    </div>
  );
}
