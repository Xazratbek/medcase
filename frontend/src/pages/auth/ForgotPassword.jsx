import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineMail, HiOutlineArrowLeft, HiOutlineCheckCircle } from 'react-icons/hi'
import { authAPI } from '../../utils/api'
import toast from 'react-hot-toast'

export default function ForgotPassword() {
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [email, setEmail] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      await authAPI.forgotPassword(email)
      setSent(true)
      toast.success("Parolni tiklash havolasi yuborildi!")
    } catch (error) {
      toast.error(error.response?.data?.xato || "Xatolik yuz berdi")
    }
    
    setLoading(false)
  }

  if (sent) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <div className="w-20 h-20 mx-auto rounded-full bg-med-500/20 flex items-center justify-center">
          <HiOutlineCheckCircle className="w-10 h-10 text-med-400" />
        </div>
        
        <h2 className="mt-6 text-2xl font-display font-bold">Email yuborildi!</h2>
        <p className="mt-3 text-slate-400">
          <span className="text-white font-medium">{email}</span> manziliga parolni tiklash havolasi yuborildi.
          Iltimos, pochta qutingizni tekshiring.
        </p>
        
        <div className="mt-8 p-4 rounded-xl bg-ocean-800/50 border border-white/5">
          <p className="text-sm text-slate-400">
            Email kelmadimi? Spam papkasini tekshiring yoki{' '}
            <button 
              onClick={() => setSent(false)} 
              className="text-med-400 hover:text-med-300"
            >
              qayta urinib ko'ring
            </button>
          </p>
        </div>
        
        <Link 
          to="/kirish" 
          className="inline-flex items-center gap-2 mt-8 text-med-400 hover:text-med-300 transition-colors"
        >
          <HiOutlineArrowLeft className="w-5 h-5" />
          <span>Kirish sahifasiga qaytish</span>
        </Link>
      </motion.div>
    )
  }

  return (
    <div>
      <Link 
        to="/kirish" 
        className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
      >
        <HiOutlineArrowLeft className="w-5 h-5" />
        <span>Orqaga</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mt-6"
      >
        <h2 className="text-3xl font-display font-bold">Parolni tiklash</h2>
        <p className="mt-2 text-slate-400">
          Email manzilingizni kiriting va biz sizga parolni tiklash havolasini yuboramiz
        </p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="mt-8 space-y-5"
      >
        <div>
          <label className="input-label">Email</label>
          <div className="relative">
            <HiOutlineMail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="email@example.com"
              className="input-field pl-12"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2 py-4"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Yuborilmoqda...</span>
            </>
          ) : (
            <span>Havola yuborish</span>
          )}
        </button>
      </motion.form>
    </div>
  )
}
