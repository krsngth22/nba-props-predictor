export function SkeletonCard() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 animate-pulse">
      <div className="h-3 bg-gray-800 rounded w-20 mb-4" />
      <div className="h-8 bg-gray-800 rounded w-16 mb-3" />
      <div className="h-3 bg-gray-800 rounded w-24" />
    </div>
  )
}

export function SkeletonTable() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden animate-pulse">
      <div className="border-b border-gray-800 px-4 py-3">
        <div className="h-3 bg-gray-800 rounded w-48" />
      </div>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="border-b border-gray-800/50 px-4 py-3 flex gap-4">
          <div className="h-3 bg-gray-800 rounded w-20" />
          <div className="h-3 bg-gray-800 rounded w-32" />
          <div className="h-3 bg-gray-800 rounded w-8 ml-auto" />
          <div className="h-3 bg-gray-800 rounded w-8" />
          <div className="h-3 bg-gray-800 rounded w-8" />
        </div>
      ))}
    </div>
  )
}
