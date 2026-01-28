import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { imtihonAPI } from '../utils/api'
import {
  HiOutlineDocumentText,
  HiOutlineCheck,
  HiOutlineX,
  HiOutlineClock,
  HiOutlineChartBar,
  HiOutlineCalendar,
  HiOutlineTrendingUp,
  HiOutlineTrendingDown,
  HiOutlinePlay,
  HiOutlineEye
} from 'react-icons/hi'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

function formatTime(seconds) {
  if (!seconds) return '0 daq'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins === 0) return `${secs} son`
  return secs > 0 ? `${mins} daq ${secs} son` : `${mins} daq`
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('uz-UZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function StatCard({ icon: Icon, label, value, subtext, color }) {
  const colorClasses = {
    emerald: 'from-emerald-500/20 to-teal-600/20 text-emerald-400',
    rose: 'from-rose-500/20 to-pink-600/20 text-rose-400',
    blue: 'from-blue-500/20 to-cyan-600/20 text-blue-400',
    amber: 'from-amber-500/20 to-orange-600/20 text-amber-400',
  }

  return (
    <div className="glass-card p-5">
      <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center`}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="mt-4">
        <div className="text-2xl font-display font-bold">{value}</div>
        <div className="text-sm text-slate-500 mt-0.5">{label}</div>
        {subtext && <div className="text-xs text-slate-600 mt-1">{subtext}</div>}
      </div>
    </div>
  )
}

function ExamCard({ exam }) {
  const passed = exam.otgan
  const percentage = exam.ball_foizi || 0

  return (
    <motion.div
      variants={itemVariants}
      className="glass-card p-5 hover:border-white/10 transition-all duration-300"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
              passed
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}>
              {passed ? "O'tdi" : "O'tmadi"}
            </span>
            <span className="text-xs text-slate-500 capitalize">{exam.turi}</span>
          </div>

          <h3 className="font-semibold text-white truncate">{exam.nom}</h3>

          <div className="flex items-center gap-4 mt-3 text-sm text-slate-400">
            <span className="flex items-center gap-1.5">
              <HiOutlineCalendar className="w-4 h-4" />
              {formatDate(exam.boshlangan_vaqt)}
            </span>
            <span className="flex items-center gap-1.5">
              <HiOutlineClock className="w-4 h-4" />
              {formatTime(exam.sarflangan_vaqt)}
            </span>
          </div>
        </div>

        {/* Score Circle */}
        <div className="relative w-16 h-16 flex-shrink-0">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="32" cy="32" r="28"
              className="fill-none stroke-ocean-700"
              strokeWidth="4"
            />
            <circle
              cx="32" cy="32" r="28"
              className={`fill-none ${passed ? 'stroke-emerald-500' : 'stroke-red-500'}`}
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${percentage * 1.76} 176`}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-lg font-bold">{percentage}%</span>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="flex items-center gap-6 mt-4 pt-4 border-t border-white/5">
        <div className="flex items-center gap-2">
          <HiOutlineCheck className="w-4 h-4 text-emerald-400" />
          <span className="text-sm"><span className="font-medium text-white">{exam.togri_javoblar}</span> to'g'ri</span>
        </div>
        <div className="flex items-center gap-2">
          <HiOutlineX className="w-4 h-4 text-red-400" />
          <span className="text-sm"><span className="font-medium text-white">{exam.notogri_javoblar}</span> noto'g'ri</span>
        </div>
        <div className="text-sm text-slate-500">
          {exam.jami_savollar} ta savol
        </div>
      </div>
    </motion.div>
  )
}

export default function ExamHistory() {
  const [exams, setExams] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    loadData()
  }, [page])

  const loadData = async () => {
    setLoading(true)
    try {
      const [examsRes, statsRes] = await Promise.all([
        imtihonAPI.getMyExams({ sahifa: page, hajm: 10 }),
        imtihonAPI.getMyStats()
      ])

      setExams(examsRes.data.imtihonlar || [])
      setTotal(examsRes.data.jami || 0)
      setStats(statsRes.data)
    } catch (error) {
      console.error('Error loading exam history:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-12 skeleton rounded-2xl w-64" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-32 skeleton rounded-2xl" />)}
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map(i => <div key={i} className="h-40 skeleton rounded-2xl" />)}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-rose-500 to-pink-600
                          flex items-center justify-center shadow-lg shadow-rose-500/25">
            <HiOutlineChartBar className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl lg:text-3xl font-display font-bold">Imtihon tarixi</h1>
            <p className="text-slate-400">Barcha imtihon natijalaringiz</p>
          </div>
        </div>

        <Link to="/imtihon" className="btn-primary flex items-center gap-2">
          <HiOutlinePlay className="w-5 h-5" />
          <span className="hidden sm:inline">Yangi imtihon</span>
        </Link>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={HiOutlineDocumentText}
            label="Jami imtihonlar"
            value={stats.jami_imtihonlar || 0}
            color="blue"
          />
          <StatCard
            icon={HiOutlineCheck}
            label="O'tgan"
            value={stats.otgan_imtihonlar || 0}
            subtext={stats.jami_imtihonlar > 0 ? `${Math.round((stats.otgan_imtihonlar / stats.jami_imtihonlar) * 100)}%` : null}
            color="emerald"
          />
          <StatCard
            icon={HiOutlineTrendingUp}
            label="O'rtacha ball"
            value={`${Math.round(stats.ortacha_ball || 0)}%`}
            color="amber"
          />
          <StatCard
            icon={HiOutlineTrendingDown}
            label="Eng yuqori"
            value={`${stats.eng_yuqori_ball || 0}%`}
            color="rose"
          />
        </div>
      )}

      {/* Exam List */}
      {exams.length > 0 ? (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-4"
        >
          {exams.map((exam) => (
            <ExamCard key={exam.id} exam={exam} />
          ))}
        </motion.div>
      ) : (
        <div className="glass-card p-12 text-center">
          <div className="w-20 h-20 mx-auto rounded-2xl bg-ocean-700/50 flex items-center justify-center mb-4">
            <HiOutlineDocumentText className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Hali imtihon topshirmadingiz</h3>
          <p className="text-slate-400 mb-6">Birinchi imtihonni boshlang va natijalarni bu yerda ko'ring</p>
          <Link to="/imtihon" className="btn-primary inline-flex items-center gap-2">
            <HiOutlinePlay className="w-5 h-5" />
            Imtihon boshlash
          </Link>
        </div>
      )}

      {/* Pagination */}
      {total > 10 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || loading}
            className="px-4 py-2 rounded-lg bg-ocean-700/50 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-ocean-700 transition-colors"
          >
            Oldingi
          </button>
          <span className="px-4 py-2 text-slate-400">
            {page} / {Math.ceil(total / 10)}
          </span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(total / 10) || loading}
            className="px-4 py-2 rounded-lg bg-ocean-700/50 text-slate-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-ocean-700 transition-colors"
          >
            Keyingi
          </button>
        </div>
      )}
    </motion.div>
  )
}
