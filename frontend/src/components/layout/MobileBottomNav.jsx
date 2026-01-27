import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  HiOutlineHome, 
  HiHome,
  HiOutlineCollection,
  HiCollection,
  HiOutlineDocumentText,
  HiDocumentText,
  HiOutlineChartBar,
  HiChartBar,
  HiOutlineUser,
  HiUser
} from 'react-icons/hi'

const navItems = [
  { 
    path: '/boshqaruv', 
    icon: HiOutlineHome, 
    activeIcon: HiHome,
    label: 'Bosh sahifa' 
  },
  { 
    path: '/kategoriyalar', 
    icon: HiOutlineCollection, 
    activeIcon: HiCollection,
    label: 'Kategoriyalar' 
  },
  { 
    path: '/holatlar', 
    icon: HiOutlineDocumentText, 
    activeIcon: HiDocumentText,
    label: 'Holatlar' 
  },
  { 
    path: '/rivojlanish', 
    icon: HiOutlineChartBar, 
    activeIcon: HiChartBar,
    label: 'Rivojlanish' 
  },
  { 
    path: '/profil', 
    icon: HiOutlineUser, 
    activeIcon: HiUser,
    label: 'Profil' 
  },
]

export default function MobileBottomNav() {
  const location = useLocation()
  
  // Agar hozirgi sahifa navigatsiya ichida bo'lmasa, profil active
  const isInNav = navItems.some(item => 
    location.pathname === item.path || location.pathname.startsWith(item.path + '/')
  )

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 lg:hidden">
      {/* Blur background */}
      <div className="absolute inset-0 bg-ocean-900/90 backdrop-blur-xl border-t border-white/5" />
      
      {/* Safe area spacer for iOS */}
      <div className="relative flex items-center justify-around px-2 h-16 pb-safe">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || 
                          location.pathname.startsWith(item.path + '/')
          const Icon = isActive ? item.activeIcon : item.icon
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className="relative flex flex-col items-center justify-center w-16 h-full"
            >
              {/* Active indicator */}
              <AnimatePresence>
                {isActive && (
                  <motion.div
                    layoutId="bottomNavIndicator"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute -top-0.5 w-8 h-1 rounded-full bg-med-500"
                  />
                )}
              </AnimatePresence>
              
              {/* Icon */}
              <motion.div
                animate={{ 
                  scale: isActive ? 1.1 : 1,
                  y: isActive ? -2 : 0
                }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                className={`relative ${isActive ? 'text-med-400' : 'text-slate-500'}`}
              >
                <Icon className="w-6 h-6" />
                
                {/* Glow effect when active */}
                {isActive && (
                  <div className="absolute inset-0 blur-lg bg-med-500/30 -z-10" />
                )}
              </motion.div>
              
              {/* Label */}
              <motion.span 
                animate={{ 
                  opacity: isActive ? 1 : 0.6,
                  y: isActive ? 0 : 2
                }}
                className={`text-[10px] mt-1 font-medium ${
                  isActive ? 'text-med-400' : 'text-slate-500'
                }`}
              >
                {item.label}
              </motion.span>
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}
