import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { gamificationAPI } from '../utils/api'
import {
  HiOutlineStar,
  HiOutlineLockClosed,
  HiOutlineSparkles
} from 'react-icons/hi'

const rarityColors = {
  ODDIY: { bg: 'from-slate-500/20 to-slate-600/20', border: 'border-slate-500/30', text: 'text-slate-400', label: 'Oddiy' },
  NOYOB: { bg: 'from-blue-500/20 to-blue-600/20', border: 'border-blue-500/30', text: 'text-blue-400', label: 'Noyob' },
  EPIK: { bg: 'from-purple-500/20 to-purple-600/20', border: 'border-purple-500/30', text: 'text-purple-400', label: 'Epik' },
  AFSONAVIY: { bg: 'from-gold-400/20 to-amber-500/20', border: 'border-gold-500/30', text: 'text-gold-400', label: 'Afsonaviy' },
}

const categoryIcons = {
  'Bosqich': '🎯',
  'Ustunlik': '🏆',
  'Aniqlik': '🎯',
  'Tezlik': '⚡',
  'Streak': '🔥',
  'Tadqiqotchi': '🔬',
  'Mukammal': '💎',
  'Sodiqlik': '❤️',
  'default': '⭐'
}

export default function Achievements() {
  const [allAchievements, setAllAchievements] = useState([])
  const [myAchievements, setMyAchievements] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, earned, locked
  const [selectedRarity, setSelectedRarity] = useState('')

  useEffect(() => {
    loadAchievements()
  }, [])

  const loadAchievements = async () => {
    try {
      const [allRes, myRes] = await Promise.all([
        gamificationAPI.getAchievements(),
        gamificationAPI.getMyAchievements()
      ])
      setAllAchievements(allRes.data.malumot || [])
      setMyAchievements(myRes.data.malumot || [])
    } catch (error) {
      console.error('Achievements loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  const isEarned = (achievementId) => {
    return myAchievements.some(a => a.nishon_id === achievementId || a.id === achievementId)
  }

  const getEarnedDate = (achievementId) => {
    const earned = myAchievements.find(a => a.nishon_id === achievementId || a.id === achievementId)
    return earned?.olingan_vaqt
  }

  const filteredAchievements = allAchievements.filter(a => {
    const earned = isEarned(a.id)
    if (filter === 'earned' && !earned) return false
    if (filter === 'locked' && earned) return false
    if (selectedRarity && a.nodirlik !== selectedRarity) return false
    return true
  })

  const earnedCount = allAchievements.filter(a => isEarned(a.id)).length
  const totalPoints = myAchievements.reduce((sum, a) => sum + (a.ball || 0), 0)

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-12 skeleton rounded-xl w-48" />
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <div key={i} className="h-48 skeleton rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 lg:space-y-8"
    >
      {/* Header */}
      <div>
        <h1 className="text-2xl lg:text-3xl font-display font-bold flex items-center gap-3">
          <HiOutlineStar className="w-8 h-8 text-gold-400" />
          Yutuqlar
        </h1>
        <p className="text-slate-400 mt-1">Nishonlar va mukofotlar</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass-card p-5 text-center">
          <div className="text-3xl font-display font-bold text-gradient">{earnedCount}</div>
          <div className="text-sm text-slate-500 mt-1">Olingan</div>
        </div>
        <div className="glass-card p-5 text-center">
          <div className="text-3xl font-display font-bold">{allAchievements.length}</div>
          <div className="text-sm text-slate-500 mt-1">Jami</div>
        </div>
        <div className="glass-card p-5 text-center">
          <div className="text-3xl font-display font-bold text-gradient-gold">{totalPoints}</div>
          <div className="text-sm text-slate-500 mt-1">Ball</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Status filter */}
        <div className="flex items-center gap-2 p-1 rounded-xl bg-ocean-800/50">
          {[
            { value: 'all', label: 'Barchasi' },
            { value: 'earned', label: 'Olingan' },
            { value: 'locked', label: 'Qulflangan' }
          ].map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === f.value
                  ? 'bg-med-500 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Rarity filter */}
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setSelectedRarity('')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              !selectedRarity ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-white'
            }`}
          >
            Barchasi
          </button>
          {Object.entries(rarityColors).map(([key, value]) => (
            <button
              key={key}
              onClick={() => setSelectedRarity(key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${value.border} border ${
                selectedRarity === key ? `bg-gradient-to-r ${value.bg} ${value.text}` : 'text-slate-500 hover:text-white'
              }`}
            >
              {value.label}
            </button>
          ))}
        </div>
      </div>

      {/* Achievements Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {filteredAchievements.map((achievement, index) => {
          const earned = isEarned(achievement.id)
          const rarity = rarityColors[achievement.nodirlik] || rarityColors.ODDIY
          const earnedDate = getEarnedDate(achievement.id)
          const icon = categoryIcons[achievement.turi] || categoryIcons.default

          return (
            <motion.div
              key={achievement.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.03 }}
              className={`
                relative p-5 rounded-2xl border transition-all duration-300
                ${earned 
                  ? `bg-gradient-to-br ${rarity.bg} ${rarity.border} hover:shadow-lg` 
                  : 'bg-ocean-800/30 border-white/5 opacity-60 hover:opacity-80'
                }
              `}
            >
              {/* Rarity indicator */}
              {earned && achievement.nodirlik === 'AFSONAVIY' && (
                <div className="absolute -top-1 -right-1">
                  <HiOutlineSparkles className="w-5 h-5 text-gold-400 animate-pulse" />
                </div>
              )}

              {/* Icon */}
              <div className={`
                w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-3xl
                ${earned ? `bg-gradient-to-br ${rarity.bg}` : 'bg-ocean-700/50'}
              `}>
                {earned ? icon : <HiOutlineLockClosed className="w-8 h-8 text-slate-600" />}
              </div>

              {/* Name */}
              <h3 className={`mt-4 text-center font-display font-semibold ${earned ? '' : 'text-slate-500'}`}>
                {achievement.nomi}
              </h3>

              {/* Description */}
              <p className="mt-2 text-xs text-center text-slate-500 line-clamp-2">
                {achievement.tavsif}
              </p>

              {/* Points */}
              <div className={`mt-3 text-center text-sm font-medium ${rarity.text}`}>
                +{achievement.ball} ball
              </div>

              {/* Earned date */}
              {earned && earnedDate && (
                <div className="mt-2 text-center text-xs text-slate-500">
                  {new Date(earnedDate).toLocaleDateString('uz-UZ')}
                </div>
              )}

              {/* Progress for locked achievements */}
              {!earned && achievement.kerakli_qiymat && (
                <div className="mt-3">
                  <div className="progress-bar h-1.5">
                    <div 
                      className="progress-bar-fill"
                      style={{ width: `${Math.min((achievement.joriy_qiymat / achievement.kerakli_qiymat) * 100, 100)}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-center text-slate-500">
                    {achievement.joriy_qiymat || 0} / {achievement.kerakli_qiymat}
                  </p>
                </div>
              )}
            </motion.div>
          )
        })}
      </div>

      {filteredAchievements.length === 0 && (
        <div className="text-center py-16">
          <div className="w-20 h-20 mx-auto rounded-full bg-ocean-800 flex items-center justify-center">
            <HiOutlineStar className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="mt-4 text-lg font-medium">Nishonlar topilmadi</h3>
          <p className="mt-2 text-slate-500">Filterlarni o'zgartiring</p>
        </div>
      )}
    </motion.div>
  )
}
