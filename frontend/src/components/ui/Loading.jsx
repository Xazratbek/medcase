import { motion } from 'framer-motion'

export function Spinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
    xl: 'w-16 h-16 border-4',
  }

  return (
    <div className={`${sizes[size]} border-med-500/30 border-t-med-500 rounded-full animate-spin ${className}`} />
  )
}

export function PageLoader() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <div className="relative">
          <div className="w-16 h-16 border-4 border-med-500/30 rounded-full" />
          <div className="w-16 h-16 border-4 border-med-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
        </div>
        <p className="mt-4 text-slate-400">Yuklanmoqda...</p>
      </motion.div>
    </div>
  )
}

export function CardSkeleton({ count = 1, className = '' }) {
  return (
    <>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className={`skeleton rounded-2xl ${className}`} />
      ))}
    </>
  )
}

export function ListSkeleton({ count = 5, height = 'h-16' }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className={`skeleton rounded-xl ${height}`} />
      ))}
    </div>
  )
}

export default function Loading({ type = 'spinner', ...props }) {
  switch (type) {
    case 'page':
      return <PageLoader {...props} />
    case 'cards':
      return <CardSkeleton {...props} />
    case 'list':
      return <ListSkeleton {...props} />
    default:
      return <Spinner {...props} />
  }
}
