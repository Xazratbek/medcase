import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { notificationAPI } from '../../utils/api'
import { useWebSocket } from '../../hooks/useWebSocket'
import {
  HiOutlineBell,
  HiOutlineCheck,
  HiOutlineStar,
  HiOutlineFire,
  HiOutlineAcademicCap,
  HiOutlineChartBar,
  HiOutlineX,
  HiOutlineTrendingUp,
  HiOutlineSparkles,
  HiOutlineCog
} from 'react-icons/hi'
import { formatDistanceToNow } from 'date-fns'
import { uz } from 'date-fns/locale'

const notificationIcons = {
  NISHON: HiOutlineStar,
  yangi_nishon: HiOutlineStar,
  STREAK: HiOutlineFire,
  streak_yangilash: HiOutlineFire,
  HOLAT: HiOutlineAcademicCap,
  REYTING: HiOutlineChartBar,
  reyting_yangilash: HiOutlineTrendingUp,
  TIZIM: HiOutlineBell,
  bildirishnoma: HiOutlineBell,
  daraja_oshdi: HiOutlineSparkles,
}

const notificationColors = {
  NISHON: 'text-gold-400 bg-gold-500/20',
  yangi_nishon: 'text-gold-400 bg-gold-500/20',
  STREAK: 'text-orange-400 bg-orange-500/20',
  streak_yangilash: 'text-orange-400 bg-orange-500/20',
  HOLAT: 'text-med-400 bg-med-500/20',
  REYTING: 'text-purple-400 bg-purple-500/20',
  reyting_yangilash: 'text-purple-400 bg-purple-500/20',
  TIZIM: 'text-blue-400 bg-blue-500/20',
  bildirishnoma: 'text-blue-400 bg-blue-500/20',
  daraja_oshdi: 'text-med-400 bg-med-500/20',
}

