import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { apiGet, apiPut, apiPost } from '../hooks/useApi';

/* ================================================================
   Google-search-like query parser
   ================================================================
   Supports:
     "exact phrase"   — must contain phrase
     -word            — must NOT contain word
     word1 OR word2   — either word
     plain words      — AND (all must match)
   ================================================================ */

function parseSearchQuery(query) {
  if (!query || !query.trim()) return null;
  const tokens = [];
  let remaining = query;

  // 1. Extract "quoted phrases"
  remaining = remaining.replace(/"([^"]+)"/g, (_, phrase) => {
    tokens.push({ type: 'exact', value: phrase.toLowerCase() });
    return ' ';
  });

  // 2. Tokenise remaining words, handling OR
  const words = remaining.trim().split(/\s+/).filter(Boolean);
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    if (w === 'OR') continue;                       // consumed below

    if (i + 2 <= words.length && words[i + 1] === 'OR') {
      // Collect OR chain: a OR b OR c ...
      const orVals = [w.replace(/^-/, '').toLowerCase()];
      let j = i + 2;
      while (j < words.length) {
        orVals.push(words[j].replace(/^-/, '').toLowerCase());
        if (j + 1 < words.length && words[j + 1] === 'OR') { j += 2; }
        else { j++; break; }
      }
      tokens.push({ type: 'or', values: orVals });
      i = j - 1;
    } else if (w.startsWith('-') && w.length > 1) {
      tokens.push({ type: 'exclude', value: w.substring(1).toLowerCase() });
    } else {
      tokens.push({ type: 'include', value: w.toLowerCase() });
    }
  }
  return tokens.length ? tokens : null;
}

function matchesTokens(text, tokens) {
  if (!tokens) return true;
  const lower = text.toLowerCase();
  return tokens.every(t => {
    if (t.type === 'exact')   return lower.includes(t.value);
    if (t.type === 'include') return lower.includes(t.value);
    if (t.type === 'exclude') return !lower.includes(t.value);
    if (t.type === 'or')      return t.values.some(v => lower.includes(v));
    return true;
  });
}

/* ================================================================
   ColumnConfig Component
   ================================================================ */

