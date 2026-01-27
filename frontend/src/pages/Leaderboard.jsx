import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { gamificationAPI } from '../utils/api'
import { useAuthStore } from '../store/authStore'
import {
  HiOutlineChartSquareBar,
  HiOutlineGlobeAlt,
  HiOutlineUserGroup,
  HiOutlineAcademicCap,
  HiOutlineChevronUp,
  HiOutlineChevronDown,
  HiOutlineMinus
} from 'react-icons/hi'

export default function Leaderboard() {
  const { user } = useAuthStore()
  const [leaderboard, setLeaderboard] = useState([])
  const [myRank, setMyRank] = useState(null)
  const [loading, setLoading] = useState(true)
  const [type, setType] = useState('global') // global, haftalik, kategoriya
  const [category, setCategory] = useState('')

  useEffect(() => {
    loadLeaderboard()
  }, [type, category])

  const loadLeaderboard = async () => {
    setLoading(true)
    try {
      const response = await gamificationAPI.getLeaderboard({ 
        turi: type,
        kategoriya_id: category || undefined 
      })
      
      const data = response.data
      // Backend ReytingRoyxati qaytaradi: foydalanuvchilar, joriy_foydalanuvchi_orni, jami
      setLeaderboard(data.foydalanuvchilar || [])
      setMyRank(data.joriy_foydalanuvchi_orni || null)
    } catch (error) {
      console.error('Leaderboard loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRankStyle = (rank) => {
    switch (rank) {
      case 1: return 'from-gold-400 to-gold-600 text-white shadow-lg shadow-gold-500/30'
      case 2: return 'from-slate-300 to-slate-400 text-slate-900'
      case 3: return 'from-orange-400 to-orange-600 text-white'
      default: return 'from-ocean-700 to-ocean-600 text-slate-400'
    }
  }

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1: return '🥇'
      case 2: return '🥈'
      case 3: return '🥉'
      default: return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 lg:space-y-8"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-display font-bold flex items-center gap-3">
            <HiOutlineChartSquareBar className="w-8 h-8 text-gold-400" />
            Reyting
          </h1>
          <p className="text-slate-400 mt-1">Eng yaxshi o'quvchilar</p>
        </div>

        {/* Type selector */}
        <div className="flex items-center gap-2 p-1 rounded-xl bg-ocean-800/50">
          {[
            { value: 'global', label: 'Global', icon: HiOutlineGlobeAlt },
            { value: 'haftalik', label: 'Haftalik', icon: HiOutlineUserGroup },
          ].map((t) => (
            <button
              key={t.value}
              onClick={() => setType(t.value)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                type === t.value
                  ? 'bg-med-500 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* My Rank Card */}
      {myRank && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 border border-med-500/30"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-med-500 to-med-600 flex items-center justify-center font-display font-bold text-xl">
                #{myRank.orni}
              </div>
              <div>
                <p className="font-medium">Sizning o'rningiz</p>
                <p className="text-sm text-slate-500">{myRank.ball?.toLocaleString()} ball</p>
              </div>
            </div>
            <div className="text-right">
              <div className={`flex items-center gap-1 ${
                myRank.ozgarish > 0 ? 'text-green-400' : myRank.ozgarish < 0 ? 'text-red-400' : 'text-slate-500'
              }`}>
                {myRank.ozgarish > 0 ? (
                  <HiOutlineChevronUp className="w-5 h-5" />
                ) : myRank.ozgarish < 0 ? (
                  <HiOutlineChevronDown className="w-5 h-5" />
                ) : (
                  <HiOutlineMinus className="w-5 h-5" />
                )}
                <span className="font-medium">{Math.abs(myRank.ozgarish || 0)}</span>
              </div>
              <p className="text-xs text-slate-500">bu hafta</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Top 3 Podium */}
      {!loading && leaderboard.length >= 3 && (
        <div className="hidden sm:flex items-end justify-center gap-4 py-8">
          {/* 2nd Place */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center"
          >
            <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-slate-300 to-slate-400 flex items-center justify-center text-3xl mb-3">
              {leaderboard[1]?.avatar_url ? (
                <img src={leaderboard[1].avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
              ) : (
                leaderboard[1]?.ism?.[0] || '?'
              )}
            </div>
            <p className="font-medium">{leaderboard[1]?.ism}</p>
            <p className="text-sm text-slate-500">{leaderboard[1]?.ball?.toLocaleString()} ball</p>
            <div className="mt-3 w-24 h-16 rounded-t-lg bg-gradient-to-b from-slate-400 to-slate-500 flex items-center justify-center">
              <span className="text-2xl">🥈</span>
            </div>
          </motion.div>

          {/* 1st Place */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-center"
          >
            <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center text-4xl mb-3 ring-4 ring-gold-400/30 shadow-lg shadow-gold-500/30">
              {leaderboard[0]?.avatar_url ? (
                <img src={leaderboard[0].avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
              ) : (
                leaderboard[0]?.ism?.[0] || '?'
              )}
            </div>
            <p className="font-display font-semibold text-lg">{leaderboard[0]?.ism}</p>
            <p className="text-sm text-gold-400">{leaderboard[0]?.ball?.toLocaleString()} ball</p>
            <div className="mt-3 w-28 h-24 rounded-t-lg bg-gradient-to-b from-gold-400 to-gold-600 flex items-center justify-center">
              <span className="text-3xl">🥇</span>
            </div>
          </motion.div>

          {/* 3rd Place */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-center"
          >
            <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center text-3xl mb-3">
              {leaderboard[2]?.avatar_url ? (
                <img src={leaderboard[2].avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
              ) : (
                leaderboard[2]?.ism?.[0] || '?'
              )}
            </div>
            <p className="font-medium">{leaderboard[2]?.ism}</p>
            <p className="text-sm text-slate-500">{leaderboard[2]?.ball?.toLocaleString()} ball</p>
            <div className="mt-3 w-24 h-12 rounded-t-lg bg-gradient-to-b from-orange-400 to-orange-600 flex items-center justify-center">
              <span className="text-2xl">🥉</span>
            </div>
          </motion.div>
        </div>
      )}

      {/* Full Leaderboard */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-white/5">
          <h3 className="font-display font-semibold">Barcha ishtirokchilar</h3>
        </div>

        {loading ? (
          <div className="p-6 space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-16 skeleton rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {leaderboard.map((item, index) => (
              <motion.div
                key={item.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`flex items-center gap-4 px-6 py-4 hover:bg-white/5 transition-colors ${
                  item.id === user?.id ? 'bg-med-500/10' : ''
                }`}
              >
                {/* Rank */}
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getRankStyle(index + 1)} flex items-center justify-center font-display font-bold`}>
                  {getRankIcon(index + 1) || index + 1}
                </div>

                {/* Avatar */}
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center">
                  {item.avatar_url ? (
                    <img src={item.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    <span className="font-display font-bold">{item.ism?.[0] || '?'}</span>
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">
                    {item.ism} {item.familiya}
                    {item.id === user?.id && (
                      <span className="ml-2 text-xs text-med-400">(Siz)</span>
                    )}
                  </p>
                  <p className="text-sm text-slate-500">Daraja {item.daraja || 1}</p>
                </div>

                {/* Stats */}
                <div className="text-right">
                  <p className="font-display font-bold text-lg">{item.ball?.toLocaleString()}</p>
                  <p className="text-xs text-slate-500">ball</p>
                </div>

                {/* Change indicator */}
                <div className={`w-8 flex items-center justify-center ${
                  item.ozgarish > 0 ? 'text-green-400' : item.ozgarish < 0 ? 'text-red-400' : 'text-slate-600'
                }`}>
                  {item.ozgarish > 0 ? (
                    <HiOutlineChevronUp className="w-5 h-5" />
                  ) : item.ozgarish < 0 ? (
                    <HiOutlineChevronDown className="w-5 h-5" />
                  ) : (
                    <HiOutlineMinus className="w-4 h-4" />
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
