import React, { useState, useEffect } from 'react';
import { apiGet, apiPut } from '../hooks/useApi';
import ColumnConfig from '../components/ColumnConfig';
import MasterDataViewer from '../components/MasterDataViewer';

const TABS = [
  { id: 'sources',  label: 'Data Sources' },
  { id: 'columns',  label: 'Column Configuration' },
  { id: 'master',   label: 'Master Dataset' },
];

export default function Settings() {
  const [activeTab, setActiveTab] = useState('columns');
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div>
      <h2 className="page-title">Project Settings</h2>
      <p className="page-subtitle">Manage data sources, column configuration, and the master dataset</p>

      {toast && (
        <div className="toast-container">
          <div className={`toast toast-${toast.type}`}>{toast.msg}</div>
        </div>
      )}

      {/* Tabs */}
      <div className="settings-tabs">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`settings-tab${activeTab === t.id ? ' active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === 'sources'  && <DataSourcesTab onToast={showToast} />}
      {activeTab === 'columns'  && <ColumnConfig onToast={showToast} />}
      {activeTab === 'master'   && <MasterDataViewer />}
    </div>
  );
}


/* ================================================================
   Data Sources Tab  (extracted from the original Settings page)
   ================================================================ */

function DataSourcesTab({ onToast }) {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editIdx, setEditIdx] = useState(null);
  const [editUrl, setEditUrl] = useState('');
  const [newUrl, setNewUrl]   = useState('');

  useEffect(() => {
    apiGet('/api/settings/sources')
      .then(s => { setSources(s); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const saveSources = async (list) => {
    await apiPut('/api/settings/sources', { urls: list.map(s => s.url) });
    const updated = await apiGet('/api/settings/sources');
    setSources(updated);
    onToast?.('Data sources saved');
  };

  const handleDelete   = (i)  => saveSources(sources.filter((_, j) => j !== i));
  const handleEdit     = (i)  => { setEditIdx(i); setEditUrl(sources[i].url); };
  const handleEditSave = ()   => {
    const next = [...sources];
    next[editIdx] = { ...next[editIdx], url: editUrl };
    setEditIdx(null);
    saveSources(next);
  };
  const handleAdd = () => {
    if (!newUrl.trim()) return;
    saveSources([...sources, { url: newUrl.trim(), label: 'New Source', type: 'other', enabled: true }]);
    setNewUrl('');
  };

  const handleToggle = async (idx) => {
    const src = sources[idx];
    const newEnabled = !src.enabled;
    // Optimistic UI
    setSources(prev => prev.map((s, i) => i === idx ? { ...s, enabled: newEnabled } : s));
    try {
      await apiPut('/api/settings/sources/toggle', { url: src.url, enabled: newEnabled });
      onToast?.(newEnabled ? `Enabled: ${src.label}` : `Disabled: ${src.label}`, newEnabled ? 'success' : 'info');
    } catch (e) {
      // Revert on error
      setSources(prev => prev.map((s, i) => i === idx ? { ...s, enabled: !newEnabled } : s));
      onToast?.('Toggle failed: ' + e.message, 'error');
    }
  };

  if (loading) return <div style={{ color: 'var(--text-secondary)' }}>Loading…</div>;

  return (
    <div className="card">
      <div className="card-header">
        <h3>Data Sources ({sources.length})</h3>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          {sources.filter(s => s.enabled).length} enabled / {sources.filter(s => !s.enabled).length} disabled
        </span>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: 40 }}>#</th>
            <th>Label</th>
            <th>URL</th>
            <th>Type</th>
            <th style={{ width: 220 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sources.map((src, idx) => (
            <tr key={idx} style={{ opacity: src.enabled ? 1 : 0.45 }}>
              <td style={{ color: 'var(--text-muted)' }}>{idx + 1}</td>
              <td>{src.label}</td>
              <td>
                {editIdx === idx ? (
                  <input className="input" value={editUrl}
                    onChange={e => setEditUrl(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleEditSave()} />
                ) : (
                  <span className="mono" style={{ wordBreak: 'break-all', fontSize: 11 }}>
                    {src.url.length > 80 ? src.url.slice(0, 80) + '…' : src.url}
                  </span>
                )}
              </td>
              <td><span className={`badge badge-${src.type}`}>{src.type}</span></td>
              <td>
                {editIdx === idx ? (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button className="btn btn-primary btn-sm" onClick={handleEditSave}>Save</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => setEditIdx(null)}>Cancel</button>
                  </div>
                ) : (
                  <div style={{ display: 'flex', gap: 6 }}>
                    <button
                      className="btn btn-sm"
                      style={src.enabled
                        ? { background: 'rgba(34,197,94,0.15)', color: 'var(--accent-green)', border: '1px solid rgba(34,197,94,0.3)' }
                        : { background: 'rgba(255,255,255,0.04)', color: 'var(--text-muted)', border: '1px solid rgba(255,255,255,0.1)' }}
                      onClick={() => handleToggle(idx)}
                    >
                      {src.enabled ? 'Enabled' : 'Disabled'}
                    </button>
                    <button className="btn btn-secondary btn-sm" onClick={() => handleEdit(idx)}>Edit</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(idx)}>Del</button>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
        <input className="input" placeholder="Add a new data source URL…"
          value={newUrl} onChange={e => setNewUrl(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAdd()} style={{ flex: 1 }} />
        <button className="btn btn-primary" onClick={handleAdd}>+ Add Source</button>
      </div>
    </div>
  );
}
