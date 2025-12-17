import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Customers from './pages/Customers'
import Metrage from './pages/Metrage'
import Quotes from './pages/Quotes'
import Login from './pages/Login'
import Sidebar from './components/Sidebar'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Vérifier le token au chargement
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
    setLoading(false)

    // Enregistrer le service worker pour PWA
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then(() => console.log('Service Worker registered'))
        .catch((err) => console.error('Service Worker registration failed:', err))
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-muted-foreground">Chargement...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />
  }

  return (
    <Router>
      <div className="flex h-screen bg-background">
        <Sidebar onLogout={() => {
          localStorage.removeItem('token')
          setIsAuthenticated(false)
        }} />
        <main className="flex-1 h-screen overflow-y-auto">
          <div className="container mx-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/metrage" element={<Metrage />} />
              <Route path="/quotes" element={<Quotes />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App 