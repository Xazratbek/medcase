import { useState, useEffect, useRef } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { caseAPI, takrorlashAPI } from '../utils/api'
import {
  HiOutlineArrowLeft,
  HiOutlineClock,
  HiOutlineBookmark,
  HiOutlineCheck,
  HiOutlineX,
  HiOutlineArrowRight,
  HiOutlineLightBulb,
  HiOutlineRefresh,
  HiOutlinePlus
} from 'react-icons/hi'
import toast from 'react-hot-toast'
import confetti from 'canvas-confetti'

export default function CaseSolve() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState(null)
  const [timer, setTimer] = useState(0)
  const [showExplanation, setShowExplanation] = useState(false)
  const [addingToRepeat, setAddingToRepeat] = useState(false)
  const [addedToRepeat, setAddedToRepeat] = useState(false)
  const timerRef = useRef(null)

  useEffect(() => {
    loadCase()
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [id])

  useEffect(() => {
    // Timer faqat case yuklanganda va javob yuborilmaganida ishlaydi
    if (caseData && !submitted) {
      // Avvalgi intervalni tozalash
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }

      // Yangi interval - aniq 1000ms (1 soniya)
      const intervalId = setInterval(() => {
        setTimer(prev => prev + 1)
      }, 1000)

      timerRef.current = intervalId

      return () => {
        clearInterval(intervalId)
        timerRef.current = null
      }
    }
  }, [caseData?.id, submitted]) // caseData.id ga o'zgartirdik - faqat yangi case yuklanganda

  const loadCase = async () => {
    try {
      const response = await caseAPI.getById(id)
      // API returns HolatJavob directly
      setCaseData(response.data.malumot || response.data)
    } catch (error) {
      console.error('Case loading error:', error)
      toast.error("Holatni yuklashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!selectedAnswer) {
      toast.error("Iltimos, javobni tanlang")
      return
    }

    if (submitting) return

    setSubmitting(true)
    if (timerRef.current) clearInterval(timerRef.current)

    try {
      const response = await caseAPI.submitAnswer(id, selectedAnswer, timer)
      // API returns UrinishJavob directly
      const resultData = response.data.malumot || response.data
      setResult(resultData)
      setSubmitted(true)

      if (resultData?.togri) {
        // Confetti for correct answer
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#14b89c', '#2dd4b3', '#fbbf24']
        })
        toast.success("To'g'ri javob! 🎉")
      } else {
        toast.error("Noto'g'ri javob")
      }
    } catch (error) {
      toast.error("Javobni yuborishda xatolik")
      if (timerRef.current) {
        timerRef.current = setInterval(() => setTimer(prev => prev + 1), 1000)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const handleNextCase = async () => {
    try {
      // Tasodifiy keyingi holatni olish (xuddi shu bo'limdan yoki umumiy)
      const params = { soni: 1 }
      if (caseData?.bolim_id) {
        params.bolim_id = caseData.bolim_id
      }

      const response = await caseAPI.getRandomCases(params)
      const cases = response.data?.holatlar || response.data || []
      const nextCase = cases[0]

      if (nextCase && nextCase.id !== id) {
        // Yangi holatga o'tish
        navigate(`/holat/${nextCase.id}`)
      } else {
        // Agar tasodifiy holat topilmasa yoki xuddi shu holat bo'lsa
        // Umumiy tasodifiy holatni olish (bo'limsiz)
        const randomResponse = await caseAPI.getRandomCases({ soni: 1 })
        const randomCases = randomResponse.data?.holatlar || randomResponse.data || []
        const randomCase = randomCases[0]

        if (randomCase && randomCase.id !== id) {
          navigate(`/holat/${randomCase.id}`)
        } else {
          toast.info("Boshqa holatlar mavjud emas")
          navigate('/holatlar')
        }
      }
    } catch (error) {
      console.error('Next case error:', error)
      toast.error("Keyingi holatni yuklashda xatolik")
      navigate('/holatlar')
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleAddToRepeat = async () => {
    if (addedToRepeat || addingToRepeat) return
    setAddingToRepeat(true)
    try {
      await takrorlashAPI.addCase(id)
      setAddedToRepeat(true)
      toast.success("Takrorlash kartasiga qo'shildi", { icon: '🔄' })
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    } finally {
      setAddingToRepeat(false)
    }
  }

  const getOptionStyle = (option) => {
    if (!submitted) {
      return selectedAnswer === option
        ? 'border-med-500 bg-med-500/10'
        : 'border-transparent hover:border-med-500/30 hover:bg-ocean-700/50'
    }

    if (option === result?.togri_javob) {
      return 'border-green-500 bg-green-500/10'
    }
    if (option === selectedAnswer && option !== result?.togri_javob) {
      return 'border-red-500 bg-red-500/10'
    }
    return 'border-transparent opacity-50'
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-8 skeleton rounded w-32" />
        <div className="h-48 skeleton rounded-2xl" />
        <div className="space-y-3">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-20 skeleton rounded-xl" />)}
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-medium">Holat topilmadi</h2>
        <Link to="/holatlar" className="btn-primary mt-4 inline-flex">
          Holatlarga qaytish
        </Link>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto"
    >
      {/* Top bar */}
      <div className="flex items-center justify-between mb-6">
        <Link
          to="/holatlar"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <HiOutlineArrowLeft className="w-5 h-5" />
          <span className="hidden sm:inline">Holatlarga qaytish</span>
        </Link>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-ocean-800/80 border border-white/5">
            <HiOutlineClock className="w-5 h-5 text-slate-400" />
            <span className="font-mono text-lg">{formatTime(timer)}</span>
          </div>
        </div>
      </div>

      {/* Case content */}
      <div className="glass-card p-6 lg:p-8 mb-6">
        {/* Scenario */}
        <div className="prose prose-invert max-w-none">
          <p className="text-slate-300 leading-relaxed whitespace-pre-line">
            {caseData.klinik_stsenariy || caseData.ssenariy}
          </p>
        </div>

        {/* Media */}
        {caseData.media && caseData.media.length > 0 && (
          <div className="mt-6 grid grid-cols-2 gap-4">
            {caseData.media.map((item, index) => (
              <div key={index} className="aspect-video rounded-xl overflow-hidden bg-ocean-800">
                <img src={item.url} alt="" className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        )}

        {/* Question */}
        <div className="mt-8 p-4 rounded-xl bg-med-500/10 border border-med-500/20">
          <h3 className="font-display font-semibold text-lg text-med-400">
            {caseData.savol}
          </h3>
        </div>
      </div>

      {/* Answer options */}
      <div className="space-y-3 mb-6">
        {caseData.variantlar?.map((variant, index) => {
          const letter = String.fromCharCode(65 + index) // A, B, C, D
          return (
            <motion.button
              key={variant.id || index}
              onClick={() => !submitted && setSelectedAnswer(letter)}
              disabled={submitted}
              className={`answer-option w-full text-left border-2 transition-all ${getOptionStyle(letter)}`}
              whileHover={!submitted ? { scale: 1.01 } : {}}
              whileTap={!submitted ? { scale: 0.99 } : {}}
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-display font-bold ${
                submitted && letter === result?.togri_javob
                  ? 'bg-green-500 text-white'
                  : submitted && letter === selectedAnswer && letter !== result?.togri_javob
                  ? 'bg-red-500 text-white'
                  : selectedAnswer === letter
                  ? 'bg-med-500 text-white'
                  : 'bg-ocean-700 text-slate-400'
              }`}>
                {submitted && letter === result?.togri_javob ? (
                  <HiOutlineCheck className="w-5 h-5" />
                ) : submitted && letter === selectedAnswer && letter !== result?.togri_javob ? (
                  <HiOutlineX className="w-5 h-5" />
                ) : (
                  letter
                )}
              </div>
              <div className="flex-1">
                <p className="font-medium">{variant.matn}</p>
              </div>
            </motion.button>
          )
        })}
      </div>

      {/* Submit / Result section */}
      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={!selectedAnswer || submitting}
          className="btn-primary w-full py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {submitting ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Yuborilmoqda...
            </>
          ) : (
            "Javobni yuborish"
          )}
        </button>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Result card */}
          <div className={`glass-card p-6 border-2 ${
            result?.togri ? 'border-green-500/50' : 'border-red-500/50'
          }`}>
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                result?.togri ? 'bg-green-500/20' : 'bg-red-500/20'
              }`}>
                {result?.togri ? (
                  <HiOutlineCheck className="w-8 h-8 text-green-400" />
                ) : (
                  <HiOutlineX className="w-8 h-8 text-red-400" />
                )}
              </div>
              <div>
                <h3 className={`text-xl font-display font-bold ${
                  result?.togri ? 'text-green-400' : 'text-red-400'
                }`}>
                  {result?.togri ? "To'g'ri javob!" : "Noto'g'ri javob"}
                </h3>
                <p className="text-slate-400 mt-1">
                  Vaqt: {formatTime(timer)} | +{result?.olingan_ball || result?.ball || 0} ball
                </p>
              </div>
            </div>
          </div>

          {/* Explanation toggle */}
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="w-full flex items-center justify-between p-4 rounded-xl bg-ocean-800/50 border border-white/5 hover:bg-ocean-700/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <HiOutlineLightBulb className="w-5 h-5 text-gold-400" />
              <span className="font-medium">Tushuntirishni ko'rish</span>
            </div>
            <motion.div
              animate={{ rotate: showExplanation ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <HiOutlineArrowRight className="w-5 h-5 transform rotate-90" />
            </motion.div>
          </button>

          {/* Explanation content */}
          <AnimatePresence>
            {showExplanation && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="glass-card p-6 overflow-hidden"
              >
                <h4 className="font-display font-semibold mb-4">Tushuntirish</h4>

                {/* User's wrong answer explanation (if wrong) */}
                {!result?.togri && selectedAnswer !== result?.togri_javob && (
                  <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 mb-4">
                    <p className="text-sm text-red-400 font-medium mb-2">
                      Sizning javobingiz: {selectedAnswer} - Noto'g'ri
                    </p>
                    <p className="text-slate-300">
                      {caseData.variantlar?.find((v, i) =>
                        String.fromCharCode(65 + i) === selectedAnswer
                      )?.tushuntirish || "Tushuntirish mavjud emas"}
                    </p>
                  </div>
                )}

                {/* Correct answer explanation */}
                <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                  <p className="text-sm text-green-400 font-medium mb-2">
                    To'g'ri javob: {result?.togri_javob}
                  </p>
                  <p className="text-slate-300">
                    {caseData.variantlar?.find((v, i) =>
                      String.fromCharCode(65 + i) === result?.togri_javob
                    )?.tushuntirish || result?.tushuntirish || "Tushuntirish mavjud emas"}
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Add to Spaced Repetition */}
          <motion.button
            onClick={handleAddToRepeat}
            disabled={addingToRepeat || addedToRepeat}
            whileHover={{ scale: addedToRepeat ? 1 : 1.01 }}
            whileTap={{ scale: addedToRepeat ? 1 : 0.99 }}
            className={`w-full p-4 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 ${
              addedToRepeat
                ? 'bg-violet-500/20 border border-violet-500/30 text-violet-400 cursor-default'
                : 'bg-gradient-to-r from-violet-600/20 to-purple-600/20 border border-violet-500/20 text-violet-300 hover:border-violet-500/40 hover:shadow-lg hover:shadow-violet-500/10'
            }`}
          >
            {addingToRepeat ? (
              <div className="w-5 h-5 border-2 border-violet-400/30 border-t-violet-400 rounded-full animate-spin" />
            ) : addedToRepeat ? (
              <>
                <HiOutlineCheck className="w-5 h-5" />
                <span className="font-medium">Takrorlash kartasiga qo'shildi</span>
              </>
            ) : (
              <>
                <HiOutlinePlus className="w-5 h-5" />
                <span className="font-medium">Takrorlash kartasiga qo'shish</span>
                <span className="text-xs text-violet-400/70 hidden sm:inline">(SM-2 algoritmi)</span>
              </>
            )}
          </motion.button>

          {/* Actions */}
          <div className="flex gap-4">
            <Link to="/holatlar" className="btn-secondary flex-1 py-4 flex items-center justify-center gap-2">
              <HiOutlineArrowLeft className="w-5 h-5" />
              Holatlarga qaytish
            </Link>
            <button
              onClick={handleNextCase}
              className="btn-primary flex-1 py-4 flex items-center justify-center gap-2"
            >
              Keyingi holat
              <HiOutlineArrowRight className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
