import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../../store/authStore'
import { 
  HiOutlineMail, 
  HiOutlineLockClosed, 
  HiOutlineEye, 
  HiOutlineEyeOff,
  HiOutlineUser,
  HiOutlineIdentification,
  HiOutlineAcademicCap
} from 'react-icons/hi'
import { FcGoogle } from 'react-icons/fc'

const roles = [
  { value: 'talaba', label: 'Talaba', icon: '🎓' },
  { value: 'rezident', label: 'Rezident', icon: '👨‍⚕️' },
  { value: 'shifokor', label: 'Shifokor', icon: '⚕️' },
  { value: 'oqituvchi', label: "O'qituvchi", icon: '📚' },
]

export default function Register() {
  const navigate = useNavigate()
  const { register } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    ism: '',
    familiya: '',
    email: '',
    foydalanuvchi_nomi: '',
    parol: '',
    parol_tasdiqlash: '',
    rol: 'talaba',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (step === 1) {
      setStep(2)
      return
    }
    
    if (formData.parol !== formData.parol_tasdiqlash) {
      return
    }
    
    setLoading(true)
    const result = await register(formData)
    
    if (result.success) {
      navigate('/boshqaruv')
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
        <h2 className="text-3xl font-display font-bold">Ro'yxatdan o'tish</h2>
        <p className="mt-2 text-slate-400">
          Yangi hisob yarating va o'qishni boshlang
        </p>
      </motion.div>

      {/* Progress indicator */}
      <div className="flex items-center gap-3 mt-6">
        <div className={`flex-1 h-1.5 rounded-full transition-colors ${step >= 1 ? 'bg-med-500' : 'bg-ocean-700'}`} />
        <div className={`flex-1 h-1.5 rounded-full transition-colors ${step >= 2 ? 'bg-med-500' : 'bg-ocean-700'}`} />
      </div>

      <motion.form
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="mt-8"
      >
        {step === 1 ? (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-5"
          >
            {/* Name fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="input-label">Ism</label>
                <div className="relative">
                  <HiOutlineUser className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type="text"
                    name="ism"
                    value={formData.ism}
                    onChange={handleChange}
                    placeholder="Ism"
                    className="input-field pl-12"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="input-label">Familiya</label>
                <input
                  type="text"
                  name="familiya"
                  value={formData.familiya}
                  onChange={handleChange}
                  placeholder="Familiya"
                  className="input-field"
                  required
                />
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="input-label">Foydalanuvchi nomi</label>
              <div className="relative">
                <HiOutlineIdentification className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="text"
                  name="foydalanuvchi_nomi"
                  value={formData.foydalanuvchi_nomi}
                  onChange={handleChange}
                  placeholder="foydalanuvchi_nomi"
                  className="input-field pl-12"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="input-label">Email</label>
              <div className="relative">
                <HiOutlineMail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="email@example.com"
                  className="input-field pl-12"
                  required
                />
              </div>
            </div>

            {/* Role selection */}
            <div>
              <label className="input-label">Sizning rolingiz</label>
              <div className="grid grid-cols-2 gap-3">
                {roles.map((role) => (
                  <button
                    key={role.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, rol: role.value }))}
                    className={`
                      flex items-center gap-3 p-4 rounded-xl border-2 transition-all duration-200
                      ${formData.rol === role.value 
                        ? 'border-med-500 bg-med-500/10' 
                        : 'border-white/10 bg-ocean-800/50 hover:border-white/20'
                      }
                    `}
                  >
                    <span className="text-2xl">{role.icon}</span>
                    <span className="font-medium">{role.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="btn-primary w-full py-4 mt-6">
              Davom etish
            </button>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-5"
          >
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
                  placeholder="Kamida 8 belgi"
                  className="input-field pl-12 pr-12"
                  minLength={8}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                >
                  {showPassword ? <HiOutlineEyeOff className="w-5 h-5" /> : <HiOutlineEye className="w-5 h-5" />}
                </button>
              </div>
              
              {/* Password strength indicator */}
              <div className="mt-2 flex gap-1">
                {[1, 2, 3, 4].map((level) => (
                  <div
                    key={level}
                    className={`h-1 flex-1 rounded-full transition-colors ${
                      formData.parol.length >= level * 3
                        ? level <= 2 ? 'bg-red-500' : level === 3 ? 'bg-yellow-500' : 'bg-green-500'
                        : 'bg-ocean-700'
                    }`}
                  />
                ))}
              </div>
            </div>

            {/* Confirm password */}
            <div>
              <label className="input-label">Parolni tasdiqlang</label>
              <div className="relative">
                <HiOutlineLockClosed className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="parol_tasdiqlash"
                  value={formData.parol_tasdiqlash}
                  onChange={handleChange}
                  placeholder="Parolni qaytadan kiriting"
                  className={`input-field pl-12 ${
                    formData.parol_tasdiqlash && formData.parol !== formData.parol_tasdiqlash
                      ? 'border-red-500 focus:border-red-500'
                      : ''
                  }`}
                  required
                />
              </div>
              {formData.parol_tasdiqlash && formData.parol !== formData.parol_tasdiqlash && (
                <p className="mt-1 text-sm text-red-400">Parollar mos kelmadi</p>
              )}
            </div>

            {/* Terms */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input 
                type="checkbox" 
                required
                className="mt-1 w-4 h-4 rounded border-white/20 bg-ocean-800 text-med-500 focus:ring-med-500/20"
              />
              <span className="text-sm text-slate-400">
                <Link to="/shartlar" className="text-med-400 hover:text-med-300">Foydalanish shartlari</Link>
                {' '}va{' '}
                <Link to="/maxfiylik" className="text-med-400 hover:text-med-300">Maxfiylik siyosati</Link>
                ga roziman
              </span>
            </label>

            {/* Buttons */}
            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="btn-secondary flex-1 py-4"
              >
                Orqaga
              </button>
              <button
                type="submit"
                disabled={loading || formData.parol !== formData.parol_tasdiqlash}
                className="btn-primary flex-1 flex items-center justify-center gap-2 py-4"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Yaratilmoqda...</span>
                  </>
                ) : (
                  <span>Hisob yaratish</span>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {step === 1 && (
          <>
            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center">
                <span className="px-4 text-sm text-slate-500 bg-ocean-900">yoki</span>
              </div>
            </div>

            {/* Google */}
            <button
              type="button"
              className="w-full flex items-center justify-center gap-3 px-6 py-3.5 rounded-xl
                         bg-white/5 border border-white/10 hover:bg-white/10 
                         transition-all duration-200"
            >
              <FcGoogle className="w-5 h-5" />
              <span>Google bilan ro'yxatdan o'tish</span>
            </button>
          </>
        )}
      </motion.form>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-8 text-center text-slate-400"
      >
        Hisobingiz bormi?{' '}
        <Link to="/kirish" className="text-med-400 hover:text-med-300 font-medium transition-colors">
          Kirish
        </Link>
      </motion.p>
    </div>
  )
}