export default function NotificationDropdown() {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [newNotification, setNewNotification] = useState(null)
  const dropdownRef = useRef(null)
  
  // WebSocket integratsiyasi
  const { isConnected, lastMessage, subscribe } = useWebSocket()

  // WebSocket xabarlarini tinglash
  useEffect(() => {
    if (lastMessage) {
      const { turi, sarlavha, malumot, vaqt } = lastMessage
      
      // Real-time bildirishnoma keldi
      if (['bildirishnoma', 'yangi_nishon', 'daraja_oshdi', 'streak_yangilash', 'reyting_yangilash'].includes(turi)) {
        const yangi = {
          id: Date.now(),
          turi: turi,
          sarlavha: sarlavha,
          matn: malumot?.matn || malumot?.nishon_nomi || '',
          oqilgan: false,
          yaratilgan_vaqt: vaqt || new Date().toISOString(),
          havola: malumot?.havola
        }
        
        // Yangi bildirishnomani qo'shish
        setNotifications(prev => [yangi, ...prev].slice(0, 20))
        setUnreadCount(prev => prev + 1)
        
        // Animatsiya uchun
        setNewNotification(yangi)
        setTimeout(() => setNewNotification(null), 3000)
      }
    }
  }, [lastMessage])

  // Reyting kanaliga obuna
  useEffect(() => {
    if (isConnected) {
      subscribe('reyting')
    }
  }, [isConnected, subscribe])

  useEffect(() => {
    loadUnreadCount()
    
    // Click tashqarisida yopish
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (isOpen) {
      loadNotifications()
    }
  }, [isOpen])

  const loadUnreadCount = async () => {
    try {
      const response = await notificationAPI.getUnreadCount()
      setUnreadCount(response.data.oqilmagan_soni || response.data.soni || 0)
    } catch (error) {
      console.error('Unread count error:', error)
    }
  }

  const loadNotifications = async () => {
    setLoading(true)
    try {
      const response = await notificationAPI.getAll({ hajm: 10 })
      setNotifications(response.data.bildirishnomalar || response.data.natijalar || [])
    } catch (error) {
      console.error('Notifications error:', error)
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (id) => {
    try {
      await notificationAPI.markAsRead(id)
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, oqilgan: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Mark as read error:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead()
      setNotifications(prev => prev.map(n => ({ ...n, oqilgan: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Mark all as read error:', error)
    }
  }

  const handleNotificationClick = (notification) => {
    if (!notification.oqilgan) {
      markAsRead(notification.id)
    }
    if (notification.havola) {
      setIsOpen(false)
      navigate(notification.havola)
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2.5 rounded-xl hover:bg-white/5 transition-colors group"
      >
        <HiOutlineBell className={`w-6 h-6 transition-colors ${
          unreadCount > 0 ? 'text-white' : 'text-slate-400 group-hover:text-white'
        }`} />
        
        {/* Unread badge */}
        <AnimatePresence>
          {unreadCount > 0 && (
            <motion.span 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-coral-500 text-xs font-bold flex items-center justify-center shadow-lg shadow-coral-500/50"
            >
              {unreadCount > 9 ? '9+' : unreadCount}
            </motion.span>
          )}
        </AnimatePresence>
        
        {/* WebSocket connection indicator */}
        <span className={`absolute bottom-0.5 right-0.5 w-2 h-2 rounded-full ${
          isConnected ? 'bg-green-500' : 'bg-slate-500'
        }`} />
      </button>

      {/* New notification toast (floating) */}
      <AnimatePresence>
        {newNotification && !isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, x: 20 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 top-14 w-72 glass-card p-3 z-50 border border-med-500/30"
          >
            <div className="flex items-start gap-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                notificationColors[newNotification.turi] || notificationColors.TIZIM
              }`}>
                {(() => {
                  const Icon = notificationIcons[newNotification.turi] || HiOutlineBell
                  return <Icon className="w-4 h-4" />
                })()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{newNotification.sarlavha}</p>
                <p className="text-xs text-slate-400 truncate">{newNotification.matn}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-80 sm:w-96 glass-card overflow-hidden z-50"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
              <div className="flex items-center gap-2">
                <h3 className="font-display font-semibold">Bildirishnomalar</h3>
                {isConnected && (
                  <span className="flex items-center gap-1 text-xs text-green-400">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                    Live
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-xs text-med-400 hover:text-med-300 font-medium"
                  >
                    Barchasini o'qish
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-white transition-colors"
                  title="Yopish"
                >
                  <HiOutlineX className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setIsOpen(false)
                    navigate('/sozlamalar')
                  }}
                  className="p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-white transition-colors"
                >
                  <HiOutlineCog className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Notifications list */}
            <div className="max-h-[60vh] overflow-y-auto scrollbar-hide">
              {loading ? (
                <div className="p-4 space-y-3">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-16 skeleton rounded-xl" />
                  ))}
                </div>
              ) : notifications.length > 0 ? (
                <div className="divide-y divide-white/5">
                  {notifications.map((notification, index) => {
                    const Icon = notificationIcons[notification.turi] || HiOutlineBell
                    const colorClass = notificationColors[notification.turi] || notificationColors.TIZIM
                    
                    return (
                      <motion.div
                        key={notification.id}
                        initial={index === 0 && newNotification?.id === notification.id ? { backgroundColor: 'rgba(20, 184, 156, 0.2)' } : {}}
                        animate={{ backgroundColor: 'transparent' }}
                        transition={{ duration: 2 }}
                        className={`flex items-start gap-3 p-4 hover:bg-white/5 transition-colors cursor-pointer ${
                          !notification.oqilgan ? 'bg-med-500/5' : ''
                        }`}
                        onClick={() => handleNotificationClick(notification)}
                      >
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm ${!notification.oqilgan ? 'font-medium' : 'text-slate-400'}`}>
                            {notification.sarlavha}
                          </p>
                          {notification.matn && (
                            <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                              {notification.matn}
                            </p>
                          )}
                          <p className="text-xs text-slate-600 mt-1">
                            {notification.yaratilgan_vaqt && formatDistanceToNow(
                              new Date(notification.yaratilgan_vaqt),
                              { addSuffix: true, locale: uz }
                            )}
                          </p>
                        </div>
                        {!notification.oqilgan && (
                          <div className="w-2 h-2 rounded-full bg-med-500 mt-2 flex-shrink-0" />
                        )}
                      </motion.div>
                    )
                  })}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <div className="w-16 h-16 mx-auto rounded-full bg-ocean-700/50 flex items-center justify-center mb-3">
                    <HiOutlineBell className="w-8 h-8 text-slate-500" />
                  </div>
                  <p className="text-slate-400 font-medium">Bildirishnomalar yo'q</p>
                  <p className="text-xs text-slate-500 mt-1">Yangi xabarlar bu yerda ko'rinadi</p>
                </div>
              )}
            </div>

            {/* Footer */}
            {notifications.length > 5 && (
              <div className="px-4 py-3 border-t border-white/5 bg-ocean-800/50">
                <button
                  onClick={() => {
                    setIsOpen(false)
                    // TODO: Barcha bildirishnomalar sahifasiga o'tish
                  }}
                  className="w-full text-center text-sm text-med-400 hover:text-med-300 font-medium transition-colors"
                >
                  Barcha bildirishnomalarni ko'rish
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
