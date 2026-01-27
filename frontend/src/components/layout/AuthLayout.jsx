import { Outlet, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { umumiyAPI } from '../../utils/api'

export default function AuthLayout() {
  const [stats, setStats] = useState([])

  useEffect(() => {
    const fetchLandingData = async () => {
      try {
        const response = await umumiyAPI.getLandingData();
        setStats(response.data.stats);
      } catch (error) {
        console.error("Error fetching landing data:", error);
      }
    };
    fetchLandingData();
  }, []);

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Gradient orbs */}
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-med-500/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-med-600/15 rounded-full blur-[100px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-ocean-700/30 rounded-full blur-[120px]" />
        
        {/* Grid pattern */}
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
        />
      </div>

      {/* Left side - Branding (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-3/5 relative">
        <div className="absolute inset-0 bg-gradient-to-br from-ocean-800 via-ocean-900 to-ocean-900" />
        
        <div className="relative z-10 flex flex-col justify-between p-12 xl:p-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-med-500 to-med-600 flex items-center justify-center shadow-glow">
              <span className="text-2xl font-display font-bold">M</span>
            </div>
            <div>
              <h1 className="font-display font-bold text-xl">MedCase Pro</h1>
              <p className="text-xs text-slate-500">Tibbiy ta'lim platformasi</p>
            </div>
          </Link>

          {/* Main content */}
          <div className="max-w-lg">
            <motion.h2 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-4xl xl:text-5xl font-display font-bold leading-tight"
            >
              Klinik fikrlash
              <span className="text-gradient block mt-2">ko'nikmalaringizni rivojlantiring</span>
            </motion.h2>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-6 text-lg text-slate-400 leading-relaxed"
            >
              Real klinik holatlar asosida o'rganing. Minglab interaktiv savollar, 
              batafsil tushuntirishlar va shaxsiy rivojlanish kuzatuvi bilan.
            </motion.p>

            {/* Stats */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-10 flex gap-8"
            >
              {stats.map((stat) => (
                <div key={stat.label}>
                  <div className="text-3xl font-display font-bold text-gradient">{stat.value}</div>
                  <div className="text-sm text-slate-500 mt-1">{stat.label}</div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Testimonial */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass-card p-6 max-w-md"
          >
            <p className="text-slate-300 italic">
              "MedCase Pro menga rezidentura imtihonlariga tayyorlanishda juda katta yordam berdi. 
              Real holatlar ustida ishlash nazariy bilimlarni amaliyotga qo'llashni o'rgatadi."
            </p>
            <div className="flex items-center gap-3 mt-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center">
                <span className="font-display font-bold">A</span>
              </div>
              <div>
                <p className="font-medium">Aziza Karimova</p>
                <p className="text-xs text-slate-500">Toshkent Tibbiyot Akademiyasi, 6-kurs</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Floating medical icons */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <motion.div
            animate={{ y: [0, -20, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            className="absolute top-1/4 right-20 text-6xl opacity-10"
          >
            🩺
          </motion.div>
          <motion.div
            animate={{ y: [0, 20, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            className="absolute bottom-1/3 right-32 text-5xl opacity-10"
          >
            💊
          </motion.div>
          <motion.div
            animate={{ y: [0, -15, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 2 }}
            className="absolute top-1/2 right-12 text-4xl opacity-10"
          >
            🫀
          </motion.div>
        </div>
      </div>

      {/* Right side - Auth form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-md"
        >
          {/* Mobile logo */}
          <Link to="/" className="flex items-center justify-center gap-3 mb-8 lg:hidden">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-med-500 to-med-600 flex items-center justify-center shadow-glow">
              <span className="text-2xl font-display font-bold">M</span>
            </div>
            <div>
              <h1 className="font-display font-bold text-xl">MedCase Pro</h1>
            </div>
          </Link>

          <Outlet />
        </motion.div>
      </div>
    </div>
  )
}
