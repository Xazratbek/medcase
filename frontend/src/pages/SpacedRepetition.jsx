import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { takrorlashAPI, caseAPI } from '../utils/api'
import toast from 'react-hot-toast'
import {
  HiOutlineRefresh,
  HiOutlineLightningBolt,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineChartBar,
  HiOutlineClock,
  HiOutlineEye,
  HiOutlineArrowRight,
  HiOutlineSparkles,
  HiOutlineAcademicCap,
  HiOutlineCalendar,
  HiOutlineFire
} from 'react-icons/hi'

const qualityButtons = [
  { value: 0, label: 'Bilmayman', color: 'from-red-600 to-red-500', desc: "To'liq unutdim", interval: 'Ertaga' },
  { value: 1, label: 'Qiyin', color: 'from-orange-600 to-orange-500', desc: "Ko'rganimda esladim", interval: 'Ertaga' },
  { value: 2, label: "O'rtacha", color: 'from-amber-600 to-amber-500', desc: 'Qiyin lekin bildim', interval: 'Ertaga' },
  { value: 3, label: 'Yaxshi', color: 'from-lime-600 to-lime-500', desc: "Biroz o'ylab topdim", interval: '~4 kun' },
  { value: 4, label: "A'lo", color: 'from-emerald-600 to-emerald-500', desc: 'Osonlik bilan', interval: '~1 hafta' },
  { value: 5, label: 'Mukammal', color: 'from-cyan-600 to-cyan-500', desc: "Hech o'ylamasdan", interval: '~2 hafta' },
]

