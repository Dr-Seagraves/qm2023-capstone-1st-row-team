import React, { useState, useEffect } from 'react';
import { apiGet, apiPut, apiPost } from '../hooks/useApi';

export default function DataDictionary() {
  const [dictionary, setDictionary] = useState(null);
  const [search, setSearch] = useState('');
  const [filterDataset, setFilterDataset] = useState('all');
  const [scanning, setScanning] = useState(false);
  const [editingCell, setEditingCell] = useState(null);
  const [editValue, setEditValue] = useState('');

  useEffect(() => {
    apiGet('/api/dictionary').then(setDictionary);
  }, []);

  const rescan = async () => {
    setScanning(true);
    try {
      await apiPost('/api/dictionary/scan');
      const updated = await apiGet('/api/dictionary');
      setDictionary(updated);
    } catch (e) {
      console.error(e);
    }
    setScanning(false);
  };

  const saveDescription = async (dsKey, colName) => {
    if (!dictionary) return;
    const next = { ...dictionary };
    next.datasets[dsKey].columns[colName].description = editValue;
    setDictionary(next);
    setEditingCell(null);
    await apiPut('/api/dictionary', next);
  };

  const exportCsv = () => {
    if (!dictionary) return;
    let csv = 'Dataset,Column,Type,Description,Nullable,SampleValues,Include\n';
    for (const [dsKey, ds] of Object.entries(dictionary.datasets || {})) {
      for (const [col, info] of Object.entries(ds.columns || {})) {
        const samples = (info.sample_values || []).join('; ');
        csv += `"${dsKey}","${col}","${info.dtype}","${info.description || ''}","${info.nullable}","${samples}","${info.include}"\n`;
      }
    }
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data_dictionary.csv';
    a.click();
  };

  // Build flat rows for display
  const rows = [];
  if (dictionary?.datasets) {
    for (const [dsKey, ds] of Object.entries(dictionary.datasets)) {
      for (const [colName, info] of Object.entries(ds.columns || {})) {
        rows.push({ dsKey, colName, ...info, dataset_label: ds.filename || dsKey });
      }
    }
  }

  const datasets = dictionary?.datasets ? Object.keys(dictionary.datasets) : [];

  const filtered = rows.filter(r => {
    if (filterDataset !== 'all' && r.dsKey !== filterDataset) return false;
    if (search && !r.colName.toLowerCase().includes(search.toLowerCase()) &&
        !(r.description || '').toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div>
      <h2 className="page-title">Data Dictionary</h2>
      <p className="page-subtitle">Auto-generated column metadata from project CSV files</p>

      <div className="flex-between mb-24" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 12, flex: 1 }}>
          <input
            className="input"
            placeholder="Search columns..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ maxWidth: 300 }}
          />
          <select
            className="input"
            value={filterDataset}
            onChange={e => setFilterDataset(e.target.value)}
            style={{ maxWidth: 300 }}
          >
            <option value="all">All Datasets ({rows.length} columns)</option>
            {datasets.map(ds => (
              <option key={ds} value={ds}>{ds}</option>
            ))}
          </select>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-primary" onClick={rescan} disabled={scanning}>
            {scanning ? 'Scanning...' : 'Re-scan CSVs'}
          </button>
          <button className="btn btn-secondary" onClick={exportCsv}>
            Export CSV
          </button>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Column</th>
              <th>Type</th>
              <th>Non-Null</th>
              <th>Sample Values</th>
              <th>Description (click to edit)</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
                  {!dictionary ? 'Loading...' : 'No columns found. Click "Re-scan CSVs" to populate.'}
                </td>
              </tr>
            ) : (
              filtered.map((r, idx) => {
                const cellKey = `${r.dsKey}::${r.colName}`;
                return (
                  <tr key={cellKey}>
                    <td style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{r.dataset_label}</td>
                    <td className="mono">{r.colName}</td>
                    <td><span className="badge badge-other">{r.dtype}</span></td>
                    <td>{r.non_null_count ?? '—'}</td>
                    <td style={{ fontSize: 11, color: 'var(--text-secondary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {(r.sample_values || []).slice(0, 3).join(', ')}
                    </td>
                    <td>
                      {editingCell === cellKey ? (
                        <div style={{ display: 'flex', gap: 6 }}>
                          <input
                            className="input"
                            value={editValue}
                            onChange={e => setEditValue(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && saveDescription(r.dsKey, r.colName)}
                            autoFocus
                          />
                          <button className="btn btn-primary btn-sm" onClick={() => saveDescription(r.dsKey, r.colName)}>✓</button>
                          <button className="btn btn-secondary btn-sm" onClick={() => setEditingCell(null)}>✕</button>
                        </div>
                      ) : (
                        <span
                          style={{ cursor: 'pointer', color: r.description ? 'var(--text-primary)' : 'var(--text-muted)' }}
                          onClick={() => { setEditingCell(cellKey); setEditValue(r.description || ''); }}
                        >
                          {r.description || 'Click to add description...'}
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 12, color: 'var(--text-muted)', fontSize: 12 }}>
        Showing {filtered.length} of {rows.length} columns
        {dictionary?.generated && ` · Last scanned: ${new Date(dictionary.generated).toLocaleString()}`}
      </div>
    </div>
  );
}
