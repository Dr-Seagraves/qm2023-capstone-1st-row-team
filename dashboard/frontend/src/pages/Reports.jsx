import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { apiGet } from '../hooks/useApi';

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [selected, setSelected] = useState(null);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiGet('/api/reports').then(setReports);
  }, []);

  const loadReport = async (filename) => {
    setLoading(true);
    setSelected(filename);
    try {
      const data = await apiGet(`/api/reports/${filename}`);
      setContent(data.content || '');
    } catch (e) {
      setContent('Error loading report.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2 className="page-title">Reports</h2>
      <p className="page-subtitle">Markdown reports from results/reports/</p>

      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ minWidth: 250 }}>
          <div className="card">
            <h3 style={{ fontSize: 14, marginBottom: 12 }}>Available Reports</h3>
            {reports.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No reports found.</p>
            ) : (
              reports.map(r => (
                <div
                  key={r.filename}
                  onClick={() => loadReport(r.filename)}
                  style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    cursor: 'pointer',
                    marginBottom: 4,
                    background: selected === r.filename ? 'var(--accent-cyan-dim)' : 'transparent',
                    color: selected === r.filename ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                    fontSize: 13,
                    transition: 'all 0.15s ease',
                  }}
                >
                  {r.filename}
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {(r.size_bytes / 1024).toFixed(1)} KB
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <div className="card" style={{ minHeight: 400 }}>
            {!selected ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', paddingTop: 60 }}>
                Select a report from the left panel to view
              </p>
            ) : loading ? (
              <p style={{ color: 'var(--text-secondary)' }}>Loading...</p>
            ) : (
              <div style={{ lineHeight: 1.7, fontSize: 14 }}>
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