function StatCard({ icon: Icon, label, value, color, subtext }) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="glass-card p-5 relative overflow-hidden group"
    >
      <div className={`absolute -right-4 -top-4 w-20 h-20 rounded-full ${color} opacity-10 
                      group-hover:opacity-20 transition-opacity blur-xl`} />
      <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center shadow-lg`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div className="mt-4">
        <div className="text-2xl font-display font-bold">{value}</div>
        <div className="text-sm text-slate-500 mt-0.5">{label}</div>
        {subtext && <div className="text-xs text-slate-600 mt-1">{subtext}</div>}
      </div>
    </motion.div>
  )
}

function ReviewCard({ card, onRate, caseData, showAnswer, onShowAnswer }) {
  const [selectedQuality, setSelectedQuality] = useState(null)
  const [rating, setRating] = useState(false)

  const handleRate = async (quality) => {
    if (rating) return
    setSelectedQuality(quality)
    setRating(true)
    try {
      await onRate(quality)
    } finally {
      setRating(false)
      setSelectedQuality(null)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="glass-card overflow-hidden"
    >
      {/* Card Header */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
              card.repetition === 0 
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
                : 'bg-med-500/20 text-med-400 border border-med-500/30'
            }`}>
              {card.repetition === 0 ? 'Yangi' : `${card.repetition} marta takrorlangan`}
            </div>
            {card.kategoriya_nomi && (
              <span className="text-sm text-slate-500">{card.kategoriya_nomi}</span>
            )}
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <HiOutlineFire className="w-4 h-4 text-orange-400" />
            <span>{Math.round(card.aniqlik_foizi || 0)}% aniqlik</span>
          </div>
        </div>

        <h3 className="text-xl font-display font-semibold text-white">
          {caseData?.sarlavha || card.holat_sarlavhasi || 'Klinik holat'}
        </h3>
      </div>

      {/* Question */}
      <div className="p-6">
        <div className="prose prose-invert max-w-none">
          <p className="text-slate-300 leading-relaxed whitespace-pre-line">
            {caseData?.klinik_stsenariy || 'Yuklanmoqda...'}
          </p>
          
          {caseData?.savol && (
            <div className="mt-6 p-4 bg-med-500/10 border border-med-500/20 rounded-xl">
              <p className="text-white font-medium">{caseData.savol}</p>
            </div>
          )}
        </div>

        {/* Answer Section */}
        <AnimatePresence mode="wait">
          {!showAnswer ? (
            <motion.div
              key="show-btn"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mt-8"
            >
              <button
                onClick={onShowAnswer}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 
                           text-white font-semibold text-lg shadow-lg shadow-violet-500/25
                           hover:from-violet-500 hover:to-purple-500 transition-all duration-300
                           flex items-center justify-center gap-3"
              >
                <HiOutlineEye className="w-6 h-6" />
                Javobni ko'rsatish
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="answer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8"
            >
              {/* Correct Answer */}
              {caseData?.variantlar && (
                <div className="mb-6 p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                  <div className="flex items-center gap-2 mb-3">
                    <HiOutlineCheckCircle className="w-5 h-5 text-emerald-400" />
                    <span className="font-semibold text-emerald-400">To'g'ri javob</span>
                  </div>
                  <p className="text-white">
                    {caseData.togri_javob}: {caseData.variantlar.find(v => v.belgi === caseData.togri_javob)?.matn}
                  </p>
                </div>
              )}

              {/* Explanation */}
              {caseData?.tushuntirish && (
                <div className="mb-6 p-5 rounded-2xl bg-ocean-700/50 border border-white/5">
                  <h4 className="font-semibold text-white mb-2">Tushuntirish</h4>
                  <p className="text-slate-300 whitespace-pre-line">{caseData.tushuntirish}</p>
                </div>
              )}

              {/* Rating Buttons */}
              <div className="mt-8">
                <p className="text-center text-slate-400 mb-4">Qanchalik yaxshi esladingiz?</p>
                <div className="grid grid-cols-3 lg:grid-cols-6 gap-2">
                  {qualityButtons.map((btn) => (
                    <motion.button
                      key={btn.value}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleRate(btn.value)}
                      disabled={rating}
                      title={`${btn.desc} - Keyingi: ${btn.interval}`}
                      className={`p-3 rounded-xl bg-gradient-to-br ${btn.color} 
                                 text-white font-medium text-sm shadow-lg
                                 hover:shadow-xl transition-all duration-200
                                 disabled:opacity-50 disabled:cursor-not-allowed
                                 relative group
                                 ${selectedQuality === btn.value ? 'ring-2 ring-white' : ''}`}
                    >
                      <div className="text-lg font-bold">{btn.value}</div>
                      <div className="text-xs opacity-90">{btn.label}</div>
                      {/* Tooltip */}
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 
                                      bg-ocean-800 border border-white/10 rounded-lg shadow-xl
                                      opacity-0 invisible group-hover:opacity-100 group-hover:visible
                                      transition-all duration-200 whitespace-nowrap z-10 pointer-events-none">
                        <p className="text-xs text-white font-medium">{btn.desc}</p>
                        <p className="text-xs text-slate-400 mt-0.5">Keyingi: {btn.interval}</p>
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 
                                        border-4 border-transparent border-t-ocean-800" />
                      </div>
                    </motion.button>
                  ))}
                </div>
                <p className="text-center text-xs text-slate-500 mt-3">
                  Tugmalar ustiga kursor olib boring - tushuntirish ko'rsatiladi
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

function EmptyState({ stats }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-12 text-center"
    >
      <div className="w-24 h-24 mx-auto rounded-3xl bg-gradient-to-br from-emerald-500/20 to-teal-600/20 
                      flex items-center justify-center mb-6 border border-emerald-500/20">
        <HiOutlineSparkles className="w-12 h-12 text-emerald-400" />
      </div>
      <h2 className="text-2xl font-display font-bold mb-2">Ajoyib!</h2>
      <p className="text-slate-400 mb-6">
        Bugungi barcha kartalarni takrorladingiz
      </p>
      
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link
          to="/holatlar"
          className="btn-primary flex items-center justify-center gap-2"
        >
          <HiOutlineAcademicCap className="w-5 h-5" />
          Yangi holatlar o'rganish
        </Link>
        <Link
          to="/boshqaruv"
          className="btn-secondary flex items-center justify-center gap-2"
        >
          Boshqaruvga qaytish
        </Link>
      </div>
    </motion.div>
  )
}

