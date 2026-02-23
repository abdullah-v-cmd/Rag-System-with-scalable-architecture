import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'

function DocumentUpload({ apiBaseUrl, onUploadSuccess }) {
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [taskId, setTaskId] = useState(null)
  const [taskStatus, setTaskStatus] = useState(null)

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setUploading(true)
    setUploadStatus(null)
    setTaskId(null)
    setTaskStatus(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${apiBaseUrl}/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadStatus({
        type: 'success',
        message: `✅ File uploaded successfully: ${response.data.filename}`,
      })
      setTaskId(response.data.task_id)
      
      // Start polling for task status
      pollTaskStatus(response.data.task_id)
      
      if (onUploadSuccess) {
        onUploadSuccess()
      }
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: `❌ Upload failed: ${error.response?.data?.detail || error.message}`,
      })
    } finally {
      setUploading(false)
    }
  }, [apiBaseUrl, onUploadSuccess])

  const pollTaskStatus = async (taskId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${apiBaseUrl}/tasks/${taskId}`)
        setTaskStatus(response.data)

        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(interval)
        }
      } catch (error) {
        console.error('Error polling task status:', error)
        clearInterval(interval)
      }
    }, 2000)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Upload Documents</h2>
        <p className="text-gray-600">
          Upload PDF, TXT, DOC, or DOCX files to add them to the knowledge base
        </p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-4 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-full shadow-lg">
              <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
          </div>
          
          {uploading ? (
            <div className="space-y-2">
              <p className="text-xl font-semibold text-gray-700">Uploading...</p>
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            </div>
          ) : isDragActive ? (
            <p className="text-xl font-semibold text-blue-600">Drop the file here...</p>
          ) : (
            <div>
              <p className="text-xl font-semibold text-gray-700 mb-2">
                Drag & drop a file here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supported formats: PDF, TXT, DOC, DOCX (Max 50MB)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div
          className={`p-6 rounded-xl shadow-lg ${
            uploadStatus.type === 'success'
              ? 'bg-green-50 border-2 border-green-500'
              : 'bg-red-50 border-2 border-red-500'
          }`}
        >
          <p className="text-lg font-semibold">{uploadStatus.message}</p>
        </div>
      )}

      {/* Task Status */}
      {taskStatus && (
        <div className="bg-blue-50 border-2 border-blue-500 rounded-xl p-6 shadow-lg">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Processing Status</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-700">Task ID:</span>
              <span className="text-sm font-mono bg-white px-3 py-1 rounded">{taskId}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-700">Status:</span>
              <span className={`px-4 py-1 rounded-full font-semibold ${
                taskStatus.status === 'completed' ? 'bg-green-500 text-white' :
                taskStatus.status === 'failed' ? 'bg-red-500 text-white' :
                taskStatus.status === 'processing' ? 'bg-yellow-500 text-white' :
                'bg-gray-500 text-white'
              }`}>
                {taskStatus.status.toUpperCase()}
              </span>
            </div>

            {taskStatus.status === 'processing' && taskStatus.result && (
              <div className="mt-2">
                <p className="text-sm text-gray-600">{taskStatus.result.status}</p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                </div>
              </div>
            )}

            {taskStatus.status === 'completed' && taskStatus.result && (
              <div className="bg-white rounded-lg p-4 mt-2">
                <p className="text-green-600 font-semibold">✅ Document processed successfully!</p>
                <p className="text-sm text-gray-600 mt-2">
                  Generated {taskStatus.result.chunk_count} text chunks for vector search
                </p>
              </div>
            )}

            {taskStatus.status === 'failed' && (
              <div className="bg-white rounded-lg p-4 mt-2">
                <p className="text-red-600 font-semibold">❌ Processing failed</p>
                {taskStatus.error && (
                  <p className="text-sm text-gray-600 mt-2">{taskStatus.error}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold text-gray-800 mb-4">📋 How it works</h3>
        <ol className="space-y-2 text-gray-700">
          <li className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">1</span>
            <span>Upload your document (PDF, TXT, DOC, DOCX)</span>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">2</span>
            <span>Document is processed in the background using Celery workers</span>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">3</span>
            <span>Text is extracted and split into overlapping chunks</span>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">4</span>
            <span>Embeddings are generated using OpenAI and cached in Redis</span>
          </li>
          <li className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">5</span>
            <span>Vectors are stored in PostgreSQL with pgvector for similarity search</span>
          </li>
        </ol>
      </div>
    </div>
  )
}

export default DocumentUpload
