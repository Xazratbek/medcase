import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

export default function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  actionLink,
  actionText = "Boshlash"
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center py-16"
    >
      {Icon && (
        <div className="w-24 h-24 mx-auto rounded-3xl bg-gradient-to-br from-ocean-700/50 to-ocean-800/50 flex items-center justify-center mb-6">
          <Icon className="w-12 h-12 text-slate-500" />
        </div>
      )}
      
      <h3 className="text-xl font-display font-semibold">{title}</h3>
      
      {description && (
        <p className="mt-2 text-slate-500 max-w-md mx-auto">{description}</p>
      )}
      
      {(action || actionLink) && (
        <div className="mt-6">
          {actionLink ? (
            <Link to={actionLink} className="btn-primary inline-flex">
              {actionText}
            </Link>
          ) : (
            <button onClick={action} className="btn-primary">
              {actionText}
            </button>
          )}
        </div>
      )}
    </motion.div>
  )
}
