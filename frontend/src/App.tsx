import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Landing } from './pages/Landing';
import { Scan } from './pages/Scan';
import { Results } from './pages/Results';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-base-900 text-text-primary selection:bg-primary selection:text-white">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/scan" element={<Scan />} />
            <Route path="/scan/:id" element={<Results />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