export default function ColumnConfig({ onToast }) {
  // ── state ────────────────────────────────────────────────────
  const [rawData, setRawData]             = useState(null);
  const [loading, setLoading]             = useState(true);
  const [scanning, setScanning]           = useState(false);

  const [selectedIds, setSelectedIds]     = useState(new Set());
  const [lastClickedId, setLastClickedId] = useState(null);

  const [sortMode, setSortMode]           = useState('default');
  const [filterStatus, setFilterStatus]   = useState('all');
  const [filterType, setFilterType]       = useState('all');
  const [filterSearch, setFilterSearch]   = useState('');
  const [masterSearch, setMasterSearch]   = useState('');

  const [collapsedGroups, setCollapsedGroups] = useState(new Set());
  const [renaming, setRenaming]           = useState(null);
  const [renameValue, setRenameValue]     = useState('');
  const [rebuilding, setRebuilding]       = useState(false);
  const [dirty, setDirty]                 = useState(false);

  const rebuildTimer = useRef(null);

  // ── data loading ─────────────────────────────────────────────
  const loadColumns = useCallback(async () => {
    try {
      const data = await apiGet('/api/data/columns');
      setRawData(data);
    } catch (e) {
      onToast?.('Failed to load columns: ' + e.message, 'error');
    }
    setLoading(false);
  }, [onToast]);

  useEffect(() => { loadColumns(); }, [loadColumns]);

  // ── flatten datasets → column list ───────────────────────────
  const flatColumns = useMemo(() => {
    if (!rawData?.datasets) return [];
    const list = [];
    let idx = 0;
    for (const [dsKey, dsInfo] of Object.entries(rawData.datasets)) {
      const filename = dsInfo.filename || dsKey.split('/').pop();
      for (const [colName, ci] of Object.entries(dsInfo.columns || {})) {
        list.push({
          id:              `${dsKey}::${colName}`,
          dataset:         dsKey,
          datasetFilename: filename,
          column:          colName,
          displayName:     ci.rename || colName,
          dtype:           ci.dtype  || 'unknown',
          include:         ci.include ?? false,
          rowCount:        ci.row_count  ?? 0,
          totalRows:       ci.total_rows ?? 0,
          rename:          ci.rename || null,
          originalIndex:   idx++,
        });
      }
    }
    return list;
  }, [rawData]);

  // ── unique types ─────────────────────────────────────────────
  const allTypes = useMemo(
    () => [...new Set(flatColumns.map(c => c.dtype))].sort(),
    [flatColumns],
  );

  // ── filter pipeline ──────────────────────────────────────────
  const filteredColumns = useMemo(() => {
    const tokens = parseSearchQuery(filterSearch);
    return flatColumns.filter(col => {
      if (filterStatus === 'included' && !col.include) return false;
      if (filterStatus === 'excluded' && col.include)  return false;
      if (filterType !== 'all' && col.dtype !== filterType) return false;
      if (tokens) {
        const haystack = `${col.column} ${col.displayName} ${col.dtype} ${col.datasetFilename}`;
        if (!matchesTokens(haystack, tokens)) return false;
      }
      return true;
    });
  }, [flatColumns, filterStatus, filterType, filterSearch]);

  // ── master search + sort ─────────────────────────────────────
  const displayedColumns = useMemo(() => {
    const masterTokens = parseSearchQuery(masterSearch);
    let result = filteredColumns;
    if (masterTokens) {
      result = result.filter(col => {
        const haystack = `${col.column} ${col.displayName} ${col.dtype} ${col.datasetFilename}`;
        return matchesTokens(haystack, masterTokens);
      });
    }
    const sorted = [...result];
    switch (sortMode) {
      case 'az':     sorted.sort((a, b) => a.displayName.localeCompare(b.displayName)); break;
      case 'za':     sorted.sort((a, b) => b.displayName.localeCompare(a.displayName)); break;
      case 'type':   sorted.sort((a, b) => a.dtype.localeCompare(b.dtype) || a.displayName.localeCompare(b.displayName)); break;
      case 'status': sorted.sort((a, b) => (b.include ? 1 : 0) - (a.include ? 1 : 0) || a.displayName.localeCompare(b.displayName)); break;
      default: break;
    }
    return sorted;
  }, [filteredColumns, masterSearch, sortMode]);

  // ── group by dataset ─────────────────────────────────────────
  const groupedColumns = useMemo(() => {
    const groups = new Map();
    for (const col of displayedColumns) {
      if (!groups.has(col.dataset))
        groups.set(col.dataset, { filename: col.datasetFilename, columns: [] });
      groups.get(col.dataset).columns.push(col);
    }
    return groups;
  }, [displayedColumns]);

  // ── selection handlers ───────────────────────────────────────
  const handleRowClick = useCallback((colId, e) => {
    const isMac = /mac/i.test(navigator.platform || navigator.userAgent);
    const isCtrl  = isMac ? e.metaKey : e.ctrlKey;
    const isShift = e.shiftKey;

    setSelectedIds(prev => {
      const next = new Set(prev);
      if (isShift && lastClickedId) {
        const ids = displayedColumns.map(c => c.id);
        const a = ids.indexOf(lastClickedId);
        const b = ids.indexOf(colId);
        if (a !== -1 && b !== -1) {
          const [lo, hi] = a < b ? [a, b] : [b, a];
          for (let i = lo; i <= hi; i++) next.add(ids[i]);
        }
      } else if (isCtrl) {
        if (next.has(colId)) next.delete(colId); else next.add(colId);
      } else {
        next.clear();
        next.add(colId);
      }
      return next;
    });
    if (!e.shiftKey) setLastClickedId(colId);
  }, [lastClickedId, displayedColumns]);

  const handleGroupSelectAll = useCallback((columns) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      const allIn = columns.every(c => next.has(c.id));
      columns.forEach(c => allIn ? next.delete(c.id) : next.add(c.id));
      return next;
    });
  }, []);

  // ── include / exclude ────────────────────────────────────────
  const updateInclusion = async (updates) => {
    // optimistic UI
    setRawData(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      for (const { dataset, column, include } of updates) {
        if (next.datasets?.[dataset]?.columns?.[column])
          next.datasets[dataset].columns[column].include = include;
      }
      return next;
    });
    try {
      await apiPut('/api/data/columns', { updates });
      setDirty(true);
      scheduleRebuild();
    } catch (e) {
      onToast?.('Save failed: ' + e.message, 'error');
      loadColumns();
    }
  };

  const toggleInclude = (col) =>
    updateInclusion([{ dataset: col.dataset, column: col.column, include: !col.include }]);

  const bulkInclude = (include) => {
    const updates = flatColumns
      .filter(c => selectedIds.has(c.id))
      .map(c => ({ dataset: c.dataset, column: c.column, include }));
    if (updates.length) updateInclusion(updates);
  };

  // ── auto-rebuild (debounced) ─────────────────────────────────
  const scheduleRebuild = () => {
    if (rebuildTimer.current) clearTimeout(rebuildTimer.current);
    rebuildTimer.current = setTimeout(doRebuild, 2000);
  };

  const doRebuild = async () => {
    setRebuilding(true);
    try {
      const r = await apiPost('/api/data/columns/rebuild');
      setDirty(false);
      onToast?.(`Master dataset rebuilt: ${r.rows} rows × ${r.columns} cols`, 'success');
    } catch (e) {
      onToast?.('Rebuild failed: ' + e.message, 'error');
    }
    setRebuilding(false);
  };

  // ── rename ───────────────────────────────────────────────────
  const startRename = (col) => { setRenaming(col.id); setRenameValue(col.displayName); };

  const saveRename = async (col) => {
    const newName = renameValue.trim();
    setRenaming(null);
    if (!newName || newName === col.column) {
      if (col.rename) {
        await apiPut('/api/data/columns/rename', { dataset: col.dataset, column: col.column, newName: '' });
        loadColumns();
      }
      return;
    }
    try {
      await apiPut('/api/data/columns/rename', { dataset: col.dataset, column: col.column, newName });
      loadColumns();
      onToast?.(`Renamed "${col.column}" → "${newName}"`, 'success');
    } catch (e) { onToast?.('Rename failed: ' + e.message, 'error'); }
  };

  // ── delete ───────────────────────────────────────────────────
  const deleteSelected = async () => {
    const items = flatColumns
      .filter(c => selectedIds.has(c.id))
      .map(c => ({ dataset: c.dataset, column: c.column }));
    if (!items.length) return;
    if (!window.confirm(`Delete ${items.length} column(s)? Re-scan to restore them.`)) return;
    try {
      await apiPost('/api/data/columns/delete', { items });
      setSelectedIds(new Set());
      loadColumns();
      scheduleRebuild();
      onToast?.(`Deleted ${items.length} column(s)`, 'success');
    } catch (e) { onToast?.('Delete failed: ' + e.message, 'error'); }
  };

  // ── scan / reset ─────────────────────────────────────────────
  const doScan = async () => {
    setScanning(true);
    try {
      const r = await apiPost('/api/data/columns/scan');
      await loadColumns();
      onToast?.(`Scanned ${r.datasets} datasets, ${r.columns} columns`, 'success');
    } catch (e) { onToast?.('Scan failed: ' + e.message, 'error'); }
    setScanning(false);
  };

  const doReset = async () => {
    if (!window.confirm('Reset all columns to excluded? Master dataset will be emptied.')) return;
    try {
      await apiPost('/api/data/columns/reset');
      await loadColumns();
      scheduleRebuild();
      onToast?.('All columns reset to excluded', 'success');
    } catch (e) { onToast?.('Reset failed: ' + e.message, 'error'); }
  };

  // ── filter reset ─────────────────────────────────────────────
  const resetFilters = () => {
    setFilterStatus('all');
    setFilterType('all');
    setFilterSearch('');
    setMasterSearch('');
    setSortMode('default');
  };

  // ── collapse helpers ─────────────────────────────────────────
  const toggleCollapse = (key) => setCollapsedGroups(prev => {
    const n = new Set(prev);
    n.has(key) ? n.delete(key) : n.add(key);
    return n;
  });
  const expandAll   = () => setCollapsedGroups(new Set());
  const collapseAll = () => setCollapsedGroups(new Set(groupedColumns.keys()));

  // ── cleanup timer on unmount ─────────────────────────────────
  useEffect(() => () => { if (rebuildTimer.current) clearTimeout(rebuildTimer.current); }, []);

  // ── renders ──────────────────────────────────────────────────
  if (loading) return <div style={{ color: 'var(--text-secondary)', padding: 20 }}>Loading column data…</div>;

  if (!rawData || flatColumns.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <p style={{ color: 'var(--text-muted)', marginBottom: 16 }}>
          No column configuration found. Scan your datasets to get started.
        </p>
        <button className="btn btn-primary" onClick={doScan} disabled={scanning}>
          {scanning ? 'Scanning…' : 'Scan Datasets'}
        </button>
      </div>
    );
  }

  const selectedCount  = selectedIds.size;
  const totalIncluded  = flatColumns.filter(c => c.include).length;

  return (
    <div className="col-config">

      {/* ── master search bar ── */}
      <div className="cc-row">
        <input
          className="input" style={{ flex: 1 }}
          placeholder='Search visible columns… ("exact", -exclude, OR)'
          value={masterSearch}
          onChange={e => setMasterSearch(e.target.value)}
        />
        <select className="input" value={sortMode} onChange={e => setSortMode(e.target.value)} style={{ width: 170 }}>
          <option value="default">Sort: Default</option>
          <option value="az">Sort: A → Z</option>
          <option value="za">Sort: Z → A</option>
          <option value="type">Sort: By Type</option>
          <option value="status">Sort: Included first</option>
        </select>
        <button className="btn btn-secondary btn-sm" onClick={resetFilters}>Reset Filters</button>
      </div>

      {/* ── filter bar ── */}
      <div className="cc-row">
        <select className="input" value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={{ width: 142 }}>
          <option value="all">All Status</option>
          <option value="included">Included</option>
          <option value="excluded">Excluded</option>
        </select>
        <select className="input" value={filterType} onChange={e => setFilterType(e.target.value)} style={{ width: 130 }}>
          <option value="all">All Types</option>
          {allTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <input
          className="input" style={{ flex: 1 }}
          placeholder='Filter by keyword… ("exact", -exclude, term1 OR term2)'
          value={filterSearch}
          onChange={e => setFilterSearch(e.target.value)}
        />
        <span className="cc-count">
          {displayedColumns.length} / {flatColumns.length} cols
          {totalIncluded > 0 && <> · <span className="cc-inc-count">{totalIncluded} included</span></>}
        </span>
      </div>

      {/* ── selection actions ── */}
      {selectedCount > 0 && (
        <div className="cc-selection-bar">
          <span className="cc-sel-label">{selectedCount} selected</span>
          <button className="btn btn-sm cc-btn-include" onClick={() => bulkInclude(true)}>Include</button>
          <button className="btn btn-secondary btn-sm" onClick={() => bulkInclude(false)}>Exclude</button>
          <button className="btn btn-danger btn-sm" onClick={deleteSelected}>Delete</button>
          <button className="btn btn-secondary btn-sm" onClick={() => setSelectedIds(new Set())}>Clear</button>
        </div>
      )}

      {/* ── rebuild indicator ── */}
      {(dirty || rebuilding) && (
        <div className="cc-rebuild-bar">
          {rebuilding
            ? <span>⟳ Rebuilding master dataset…</span>
            : <span>Changes pending — auto-rebuild in ~2 s…</span>}
          {!rebuilding && (
            <button className="btn btn-primary btn-sm" onClick={doRebuild}>Rebuild Now</button>
          )}
        </div>
      )}

      {/* ── dataset groups ── */}
      <div className="cc-groups">
        <div className="cc-row" style={{ gap: 8, marginBottom: 4 }}>
          <button className="btn btn-secondary btn-sm" onClick={expandAll}>Expand All</button>
          <button className="btn btn-secondary btn-sm" onClick={collapseAll}>Collapse All</button>
        </div>

        {[...groupedColumns.entries()].map(([dsKey, group]) => {
          const collapsed     = collapsedGroups.has(dsKey);
          const groupIncluded = group.columns.filter(c => c.include).length;
          const allSel        = group.columns.length > 0 && group.columns.every(c => selectedIds.has(c.id));
          const someSel       = group.columns.some(c => selectedIds.has(c.id));

          return (
            <div key={dsKey} className="cc-dataset">
              {/* header */}
              <div className="cc-ds-header" onClick={() => toggleCollapse(dsKey)}>
                <span className="cc-arrow">{collapsed ? '▸' : '▾'}</span>
                <input
                  type="checkbox"
                  checked={allSel}
                  ref={el => { if (el) el.indeterminate = someSel && !allSel; }}
                  onChange={() => handleGroupSelectAll(group.columns)}
                  onClick={e => e.stopPropagation()}
                  className="cc-group-cb"
                />
                <span className="cc-ds-name">{group.filename}</span>
                <span className="cc-ds-meta">
                  {group.columns.length} columns · {groupIncluded} included
                </span>
              </div>

              {/* column table */}
              {!collapsed && (
                <table className="cc-table">
                  <thead>
                    <tr>
                      <th style={{ width: 30 }}></th>
                      <th style={{ width: 42 }}>Inc.</th>
                      <th>Column Name</th>
                      <th style={{ width: 78 }}>Type</th>
                      <th style={{ width: 68 }}>Rows</th>
                      <th style={{ width: 94 }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.columns.map(col => {
                      const isSel = selectedIds.has(col.id);
                      const isRen = renaming === col.id;

                      return (
                        <tr
                          key={col.id}
                          className={`cc-row-item${isSel ? ' selected' : ''}${col.include ? ' included' : ''}`}
                          onClick={e => handleRowClick(col.id, e)}
                        >
                          <td>
                            <input type="checkbox" checked={isSel} readOnly className="cc-cb" />
                          </td>
                          <td>
                            <label className="toggle" onClick={e => e.stopPropagation()}>
                              <input type="checkbox" checked={col.include} onChange={() => toggleInclude(col)} />
                              <span className="toggle-slider" />
                            </label>
                          </td>
                          <td className="cc-name-cell">
                            {isRen ? (
                              <input
                                className="input cc-rename-input"
                                value={renameValue}
                                onChange={e => setRenameValue(e.target.value)}
                                onKeyDown={e => { if (e.key === 'Enter') saveRename(col); if (e.key === 'Escape') setRenaming(null); }}
                                onBlur={() => saveRename(col)}
                                autoFocus
                                onClick={e => e.stopPropagation()}
                              />
                            ) : (
                              <span className="mono" title={col.column}>
                                {col.displayName}
                                {col.rename && <span className="cc-orig"> ({col.column})</span>}
                              </span>
                            )}
                          </td>
                          <td>
                            <span className={`badge badge-${
                              col.dtype === 'float' || col.dtype === 'integer' ? 'noaa'
                              : col.dtype === 'date' ? 'zillow' : 'other'
                            }`}>
                              {col.dtype}
                            </span>
                          </td>
                          <td className="mono" style={{ fontSize: 11 }}>
                            {(col.totalRows || col.rowCount).toLocaleString()}
                          </td>
                          <td>
                            <div className="cc-actions" onClick={e => e.stopPropagation()}>
                              <button className="btn btn-secondary btn-sm" onClick={() => startRename(col)} title="Rename column">✎</button>
                              <button
                                className="btn btn-danger btn-sm"
                                title="Delete column from config"
                                onClick={() => {
                                  if (!window.confirm(`Delete "${col.column}" from ${col.datasetFilename}?`)) return;
                                  apiPost('/api/data/columns/delete', { items: [{ dataset: col.dataset, column: col.column }] })
                                    .then(() => { loadColumns(); scheduleRebuild(); onToast?.('Column deleted', 'success'); })
                                    .catch(e => onToast?.('Delete failed: ' + e.message, 'error'));
                                }}
                              >✕</button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          );
        })}
      </div>

      {/* ── bottom actions ── */}
      <div className="cc-bottom-actions">
        <button className="btn btn-secondary" onClick={doScan} disabled={scanning}>
          {scanning ? 'Scanning…' : 'Scan Datasets'}
        </button>
        <button className="btn btn-primary" onClick={doRebuild} disabled={rebuilding}>
          {rebuilding ? 'Rebuilding…' : 'Rebuild Master Dataset'}
        </button>
        <button className="btn btn-danger" onClick={doReset}>Reset All</button>
      </div>
    </div>
  );
}
