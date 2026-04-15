/**
 * Main App Component
 * Handles routing and layout
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/common/Navbar';
import { Overview } from './pages/Overview';
import { Fleet } from './pages/Fleet';
import { UPSDetail } from './pages/UPSDetail';
import { Analytics } from './pages/Analytics';
import { Alerts } from './pages/Alerts';
import { Simulation } from './pages/Simulation';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/fleet" element={<Fleet />} />
          <Route path="/ups/:id" element={<UPSDetail />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/simulation" element={<Simulation />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
