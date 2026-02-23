import { useState } from 'react'
import axios from 'axios'

function QueryInterface({ apiBaseUrl }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)
  const [streamMode, setStreamMode] = useState(false)
  const [streamingText, setStreamingText] = useState('')

  const handleQuery = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)
    setStreamingText('')

    if (streamMode) {
      await handleStreamingQuery()
    } else {
      await handleNormalQuery()
    }
  }

  const handleNormalQuery = async () => {
    try {
      const res = await axios.post(`${apiBaseUrl}/query`, {
        query: query,
        top_k: 5,
        similarity_threshold: 0.7,
        stream: false
      })
      setResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStreamingQuery = async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          top_k: 5,
          similarity_threshold: 0.7,
          stream: true
        })
      })

      if (!res.ok) {
        throw new Error('Stream request failed')
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let text = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        text += chunk
        setStreamingText(text)
      }

      setResponse({
        query: query,
        response: text,
        relevant_chunks: [],
        execution_time: 0
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Query Documents</h2>
        <p className="text-gray-600">
          Ask questions and get AI-powered answers from your document knowledge base
        </p>
      </div>

      {/* Query Form */}
      <form onSubmit={handleQuery} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to know from the documents?"
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none h-32 text-lg"
            disabled={loading}
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="streamMode"
              checked={streamMode}
              onChange={(e) => setStreamMode(e.target.checked)}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="streamMode" className="text-sm font-medium text-gray-700">
              Enable Streaming Response ⚡
            </label>
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className={`px-8 py-3 rounded-xl font-semibold text-white shadow-lg transform transition-all ${
              loading || !query.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:scale-105 hover:shadow-xl'
            }`}
          >
            {loading ? (
              <span className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing...</span>
              </span>
            ) : (
              <span className="flex items-center space-x-2">
                <span>🔍</span>
                <span>Search</span>
              </span>
            )}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-2 border-red-500 rounded-xl p-6 shadow-lg">
          <div className="flex items-start">
            <span className="text-2xl mr-3">❌</span>
            <div>
              <h3 className="text-lg font-semibold text-red-800 mb-1">Error</h3>
              <p className="text-red-600">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Streaming Response */}
      {loading && streamMode && streamingText && (
        <div className="bg-blue-50 border-2 border-blue-500 rounded-xl p-6 shadow-lg">
          <div className="flex items-start mb-4">
            <span className="text-2xl mr-3">💬</span>
            <h3 className="text-xl font-bold text-gray-800">Streaming Response...</h3>
          </div>
          <div className="bg-white rounded-lg p-4 whitespace-pre-wrap">
            {streamingText}
            <span className="inline-block w-2 h-5 bg-blue-500 animate-pulse ml-1"></span>
          </div>
        </div>
      )}

      {/* Response */}
      {response && !loading && (
        <div className="space-y-6">
          {/* Answer */}
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-500 rounded-xl p-6 shadow-lg">
            <div className="flex items-start mb-4">
              <span className="text-2xl mr-3">💡</span>
              <h3 className="text-xl font-bold text-gray-800">Answer</h3>
            </div>
            <div className="bg-white rounded-lg p-4">
              <p className="text-gray-800 text-lg leading-relaxed whitespace-pre-wrap">
                {response.response}
              </p>
            </div>
            {response.execution_time > 0 && (
              <div className="mt-4 text-sm text-gray-600">
                ⏱️ Execution time: {response.execution_time}s
              </div>
            )}
          </div>

          {/* Relevant Chunks */}
          {response.relevant_chunks && response.relevant_chunks.length > 0 && (
            <div className="bg-purple-50 border-2 border-purple-500 rounded-xl p-6 shadow-lg">
              <div className="flex items-start mb-4">
                <span className="text-2xl mr-3">📚</span>
                <h3 className="text-xl font-bold text-gray-800">
                  Relevant Sources ({response.relevant_chunks.length})
                </h3>
              </div>
              <div className="space-y-4">
                {response.relevant_chunks.map((chunk, index) => (
                  <div
                    key={index}
                    className="bg-white rounded-lg p-4 shadow hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-purple-600">
                        📄 {chunk.filename}
                      </span>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                          Chunk #{chunk.chunk_index}
                        </span>
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          {(chunk.similarity * 100).toFixed(1)}% match
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      {chunk.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* How it works */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold text-gray-800 mb-4">🎯 How RAG Works</h3>
        <div className="space-y-3 text-gray-700">
          <div className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">1</span>
            <div>
              <p className="font-semibold">Query Embedding</p>
              <p className="text-sm text-gray-600">Your question is converted to a vector using OpenAI embeddings</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">2</span>
            <div>
              <p className="font-semibold">Vector Similarity Search</p>
              <p className="text-sm text-gray-600">pgvector performs cosine similarity search to find relevant chunks</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">3</span>
            <div>
              <p className="font-semibold">Context Building</p>
              <p className="text-sm text-gray-600">Top matching chunks are retrieved and combined as context</p>
            </div>
          </div>
          <div className="flex items-start">
            <span className="bg-blue-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-semibold">4</span>
            <div>
              <p className="font-semibold">AI Response Generation</p>
              <p className="text-sm text-gray-600">GPT generates a contextual answer based on the retrieved information</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default QueryInterface
