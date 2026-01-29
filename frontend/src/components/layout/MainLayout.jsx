import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../../store/authStore'
import { 
  HiOutlineHome, 
  HiOutlineCollection,
  HiOutlineDocumentText,
  HiOutlineChartBar,
  HiOutlineChartSquareBar,
  HiOutlineStar,
  HiOutlineBookmark,
  HiOutlineCog,
  HiOutlineLogout,
  HiOutlineMenu,
  HiOutlineX,
  HiOutlineUser,
  HiOutlineFire,
  HiOutlineSearch,
  HiOutlineShieldCheck,
  HiOutlineRefresh,
  HiOutlineClock
} from 'react-icons/hi'
import NotificationDropdown from '../common/NotificationDropdown'
import SearchModal from '../common/SearchModal'
import MobileBottomNav from './MobileBottomNav'
import Footer from './Footer'

const navItems = [
  { path: '/boshqaruv', icon: HiOutlineHome, label: 'Boshqaruv' },
  { path: '/kategoriyalar', icon: HiOutlineCollection, label: 'Kategoriyalar' },
  { path: '/holatlar', icon: HiOutlineDocumentText, label: 'Holatlar' },
  { path: '/takrorlash', icon: HiOutlineRefresh, label: 'Takrorlash' },
  { path: '/imtihon', icon: HiOutlineClock, label: 'Imtihon' },
  { path: '/rivojlanish', icon: HiOutlineChartBar, label: 'Rivojlanish' },
  { path: '/reyting', icon: HiOutlineChartSquareBar, label: 'Reyting' },
  { path: '/yutuqlar', icon: HiOutlineStar, label: 'Yutuqlar' },
  { path: '/xatcholar', icon: HiOutlineBookmark, label: 'Xatcholar' },
]

// Admin rollari
const ADMIN_ROLES = ['admin', 'ADMIN', 'super_admin', 'SUPER_ADMIN']

