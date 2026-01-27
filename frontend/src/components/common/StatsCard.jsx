import { motion } from 'framer-motion'

export default function StatsCard({ 
  icon: Icon, 
  label, 
  value, 
  subtext, 
  trend, 
  color = 'med',
  delay = 0 
}) {
  const colors = {
    med: {
      bg: 'from-med-500/20 to-med-600/10',
      icon: 'text-med-400',
      glow: 'shadow-med-500/20'
    },
    blue: {
      bg: 'from-blue-500/20 to-blue-600/10',
      icon: 'text-blue-400',
      glow: 'shadow-blue-500/20'
    },
    purple: {
      bg: 'from-purple-500/20 to-purple-600/10',
      icon: 'text-purple-400',
      glow: 'shadow-purple-500/20'
    },
    orange: {
      bg: 'from-orange-500/20 to-orange-600/10',
      icon: 'text-orange-400',
      glow: 'shadow-orange-500/20'
    },
    gold: {
      bg: 'from-gold-400/20 to-gold-500/10',
      icon: 'text-gold-400',
      glow: 'shadow-gold-500/20'
    },
    coral: {
      bg: 'from-coral-400/20 to-coral-500/10',
      icon: 'text-coral-400',
      glow: 'shadow-coral-500/20'
    },
  }

  const colorSet = colors[color] || colors.med

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className={`glass-card p-5 relative overflow-hidden group hover:shadow-lg ${colorSet.glow}`}
    >
      {/* Background gradient glow */}
      <div className={`absolute -top-10 -right-10 w-32 h-32 rounded-full bg-gradient-to-br ${colorSet.bg} blur-2xl opacity-50 group-hover:opacity-80 transition-opacity`} />
      
      <div className="relative">
        {/* Icon */}
        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${colorSet.bg} flex items-center justify-center mb-4`}>
          <Icon className={`w-6 h-6 ${colorSet.icon}`} />
        </div>

        {/* Value */}
        <div className="text-3xl font-display font-bold tracking-tight">
          {value}
        </div>

        {/* Label */}
        <div className="text-sm text-slate-500 mt-1">{label}</div>

        {/* Trend/Subtext */}
        {(trend || subtext) && (
          <div className={`mt-3 text-xs font-medium ${
            trend === 'up' ? 'text-green-400' : 
            trend === 'down' ? 'text-red-400' : 
            'text-slate-500'
          }`}>
            {trend === 'up' && '↑ '}
            {trend === 'down' && '↓ '}
            {subtext}
          </div>
        )}
      </div>
    </motion.div>
  )
}
