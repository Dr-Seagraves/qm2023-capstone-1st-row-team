import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';

const mainNav = [
  { path: '/overview', label: 'Overview', icon: '◈' },
  { path: '/charts', label: 'Charts', icon: '◔' },
  { path: '/reports', label: 'Reports', icon: '▤' },
];

const setupNav = [
  { path: '/pipeline', label: 'Pipeline', icon: '▶' },
  { path: '/dictionary', label: 'Data Dictionary', icon: '▦' },
  { path: '/logs', label: 'Logs', icon: '▥' },
  { path: '/settings', label: 'Settings', icon: '⚙' },
];

const pageNames = {
  '/overview': 'Overview',
  '/charts': 'Chart Builder',
  '/reports': 'Reports',
  '/pipeline': 'Pipeline Runner',
  '/dictionary': 'Data Dictionary',
  '/logs': 'Activity Logs',
  '/settings': 'Settings',
};

export default function Layout() {
  const location = useLocation();
  const pageTitle = pageNames[location.pathname] || 'Dashboard';
  const isSetupPage = setupNav.some(n => n.path === location.pathname);
  const [setupOpen, setSetupOpen] = useState(isSetupPage);

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>HURRICANE FX</h2>
          <p>Capstone Dashboard</p>
        </div>
        <nav className="sidebar-nav">
          {mainNav.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link${isActive ? ' active' : ''}`
              }
            >
              <span className="icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}

          {/* Setup folder */}
          <div
            className="sidebar-section"
            style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingRight: 14 }}
            onClick={() => setSetupOpen(!setupOpen)}
          >
            <span>Setup</span>
            <span style={{ fontSize: 10, transition: 'transform 0.2s', transform: setupOpen ? 'rotate(90deg)' : 'rotate(0deg)' }}>
              ▸
            </span>
          </div>
          {setupOpen && setupNav.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link${isActive ? ' active' : ''}`
              }
              style={{ paddingLeft: 24 }}
            >
              <span className="icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div style={{ flex: 1 }} />
        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)' }}>
          <NavLink to="/" className="sidebar-link" style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            ← Back to Splash
          </NavLink>
        </div>
      </aside>
      <div className="main-area">
        <header className="topbar">
          <h1>{pageTitle}</h1>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
