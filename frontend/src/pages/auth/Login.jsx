import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../../store/authStore'
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi'
import { FcGoogle } from 'react-icons/fc'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    email_yoki_nom: '',
    parol: ''
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    const result = await login(formData)
    
    if (result.success) {
      // Admin bo'lsa /admin ga, aks holda /boshqaruv ga
      if (result.isAdmin) {
        navigate('/admin')
      } else {
        navigate('/boshqaruv')
      }
    }
    
    setLoading(false)
  }

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="text-3xl font-display font-bold">Xush kelibsiz!</h2>
        <p className="mt-2 text-slate-400">
          Hisobingizga kiring va o'qishni davom ettiring
        </p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="mt-8 space-y-5"
      >
        {/* Email */}
        <div>
          <label className="input-label">Email yoki foydalanuvchi nomi</label>
          <div className="relative">
            <HiOutlineMail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="text"
              name="email_yoki_nom"
              value={formData.email_yoki_nom}
              onChange={handleChange}
              placeholder="email@example.com"
              className="input-field pl-12"
              required
            />
          </div>
        </div>

        {/* Password */}
        <div>
          <label className="input-label">Parol</label>
          <div className="relative">
            <HiOutlineLockClosed className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type={showPassword ? 'text' : 'password'}
              name="parol"
              value={formData.parol}
              onChange={handleChange}
              placeholder="••••••••"
              className="input-field pl-12 pr-12"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
            >
              {showPassword ? (
                <HiOutlineEyeOff className="w-5 h-5" />
              ) : (
                <HiOutlineEye className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Remember & Forgot */}
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              className="w-4 h-4 rounded border-white/20 bg-ocean-800 text-med-500 focus:ring-med-500/20"
            />
            <span className="text-sm text-slate-400">Eslab qolish</span>
          </label>
          <Link 
            to="/parolni-tiklash" 
            className="text-sm text-med-400 hover:text-med-300 transition-colors"
          >
            Parolni unutdingizmi?
          </Link>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2 py-4"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Kirilmoqda...</span>
            </>
          ) : (
            <span>Kirish</span>
          )}
        </button>

        {/* Divider */}
        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10" />
          </div>
          <div className="relative flex justify-center">
            <span className="px-4 text-sm text-slate-500 bg-ocean-900">yoki</span>
          </div>
        </div>

        {/* Google login */}
        <button
          type="button"
          className="w-full flex items-center justify-center gap-3 px-6 py-3.5 rounded-xl
                     bg-white/5 border border-white/10 hover:bg-white/10 
                     transition-all duration-200"
        >
          <FcGoogle className="w-5 h-5" />
          <span>Google bilan kirish</span>
        </button>
      </motion.form>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-8 text-center text-slate-400"
      >
        Hisobingiz yo'qmi?{' '}
        <Link to="/royxatdan-otish" className="text-med-400 hover:text-med-300 font-medium transition-colors">
          Ro'yxatdan o'ting
        </Link>
      </motion.p>
    </div>
  )
}
