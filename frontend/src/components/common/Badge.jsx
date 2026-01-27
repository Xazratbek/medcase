import { motion } from 'framer-motion'

const variants = {
  primary: 'bg-med-500/20 text-med-400 border-med-500/30',
  secondary: 'bg-ocean-700/50 text-slate-400 border-white/10',
  success: 'bg-green-500/20 text-green-400 border-green-500/30',
  warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  danger: 'bg-red-500/20 text-red-400 border-red-500/30',
  gold: 'bg-gold-500/20 text-gold-400 border-gold-500/30',
  purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  coral: 'bg-coral-500/20 text-coral-400 border-coral-500/30',
}

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-xs',
  lg: 'px-4 py-1.5 text-sm',
}

export default function Badge({
  children,
  variant = 'primary',
  size = 'md',
  dot = false,
  animated = false,
  className = ''
}) {
  const Component = animated ? motion.span : 'span'
  const animationProps = animated ? {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    transition: { type: 'spring', stiffness: 500, damping: 30 }
  } : {}

  return (
    <Component
      {...animationProps}
      className={`
        inline-flex items-center gap-1.5 rounded-full border font-medium
        ${variants[variant]} ${sizes[size]} ${className}
      `}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${
          variant === 'success' ? 'bg-green-400' :
          variant === 'warning' ? 'bg-yellow-400' :
          variant === 'danger' ? 'bg-red-400' :
          'bg-current'
        } ${animated ? 'animate-pulse' : ''}`} />
      )}
      {children}
    </Component>
  )
}

// Difficulty badge specifically for cases
export function DifficultyBadge({ difficulty }) {
  const config = {
    OSON: { variant: 'success', label: 'Oson' },
    ORTACHA: { variant: 'warning', label: "O'rtacha" },
    QIYIN: { variant: 'danger', label: 'Qiyin' },
  }

  const { variant, label } = config[difficulty?.toUpperCase()] || config.OSON

  return <Badge variant={variant} size="sm">{label}</Badge>
}

// Rarity badge for achievements
export function RarityBadge({ rarity }) {
  const config = {
    ODDIY: { variant: 'secondary', label: 'Oddiy' },
    NOYOB: { variant: 'blue', label: 'Noyob' },
    EPIK: { variant: 'purple', label: 'Epik' },
    AFSONAVIY: { variant: 'gold', label: 'Afsonaviy' },
  }

  const { variant, label } = config[rarity?.toUpperCase()] || config.ODDIY

  return <Badge variant={variant} size="sm">{label}</Badge>
}
