import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Splash from './pages/Splash';
import Overview from './pages/Overview';
import Charts from './pages/Charts';
import Reports from './pages/Reports';
import Pipeline from './pages/Pipeline';
import DataDictionary from './pages/DataDictionary';
import Logs from './pages/Logs';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route element={<Layout />}>
          <Route path="/overview" element={<Overview />} />
          <Route path="/charts" element={<Charts />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/dictionary" element={<DataDictionary />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
