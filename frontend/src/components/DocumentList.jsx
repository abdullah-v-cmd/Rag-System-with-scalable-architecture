import { useState, useEffect } from 'react'
import axios from 'axios'

function DocumentList({ apiBaseUrl, onDelete }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/documents`)
      setDocuments(response.data)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return
    }

    setDeleting(documentId)
    try {
      await axios.delete(`${apiBaseUrl}/documents/${documentId}`)
      setDocuments(documents.filter(doc => doc.id !== documentId))
      if (onDelete) {
        onDelete()
      }
    } catch (err) {
      alert(`Error deleting document: ${err.response?.data?.detail || err.message}`)
    } finally {
      setDeleting(null)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'pending':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'pdf':
        return '📕'
      case 'txt':
        return '📄'
      case 'doc':
      case 'docx':
        return '📘'
      default:
        return '📄'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-500 rounded-xl p-6">
        <div className="flex items-start">
          <span className="text-2xl mr-3">❌</span>
          <div>
            <h3 className="text-lg font-semibold text-red-800 mb-1">Error</h3>
            <p className="text-red-600">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Document Library</h2>
          <p className="text-gray-600 mt-1">
            {documents.length} document{documents.length !== 1 ? 's' : ''} in your knowledge base
          </p>
        </div>
        <button
          onClick={fetchDocuments}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          <span className="text-6xl mb-4 block">📚</span>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No documents yet</h3>
          <p className="text-gray-600">Upload your first document to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-blue-500 hover:shadow-lg transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <span className="text-4xl">{getFileIcon(doc.file_type)}</span>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-800 truncate">
                      {doc.filename}
                    </h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className={`text-xs px-3 py-1 rounded-full font-semibold ${getStatusColor(doc.status)}`}>
                        {doc.status.toUpperCase()}
                      </span>
                      <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
                        {doc.file_type.toUpperCase()}
                      </span>
                      <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
                        {formatFileSize(doc.file_size)}
                      </span>
                      {doc.metadata?.chunk_count && (
                        <span className="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
                          {doc.metadata.chunk_count} chunks
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-4 mt-3 text-sm text-gray-600">
                      <span>📅 Uploaded: {formatDate(doc.upload_date)}</span>
                      {doc.processed_at && (
                        <span>✅ Processed: {formatDate(doc.processed_at)}</span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  disabled={deleting === doc.id}
                  className={`ml-4 px-4 py-2 rounded-lg font-semibold transition-colors ${
                    deleting === doc.id
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-red-500 text-white hover:bg-red-600'
                  }`}
                >
                  {deleting === doc.id ? (
                    <span className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Deleting...</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <span>🗑️</span>
                      <span>Delete</span>
                    </span>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DocumentList
