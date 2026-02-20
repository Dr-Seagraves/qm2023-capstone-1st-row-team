import React, { useState, useEffect, useCallback } from 'react';
import { apiGet } from '../hooks/useApi';

/**
 * Dark-themed, read-only Excel-style viewer for master_dataset.csv.
 * Supports pagination, fixed header, sticky row numbers.
 */
export default function MasterDataViewer() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage]       = useState(1);
  const [pageSize]            = useState(100);
  const [info, setInfo]       = useState(null);

  // ── load master info ────────────────────────────────────────
  useEffect(() => {
    apiGet('/api/data/master/info').then(setInfo).catch(() => {});
  }, []);

  // ── load page data ──────────────────────────────────────────
  const loadPage = useCallback((p) => {
    setLoading(true);
    apiGet(`/api/data/master?page=${p}&pageSize=${pageSize}`)
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [pageSize]);

  useEffect(() => { loadPage(page); }, [page, loadPage]);

  // ── refresh (can be called after a rebuild) ─────────────────
  const refresh = () => { loadPage(page); apiGet('/api/data/master/info').then(setInfo).catch(() => {}); };

  // ── loading state ───────────────────────────────────────────
  if (loading && !data) {
    return <div style={{ color: 'var(--text-secondary)', padding: 20 }}>Loading master dataset…</div>;
  }

  // ── empty state ─────────────────────────────────────────────
  if (!data || data.totalRows === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <p style={{ color: 'var(--text-muted)' }}>Master dataset is empty.</p>
        <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 8 }}>
          Include columns in the <strong>Column Configuration</strong> tab, then the dataset will rebuild automatically.
        </p>
        <button className="btn btn-secondary" onClick={refresh} style={{ marginTop: 16 }}>
          Refresh
        </button>
      </div>
    );
  }

  const totalPages = data.totalPages || 1;

  return (
    <div className="mv">
      {/* ── info bar ────────────────────────────────────────── */}
      <div className="mv-info">
        <span>{data.totalRows.toLocaleString()} rows × {data.totalColumns} columns</span>
        {info?.size_bytes != null && (
          <span style={{ color: 'var(--text-muted)' }}>
            ({(info.size_bytes / 1024 / 1024).toFixed(2)} MB)
          </span>
        )}
        <button className="btn btn-secondary btn-sm" onClick={refresh} style={{ marginLeft: 'auto' }}>
          ↻ Refresh
        </button>
      </div>

      {/* ── table ───────────────────────────────────────────── */}
      <div className="mv-wrap">
        <table className="mv-table">
          <thead>
            <tr>
              <th className="mv-rownum">#</th>
              {data.columns.map((col, i) => <th key={i}>{col}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, ri) => (
              <tr key={ri}>
                <td className="mv-rownum">{(page - 1) * pageSize + ri + 1}</td>
                {row.map((cell, ci) => (
                  <td key={ci} title={cell != null ? String(cell) : ''}>
                    {cell != null
                      ? String(cell)
                      : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── pagination ──────────────────────────────────────── */}
      <div className="mv-pagination">
        <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage(1)}>
          First
        </button>
        <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
          ← Prev
        </button>
        <span className="mono" style={{ fontSize: 12, minWidth: 100, textAlign: 'center' }}>
          Page {data.page} of {totalPages}
        </span>
        <button className="btn btn-secondary btn-sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
          Next →
        </button>
        <button className="btn btn-secondary btn-sm" disabled={page >= totalPages} onClick={() => setPage(totalPages)}>
          Last
        </button>
      </div>
    </div>
  );
}