export default function SpacedRepetition() {
  const [cards, setCards] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showAnswer, setShowAnswer] = useState(false)
  const [currentCaseData, setCurrentCaseData] = useState(null)
  const [completed, setCompleted] = useState(0)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [cardsRes, statsRes] = await Promise.all([
        takrorlashAPI.getToday({ limit: 100 }),
        takrorlashAPI.getStats()
      ])
      
      setCards(cardsRes.data.kartalar || [])
      setStats(statsRes.data)
      
      if (cardsRes.data.kartalar?.length > 0) {
        loadCaseData(cardsRes.data.kartalar[0].holat_id)
      }
    } catch (error) {
      console.error('Error loading data:', error)
      toast.error("Ma'lumotlarni yuklashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const loadCaseData = async (holatId) => {
    try {
      const response = await caseAPI.getById(holatId)
      setCurrentCaseData(response.data)
    } catch (error) {
      console.error('Error loading case:', error)
    }
  }

  const handleRate = async (quality) => {
    const currentCard = cards[currentIndex]
    
    try {
      await takrorlashAPI.rate(currentCard.holat_id, { sifat: quality })
      
      setCompleted(prev => prev + 1)
      
      if (currentIndex < cards.length - 1) {
        setCurrentIndex(prev => prev + 1)
        setShowAnswer(false)
        setCurrentCaseData(null)
        loadCaseData(cards[currentIndex + 1].holat_id)
      } else {
        setCards([])
      }
      
      if (quality >= 3) {
        toast.success("Yaxshi! Keyingi takrorlash belgilandi", { icon: '🎯' })
      }
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const currentCard = cards[currentIndex]
  const progress = cards.length > 0 ? ((currentIndex + completed) / (cards.length + completed)) * 100 : 0

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-12 skeleton rounded-2xl w-64" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-32 skeleton rounded-2xl" />)}
        </div>
        <div className="h-96 skeleton rounded-2xl" />
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
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 
                          flex items-center justify-center shadow-lg shadow-violet-500/25">
            <HiOutlineRefresh className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl lg:text-3xl font-display font-bold">Takrorlash</h1>
            <p className="text-slate-400">SM-2 algoritmi bilan samarali o'rganish</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={HiOutlineLightningBolt}
          label="Bugungi"
          value={cards.length + completed}
          color="from-amber-500 to-orange-600"
          subtext={`${completed} bajarildi`}
        />
        <StatCard
          icon={HiOutlineCheckCircle}
          label="Jami kartalar"
          value={stats?.jami_kartalar || 0}
          color="from-emerald-500 to-teal-600"
        />
        <StatCard
          icon={HiOutlineChartBar}
          label="O'rtacha aniqlik"
          value={`${Math.round(stats?.ortacha_aniqlik || 0)}%`}
          color="from-blue-500 to-cyan-600"
        />
        <StatCard
          icon={HiOutlineCalendar}
          label="Streak"
          value={`${stats?.takrorlash_kunlari || 0} kun`}
          color="from-rose-500 to-pink-600"
        />
      </div>

      {/* Progress Bar */}
      {cards.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
            <span>Bugungi jarayon</span>
            <span>{currentIndex + 1} / {cards.length + completed}</span>
          </div>
          <div className="h-2 rounded-full bg-ocean-700 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full"
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <AnimatePresence mode="wait">
        {cards.length === 0 ? (
          <EmptyState key="empty" stats={stats} />
        ) : currentCard ? (
          <ReviewCard
            key={currentCard.id}
            card={currentCard}
            caseData={currentCaseData}
            showAnswer={showAnswer}
            onShowAnswer={() => setShowAnswer(true)}
            onRate={handleRate}
          />
        ) : null}
      </AnimatePresence>

      {/* Tips */}
      {cards.length > 0 && (
        <div className="mt-8 p-4 rounded-2xl bg-ocean-800/30 border border-white/5">
          <h4 className="text-sm font-medium text-slate-400 mb-2">SM-2 Algoritmi haqida</h4>
          <p className="text-xs text-slate-500">
            Baholash sifatiga qarab keyingi takrorlash vaqti belgilanadi. 
            Qanchalik yaxshi eslasangiz, interval shunchalik uzoq bo'ladi. 
            0-2 ball = ertaga takrorlash, 3-5 ball = kunlar/haftalarga cho'ziladi.
          </p>
        </div>
      )}
    </motion.div>
  )
}