export default function MainLayout() {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Keyboard shortcut: Ctrl/Cmd + K for search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setSearchQuery('')
        setSearchOpen(true)
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  return (
    <div className="min-h-screen flex">
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 z-50">
        <div className="flex flex-col flex-grow bg-ocean-800/50 backdrop-blur-xl border-r border-white/5">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-5 border-b border-white/5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-med-500 to-med-600 flex items-center justify-center shadow-glow">
              <span className="text-xl font-display font-bold">M</span>
            </div>
            <div>
              <h1 className="font-display font-bold text-lg">MedCase Pro</h1>
              <p className="text-xs text-slate-500">Tibbiy ta'lim</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-hide">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                  ${isActive 
                    ? 'bg-med-500/10 text-med-400 shadow-inner-glow' 
                    : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  }
                `}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
            
            {/* Admin Panel link - faqat adminlar uchun */}
            {ADMIN_ROLES.includes(user?.rol) && (
              <div className="pt-4 mt-4 border-t border-white/5">
                <NavLink
                  to="/admin"
                  className={({ isActive }) => `
                    flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                    ${isActive 
                      ? 'bg-purple-500/20 text-purple-400' 
                      : 'text-purple-400/70 hover:bg-purple-500/10 hover:text-purple-400'
                    }
                  `}
                >
                  <HiOutlineShieldCheck className="w-5 h-5" />
                  <span>Admin Panel</span>
                </NavLink>
              </div>
            )}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-white/5">
            <NavLink
              to="/profil"
              className={({ isActive }) => `
                flex items-center gap-3 p-3 rounded-xl transition-all duration-200
                ${isActive ? 'bg-med-500/10' : 'hover:bg-white/5'}
              `}
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center">
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                ) : (
                  <span className="font-display font-bold">{user?.ism?.[0] || 'F'}</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{user?.ism} {user?.familiya}</p>
                <p className="text-xs text-slate-500 truncate">{user?.email}</p>
              </div>
            </NavLink>

            <div className="flex items-center gap-2 mt-3">
              <NavLink
                to="/sozlamalar"
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-white/5 hover:text-white transition-colors"
              >
                <HiOutlineCog className="w-5 h-5" />
              </NavLink>
              <button
                onClick={logout}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-colors"
              >
                <HiOutlineLogout className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed inset-y-0 left-0 w-72 bg-ocean-800 border-r border-white/5 z-50 lg:hidden"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-4 border-b border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-med-500 to-med-600 flex items-center justify-center">
                    <span className="text-xl font-display font-bold">M</span>
                  </div>
                  <span className="font-display font-bold text-lg">MedCase Pro</span>
                </div>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-2 rounded-lg hover:bg-white/5"
                >
                  <HiOutlineX className="w-6 h-6" />
                </button>
              </div>

              {/* Navigation */}
              <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                {navItems.map((item, index) => (
                  <motion.div
                    key={item.path}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <NavLink
                      to={item.path}
                      className={({ isActive }) => `
                        flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                        ${isActive 
                          ? 'bg-med-500/10 text-med-400' 
                          : 'text-slate-400 hover:bg-white/5 hover:text-white'
                        }
                      `}
                    >
                      <item.icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </NavLink>
                  </motion.div>
                ))}
                
                {/* Admin Panel - Mobile */}
                {ADMIN_ROLES.includes(user?.rol) && (
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: navItems.length * 0.05 }}
                    className="pt-4 mt-4 border-t border-white/5"
                  >
                    <NavLink
                      to="/admin"
                      className={({ isActive }) => `
                        flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200
                        ${isActive 
                          ? 'bg-purple-500/20 text-purple-400' 
                          : 'text-purple-400/70 hover:bg-purple-500/10 hover:text-purple-400'
                        }
                      `}
                    >
                      <HiOutlineShieldCheck className="w-5 h-5" />
                      <span>Admin Panel</span>
                    </NavLink>
                  </motion.div>
                )}
              </nav>

              {/* User section */}
              <div className="p-4 border-t border-white/5">
                <NavLink to="/profil" className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center">
                    <span className="font-display font-bold">{user?.ism?.[0] || 'F'}</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{user?.ism} {user?.familiya}</p>
                    <p className="text-xs text-slate-500">{user?.email}</p>
                  </div>
                </NavLink>
                <button
                  onClick={logout}
                  className="w-full mt-3 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <HiOutlineLogout className="w-5 h-5" />
                  <span>Chiqish</span>
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="flex-1 lg:pl-64">
        {/* Top header */}
        <header className={`
          sticky top-0 z-30 transition-all duration-300
          ${scrolled ? 'bg-ocean-900/80 backdrop-blur-xl border-b border-white/5' : 'bg-transparent'}
        `}>
          <div className="flex items-center justify-between px-4 lg:px-8 py-4">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-white/5 lg:hidden"
            >
              <HiOutlineMenu className="w-6 h-6" />
            </button>

            {/* Streak badge */}
            <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full bg-orange-500/10 border border-orange-500/20">
              <HiOutlineFire className="w-5 h-5 text-orange-400" />
              <span className="text-sm font-medium text-orange-400">
                {user?.streak || 0} kunlik streak
              </span>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-3">
              {/* Search input */}
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-ocean-700/50 hover:bg-ocean-700 border border-white/5 transition-colors group">
                <HiOutlineSearch className="w-5 h-5 text-slate-400 group-hover:text-white" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value)
                    setSearchOpen(true)
                  }}
                  onFocus={() => setSearchOpen(true)}
                  placeholder="Qidirish..."
                  className="bg-transparent outline-none text-sm text-slate-200 placeholder:text-slate-500 w-28 md:w-48"
                />
                <kbd className="hidden md:inline px-1.5 py-0.5 rounded bg-ocean-800 text-xs text-slate-500 border border-white/10">
                  ⌘K
                </kbd>
              </div>

              {/* Notifications */}
              <NotificationDropdown />

              {/* Profile - Desktop */}
              <NavLink
                to="/profil"
                className="hidden sm:flex items-center gap-3 p-2 pr-4 rounded-xl hover:bg-white/5 transition-colors"
              >
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center">
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <span className="font-display font-bold text-sm">{user?.ism?.[0] || 'F'}</span>
                  )}
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-medium">{user?.ism}</p>
                  <p className="text-xs text-slate-500">Daraja {user?.daraja || 1}</p>
                </div>
              </NavLink>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="px-4 lg:px-8 py-6 lg:py-8 pb-24 lg:pb-8">
          <Outlet />
          <Footer />
        </main>
      </div>

      {/* Search Modal */}
      <SearchModal
        isOpen={searchOpen}
        onClose={() => setSearchOpen(false)}
        initialQuery={searchQuery}
      />

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav />
    </div>
  )
}
