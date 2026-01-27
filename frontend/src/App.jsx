import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'

// Layouts
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'

// Pages
import Landing from './pages/Landing'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import ForgotPassword from './pages/auth/ForgotPassword'
import Dashboard from './pages/Dashboard'
import Categories from './pages/Categories'
import Sections from './pages/Sections'
import Cases from './pages/Cases'
import CaseDetail from './pages/CaseDetail'
import CaseSolve from './pages/CaseSolve'
import Progress from './pages/Progress'
import Leaderboard from './pages/Leaderboard'
import Achievements from './pages/Achievements'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import Bookmarks from './pages/Bookmarks'
import SpacedRepetition from './pages/SpacedRepetition'
import ExamMode from './pages/ExamMode'
import ExamHistory from './pages/ExamHistory'
import NotFound from './pages/NotFound'

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard'
import ExcelImport from './pages/admin/ExcelImport'
import AdminUsers from './pages/admin/AdminUsers'
import AdminCases from './pages/admin/AdminCases'
import AdminCategories from './pages/admin/AdminCategories'

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-med-500/30 border-t-med-500 rounded-full animate-spin" />
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/kirish" replace />
  }
  
  return children
}

// Public Route (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore()
  
  if (isAuthenticated) {
    return <Navigate to="/boshqaruv" replace />
  }
  
  return children
}

// Admin Route wrapper
const AdminRoute = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuthStore()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-med-500/30 border-t-med-500 rounded-full animate-spin" />
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/kirish" replace />
  }
  
  // Admin yoki Super Admin ekanligini tekshirish
  const adminRoles = ['admin', 'ADMIN', 'super_admin', 'SUPER_ADMIN']
  if (!adminRoles.includes(user?.rol)) {
    return <Navigate to="/boshqaruv" replace />
  }
  
  return children
}

function App() {
  const { checkAuth } = useAuthStore()
  
  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Landing />} />
      
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/kirish" element={
          <PublicRoute><Login /></PublicRoute>
        } />
        <Route path="/royxatdan-otish" element={
          <PublicRoute><Register /></PublicRoute>
        } />
        <Route path="/parolni-tiklash" element={
          <PublicRoute><ForgotPassword /></PublicRoute>
        } />
      </Route>
      
      {/* Protected Routes */}
      <Route element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route path="/boshqaruv" element={<Dashboard />} />
        <Route path="/kategoriyalar" element={<Categories />} />
        <Route path="/kategoriya/:kategoriyaId/bolimlar" element={<Sections />} />
        <Route path="/holatlar" element={<Cases />} />
        <Route path="/holat/:id" element={<CaseDetail />} />
        <Route path="/holat/:id/yechish" element={<CaseSolve />} />
        <Route path="/rivojlanish" element={<Progress />} />
        <Route path="/reyting" element={<Leaderboard />} />
        <Route path="/yutuqlar" element={<Achievements />} />
        <Route path="/profil" element={<Profile />} />
        <Route path="/sozlamalar" element={<Settings />} />
        <Route path="/xatcholar" element={<Bookmarks />} />
        <Route path="/takrorlash" element={<SpacedRepetition />} />
        <Route path="/imtihon" element={<ExamMode />} />
        <Route path="/imtihon/tarix" element={<ExamHistory />} />
      </Route>
      
      {/* Admin Routes */}
      <Route element={
        <AdminRoute>
          <MainLayout />
        </AdminRoute>
      }>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/import" element={<ExcelImport />} />
        <Route path="/admin/foydalanuvchilar" element={<AdminUsers />} />
        <Route path="/admin/holatlar" element={<AdminCases />} />
        <Route path="/admin/kategoriyalar" element={<AdminCategories />} />
      </Route>
      
      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
