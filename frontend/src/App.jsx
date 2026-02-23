import { useState, useEffect } from 'react'
import axios from 'axios'
import DocumentUpload from './components/DocumentUpload'
import QueryInterface from './components/QueryInterface'
import DocumentList from './components/DocumentList'
import Stats from './components/Stats'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('query')
  const [stats, setStats] = useState(null)
  const [health, setHealth] = useState(null)

  useEffect(() => {
    fetchStats()
    fetchHealth()
    const interval = setInterval(() => {
      fetchStats()
      fetchHealth()
    }, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`)
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      setHealth(response.data)
    } catch (error) {
      console.error('Error fetching health:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-blue-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  RAG Intelligence Platform
                </h1>
                <p className="text-sm text-gray-600 mt-1">Document Intelligence & Question Answering System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {health && (
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${health.status === 'healthy' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                  <span className="text-sm font-medium text-gray-700">
                    {health.status === 'healthy' ? 'System Healthy' : 'System Issues'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && <Stats stats={stats} />}

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-2xl shadow-xl p-2">
          <nav className="flex space-x-2">
            {[
              { id: 'query', label: 'Query Documents', icon: '🔍' },
              { id: 'upload', label: 'Upload Documents', icon: '📤' },
              { id: 'documents', label: 'Document Library', icon: '📚' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 px-6 py-4 rounded-xl font-semibold transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg transform scale-105'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span className="text-2xl">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {activeTab === 'query' && <QueryInterface apiBaseUrl={API_BASE_URL} />}
          {activeTab === 'upload' && <DocumentUpload apiBaseUrl={API_BASE_URL} onUploadSuccess={fetchStats} />}
          {activeTab === 'documents' && <DocumentList apiBaseUrl={API_BASE_URL} onDelete={fetchStats} />}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600">
            🚀 Powered by OpenAI, FastAPI, PostgreSQL with pgvector, Redis & Celery
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
