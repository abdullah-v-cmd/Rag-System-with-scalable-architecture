import React from 'react'

function Stats({ stats }) {
  const statItems = [
    {
      label: 'Total Documents',
      value: stats.total_documents,
      icon: '📄',
      color: 'from-blue-500 to-blue-600'
    },
    {
      label: 'Document Chunks',
      value: stats.total_chunks,
      icon: '🧩',
      color: 'from-purple-500 to-purple-600'
    },
    {
      label: 'Total Queries',
      value: stats.total_queries,
      icon: '💬',
      color: 'from-green-500 to-green-600'
    },
    {
      label: 'Cache Hit Rate',
      value: `${stats.cache_hit_rate}%`,
      icon: '⚡',
      color: 'from-yellow-500 to-orange-600'
    }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statItems.map((item, index) => (
          <div
            key={index}
            className="bg-white rounded-xl shadow-lg p-6 transform transition-all hover:scale-105 hover:shadow-xl"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{item.label}</p>
                <p className="text-3xl font-bold text-gray-800">{item.value}</p>
              </div>
              <div className={`bg-gradient-to-br ${item.color} p-4 rounded-xl shadow-lg`}>
                <span className="text-3xl">{item.icon}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Stats
