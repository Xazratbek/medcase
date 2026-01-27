import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HiOutlineX } from 'react-icons/hi'

export default function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'md',
  showClose = true 
}) {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  }

  // ESC tugmasi bilan yopish
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      document.addEventListener('keydown', handleEsc)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={`relative w-full ${sizes[size]} glass-card overflow-hidden`}
          >
            {/* Header */}
            {(title || showClose) && (
              <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
                {title && (
                  <h2 className="text-lg font-display font-semibold">{title}</h2>
                )}
                {showClose && (
                  <button
                    onClick={onClose}
                    className="p-2 -mr-2 rounded-lg hover:bg-white/5 transition-colors"
                  >
                    <HiOutlineX className="w-5 h-5" />
                  </button>
                )}
              </div>
            )}

            {/* Body */}
            <div className="p-6 max-h-[70vh] overflow-y-auto">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}

// Confirmation Modal
export function ConfirmModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = "Tasdiqlash",
  message = "Haqiqatan ham davom etmoqchimisiz?",
  confirmText = "Ha",
  cancelText = "Yo'q",
  variant = 'danger' // danger, warning, info
}) {
  const variants = {
    danger: 'bg-red-500 hover:bg-red-600',
    warning: 'bg-yellow-500 hover:bg-yellow-600',
    info: 'bg-med-500 hover:bg-med-600',
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <p className="text-slate-400 mb-6">{message}</p>
      <div className="flex gap-3 justify-end">
        <button onClick={onClose} className="btn-secondary">
          {cancelText}
        </button>
        <button 
          onClick={() => { onConfirm(); onClose(); }}
          className={`px-6 py-3 rounded-xl font-medium text-white transition-colors ${variants[variant]}`}
        >
          {confirmText}
        </button>
      </div>
    </Modal>
  )
}
