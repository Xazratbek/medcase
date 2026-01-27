import { motion } from 'framer-motion'

export default function ProgressRing({
  progress = 0,
  size = 120,
  strokeWidth = 8,
  color = 'med',
  showPercentage = true,
  label,
  children
}) {
  const colors = {
    med: '#14b89c',
    blue: '#3b82f6',
    purple: '#a855f7',
    orange: '#f97316',
    gold: '#fbbf24',
    coral: '#f43f5e',
  }

  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (progress / 100) * circumference

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-ocean-700"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colors[color] || colors.med}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {children || (
          <>
            {showPercentage && (
              <motion.span
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 }}
                className="text-2xl font-display font-bold"
              >
                {Math.round(progress)}%
              </motion.span>
            )}
            {label && (
              <span className="text-xs text-slate-500 mt-1">{label}</span>
            )}
          </>
        )}
      </div>
    </div>
  )
}
