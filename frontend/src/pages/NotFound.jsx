import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { HiOutlineHome } from 'react-icons/hi'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        {/* 404 Number */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative"
        >
          <span className="text-[150px] sm:text-[200px] font-display font-bold text-gradient opacity-20">
            404
          </span>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-6xl">🩺</span>
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-2xl sm:text-3xl font-display font-bold -mt-8"
        >
          Sahifa topilmadi
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-4 text-slate-400 max-w-md mx-auto"
        >
          Afsuski, siz qidirayotgan sahifa mavjud emas yoki boshqa joyga ko'chirilgan.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link to="/" className="btn-primary flex items-center gap-2">
            <HiOutlineHome className="w-5 h-5" />
            <span>Bosh sahifaga qaytish</span>
          </Link>
          <Link to="/holatlar" className="btn-secondary">
            Holatlarni ko'rish
          </Link>
        </motion.div>
      </motion.div>
    </div>
  )
}
