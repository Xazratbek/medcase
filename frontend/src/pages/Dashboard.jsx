import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { progressAPI, caseAPI, takrorlashAPI, imtihonAPI } from '../utils/api'
import { formatQiyinlik } from '../utils/format'
import {
  HiOutlineFire,
  HiOutlineAcademicCap,
  HiOutlineChartBar,
  HiOutlineClock,
  HiOutlineArrowRight,
  HiOutlineLightningBolt,
  HiOutlineBookOpen,
  HiOutlineTrendingUp,
  HiOutlineTrendingDown,
  HiOutlineRefresh,
  HiOutlineDocumentText,
  HiOutlinePlay
} from 'react-icons/hi'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export default function Dashboard() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dailyCase, setDailyCase] = useState(null)
  const [repeatStats, setRepeatStats] = useState(null)
  const [examStats, setExamStats] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, dailyRes, weakAreasRes, repeatRes, examRes] = await Promise.all([
        progressAPI.getDashboard(),
        caseAPI.getDailyChallenge().catch(() => null),
        progressAPI.getWeakAreas().catch(() => null),
        takrorlashAPI.getToday({ limit: 1 }).catch(() => null),
        imtihonAPI.getMyStats().catch(() => null)
      ])

      // Stats - API returns directly, not wrapped in malumot
      const statsData = statsRes.data.malumot || statsRes.data

      // Weak areas - add to stats
      if (weakAreasRes?.data) {
        statsData.zaif_tomonlar = weakAreasRes.data
      }

      setStats(statsData)

      // Daily case - API returns HolatJavob directly
      if (dailyRes) {
        setDailyCase(dailyRes.data.malumot || dailyRes.data)
      }

      // Repeat stats
      if (repeatRes?.data) {
        setRepeatStats(repeatRes.data)
      }

      // Exam stats
      if (examRes?.data) {
        setExamStats(examRes.data)
      }
    } catch (error) {
      console.error('Data loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  const greeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Xayrli tong'
    if (hour < 18) return 'Xayrli kun'
    return 'Xayrli kech'
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-20 skeleton rounded-2xl" />
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-32 skeleton rounded-2xl" />)}
        </div>
        <div className="h-64 skeleton rounded-2xl" />
      </div>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 lg:space-y-8"
    >
      {/* Welcome Section */}
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-display font-bold text-white">
            {greeting()}, <span className="text-gradient">{user?.ism}</span>! 👋
          </h1>
          <p className="mt-1 text-slate-400">
            Bugun ham o'qishni davom ettiramizmi?
          </p>
        </div>
        <Link to="/holatlar" className="btn-primary flex items-center gap-2">
          <HiOutlineBookOpen className="w-5 h-5" />
          <span>O'qishni boshlash</span>
        </Link>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard
          icon={HiOutlineFire}
          label="Streak"
          value={`${stats?.joriy_streak || 0} kun`}
          color="orange"
          trend={stats?.joriy_streak > 0 ? '+1 bugun' : null}
        />
        <StatCard
          icon={HiOutlineAcademicCap}
          label="Yechilgan holatlar"
          value={stats?.jami_yechilgan_holatlar || 0}
          color="med"
        />
        <StatCard
          icon={HiOutlineChartBar}
          label="O'rtacha Aniqlik"
          value={`${stats?.ortacha_aniqlik || 0}%`}
          color="blue"
        />
        <StatCard
          icon={HiOutlineClock}
          label="O'qish vaqti"
          value={formatTime(stats?.bu_hafta_vaqt || 0)}
          color="purple"
        />
        <StatCard
            icon={HiOutlineTrendingUp}
            label="Eng ko'p yechilgan"
            value={stats?.eng_kop_yechilgan_kategoriya || '-'}
            color="green"
        />
        <StatCard
            icon={HiOutlineTrendingDown}
            label="Eng kam yechilgan"
            value={stats?.eng_kam_yechilgan_kategoriya || '-'}
            color="red"
        />
      </motion.div>

      {/* Quick Access - Takrorlash & Imtihon */}
      <motion.div variants={itemVariants} className="grid sm:grid-cols-2 gap-4">
        {/* Takrorlash Card */}
        <Link to="/takrorlash" className="group">
          <div className="glass-card p-6 h-full border border-transparent hover:border-violet-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-violet-500/10">
            <div className="flex items-start justify-between">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/25 group-hover:scale-110 transition-transform duration-300">
                <HiOutlineRefresh className="w-7 h-7 text-white" />
              </div>
              {repeatStats?.jami > 0 && (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-violet-500/20 text-violet-400 border border-violet-500/30">
                  {repeatStats.jami} karta
                </span>
              )}
            </div>
            <h3 className="text-xl font-display font-bold mt-4 group-hover:text-violet-400 transition-colors">
              Takrorlash
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              SM-2 algoritmi bilan xotirangizni mustahkamlang
            </p>
            <div className="flex items-center gap-2 mt-4 text-violet-400 text-sm font-medium">
              <span>Boshlash</span>
              <HiOutlineArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </Link>

        {/* Imtihon Card */}
        <Link to="/imtihon" className="group">
          <div className="glass-card p-6 h-full border border-transparent hover:border-rose-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-rose-500/10">
            <div className="flex items-start justify-between">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-rose-500 to-pink-600 flex items-center justify-center shadow-lg shadow-rose-500/25 group-hover:scale-110 transition-transform duration-300">
                <HiOutlineDocumentText className="w-7 h-7 text-white" />
              </div>
              {examStats?.jami_imtihonlar > 0 && (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  {examStats.ortacha_ball}% o'rtacha
                </span>
              )}
            </div>
            <h3 className="text-xl font-display font-bold mt-4 group-hover:text-rose-400 transition-colors">
              Imtihon rejimi
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              O'zingizni sinab ko'ring va tayyorgarlikni baholang
            </p>
            <div className="flex items-center gap-2 mt-4 text-rose-400 text-sm font-medium">
              <HiOutlinePlay className="w-4 h-4" />
              <span>Boshlash</span>
              <HiOutlineArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </Link>
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Daily Challenge */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-display font-semibold flex items-center gap-2">
                <HiOutlineLightningBolt className="w-5 h-5 text-gold-400" />
                Kunlik mashq
              </h2>
              <span className="badge-gold">+50 ball</span>
            </div>

            {dailyCase ? (
              <div className="space-y-4">
                <p className="text-slate-300 line-clamp-3">{dailyCase.klinik_stsenariy || dailyCase.ssenariy}</p>
                <div className="flex items-center gap-4">
                  <span className={`case-difficulty ${dailyCase.qiyinlik?.toLowerCase()}`}>
                    {formatQiyinlik(dailyCase.qiyinlik)}
                  </span>
                  <span className="text-sm text-slate-500">{dailyCase.kichik_kategoriya_nomi || dailyCase.bolim_nomi || dailyCase.kategoriya_nomi}</span>
                </div>
                <Link
                  to={`/holat/${dailyCase.id}/yechish`}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  <span>Mashqni boshlash</span>
                  <HiOutlineArrowRight className="w-5 h-5" />
                </Link>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto rounded-full bg-med-500/20 flex items-center justify-center">
                  <HiOutlineAcademicCap className="w-8 h-8 text-med-400" />
                </div>
                <p className="mt-4 text-slate-400">Kunlik mashq hali tayyor emas</p>
                <Link to="/holatlar" className="btn-secondary mt-4 inline-flex">
                  Boshqa holatlarni ko'rish
                </Link>
              </div>
            )}
          </div>
        </motion.div>

        {/* Level Progress */}
        <motion.div variants={itemVariants}>
          <div className="glass-card p-6 h-full">
            <h2 className="text-lg font-display font-semibold mb-6">Daraja</h2>

            <div className="text-center">
              <div className="relative w-28 h-28 mx-auto">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="56" cy="56" r="48"
                    className="fill-none stroke-ocean-700"
                    strokeWidth="8"
                  />
                  <circle
                    cx="56" cy="56" r="48"
                    className="fill-none stroke-med-500"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={`${(stats?.daraja_foizi || 0) * 3.01} 301`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-display font-bold">{stats?.daraja || 1}</span>
                </div>
              </div>

              <p className="mt-4 text-sm text-slate-400">
                Keyingi darajagacha <span className="text-white font-medium">{stats?.keyingi_darajagacha || 100}</span> ball
              </p>

              <div className="mt-4 progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${stats?.daraja_foizi || 0}%` }}
                />
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recent Activity & Weak Areas */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <motion.div variants={itemVariants}>
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-display font-semibold">So'nggi faoliyat</h2>
              <Link to="/rivojlanish" className="text-sm text-med-400 hover:text-med-300">
                Barchasini ko'rish
              </Link>
            </div>

            {stats?.oxirgi_faoliyat?.length > 0 ? (
              <div className="space-y-3">
                {stats.oxirgi_faoliyat.slice(0, 5).map((item, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-colors">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      item.togri ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {item.togri ? '✓' : '✗'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{item.holat_nomi}</p>
                      <p className="text-xs text-slate-500">{item.kategoriya}</p>
                    </div>
                    <span className="text-xs text-slate-500">{item.vaqt}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-slate-500 py-8">Hali faoliyat yo'q</p>
            )}
          </div>
        </motion.div>

        {/* Weak Areas */}
        <motion.div variants={itemVariants}>
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-display font-semibold flex items-center gap-2">
                <HiOutlineTrendingUp className="w-5 h-5 text-coral-400" />
                Zaif tomonlar
              </h2>
            </div>

            {stats?.zaif_tomonlar?.length > 0 ? (
              <div className="space-y-4">
                {stats.zaif_tomonlar.slice(0, 4).map((area, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span>{area.kategoriya}</span>
                      <span className="text-slate-500">{area.aniqlik}%</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-coral-500 to-coral-400"
                        style={{ width: `${area.aniqlik}%` }}
                      />
                    </div>
                  </div>
                ))}
                <Link
                  to="/holatlar?filter=zaif"
                  className="btn-secondary w-full mt-4 text-sm"
                >
                  Zaif tomonlarni mashq qilish
                </Link>
              </div>
            ) : (
              <p className="text-center text-slate-500 py-8">Ma'lumot yetarli emas</p>
            )}
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}

function StatCard({ icon: Icon, label, value, color, trend }) {
  const colors = {
    orange: 'from-orange-500/20 to-orange-600/20 text-orange-400',
    med: 'from-med-500/20 to-med-600/20 text-med-400',
    blue: 'from-blue-500/20 to-blue-600/20 text-blue-400',
    purple: 'from-purple-500/20 to-purple-600/20 text-purple-400',
    green: 'from-green-500/20 to-green-600/20 text-green-400',
    red: 'from-red-500/20 to-red-600/20 text-red-400',
  }

  return (
    <div className="glass-card p-5">
      <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${colors[color]} flex items-center justify-center`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="mt-4">
        <div className="text-2xl font-display font-bold">{value}</div>
        <div className="text-sm text-slate-500 mt-0.5">{label}</div>
      </div>
      {trend && (
        <div className="mt-2 text-xs text-green-400">{trend}</div>
      )}
    </div>
  )
}

function formatTime(minutes) {
  if (minutes < 60) return `${minutes} daq`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours} soat ${mins > 0 ? mins + ' daq' : ''}`
}
