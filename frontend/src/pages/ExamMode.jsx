import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { imtihonAPI, categoryAPI } from '../utils/api'
import toast from 'react-hot-toast'
import {
  HiOutlineClock,
  HiOutlinePlay,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineFlag,
  HiOutlineCheck,
  HiOutlineX,
  HiOutlineExclamation,
  HiOutlineDocumentText,
  HiOutlineAcademicCap,
  HiOutlineLightningBolt,
  HiOutlineChartBar,
  HiOutlineRefresh,
  HiOutlineHome,
  HiOutlineTrendingUp,
  HiOutlineTrendingDown
} from 'react-icons/hi'

const examTypes = [
  {
    value: 'amaliyot',
    label: 'Amaliyot',
    desc: 'Vaqt chegarasisiz mashq',
    icon: HiOutlineAcademicCap,
    color: 'from-emerald-500 to-teal-600'
  },
  {
    value: 'vaqtli',
    label: 'Vaqtli',
    desc: 'Umumiy vaqt chegarasi',
    icon: HiOutlineClock,
    color: 'from-blue-500 to-cyan-600'
  },
  {
    value: 'imtihon',
    label: 'Imtihon',
    desc: 'Har savol uchun vaqt',
    icon: HiOutlineLightningBolt,
    color: 'from-rose-500 to-pink-600'
  },
]

function formatTime(seconds) {
  if (!seconds || seconds < 0) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function ExamSetup({ onStart }) {
  const [examType, setExamType] = useState('vaqtli')
  const [questionCount, setQuestionCount] = useState(20)
  const [totalTime, setTotalTime] = useState(1800)
  const [questionTime, setQuestionTime] = useState(90)
  const [shuffle, setShuffle] = useState(true)
  const [allowBack, setAllowBack] = useState(true)
  const [starting, setStarting] = useState(false)

  const handleStart = async () => {
    setStarting(true)
    try {
      await onStart({
        turi: examType,
        savollar_soni: questionCount,
        umumiy_vaqt: totalTime,
        savol_vaqti: questionTime,
        aralashtirish: shuffle,
        orqaga_qaytish: allowBack
      })
    } finally {
      setStarting(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto"
    >
      <div className="text-center mb-8">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-rose-500 to-pink-600
                        flex items-center justify-center shadow-lg shadow-rose-500/25 mb-4">
          <HiOutlineDocumentText className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-display font-bold">Imtihon rejimi</h1>
        <p className="text-slate-400 mt-2">O'zingizni sinab ko'ring</p>
      </div>

      <div className="glass-card p-8">
        {/* Exam Type */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-slate-400 mb-4">Imtihon turi</label>
          <div className="grid grid-cols-3 gap-3">
            {examTypes.map((type) => (
              <button
                key={type.value}
                onClick={() => setExamType(type.value)}
                className={`p-4 rounded-xl border-2 transition-all duration-200 text-left
                           ${examType === type.value
                             ? `border-white/20 bg-gradient-to-br ${type.color} bg-opacity-10`
                             : 'border-white/5 bg-ocean-800/50 hover:border-white/10'}`}
              >
                <type.icon className={`w-6 h-6 mb-2 ${examType === type.value ? 'text-white' : 'text-slate-400'}`} />
                <div className={`font-semibold ${examType === type.value ? 'text-white' : 'text-slate-300'}`}>
                  {type.label}
                </div>
                <div className="text-xs text-slate-500 mt-1">{type.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Question Count */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-400 mb-3">
            Savollar soni: <span className="text-white">{questionCount}</span>
          </label>
          <input
            type="range"
            min="5"
            max="100"
            step="5"
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
            className="w-full h-2 rounded-full bg-ocean-700 appearance-none cursor-pointer
                       [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5
                       [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full
                       [&::-webkit-slider-thumb]:bg-med-500 [&::-webkit-slider-thumb]:shadow-lg"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>5</span>
            <span>100</span>
          </div>
        </div>

        {/* Time Settings */}
        {examType === 'vaqtli' && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-400 mb-3">
              Umumiy vaqt: <span className="text-white">{Math.floor(totalTime / 60)} daqiqa</span>
            </label>
            <input
              type="range"
              min="300"
              max="7200"
              step="300"
              value={totalTime}
              onChange={(e) => setTotalTime(Number(e.target.value))}
              className="w-full h-2 rounded-full bg-ocean-700 appearance-none cursor-pointer
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5
                         [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full
                         [&::-webkit-slider-thumb]:bg-blue-500 [&::-webkit-slider-thumb]:shadow-lg"
            />
          </div>
        )}

        {examType === 'imtihon' && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-400 mb-3">
              Har savol uchun: <span className="text-white">{questionTime} soniya</span>
            </label>
            <input
              type="range"
              min="30"
              max="300"
              step="15"
              value={questionTime}
              onChange={(e) => setQuestionTime(Number(e.target.value))}
              className="w-full h-2 rounded-full bg-ocean-700 appearance-none cursor-pointer
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5
                         [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full
                         [&::-webkit-slider-thumb]:bg-rose-500 [&::-webkit-slider-thumb]:shadow-lg"
            />
          </div>
        )}

        {/* Options */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <label className="flex items-center gap-3 p-4 rounded-xl bg-ocean-800/50 cursor-pointer">
            <input
              type="checkbox"
              checked={shuffle}
              onChange={(e) => setShuffle(e.target.checked)}
              className="w-5 h-5 rounded bg-ocean-700 border-white/10 text-med-500 focus:ring-med-500"
            />
            <div>
              <div className="font-medium text-white">Aralashtirish</div>
              <div className="text-xs text-slate-500">Savollar tartibini</div>
            </div>
          </label>

          <label className="flex items-center gap-3 p-4 rounded-xl bg-ocean-800/50 cursor-pointer">
            <input
              type="checkbox"
              checked={allowBack}
              onChange={(e) => setAllowBack(e.target.checked)}
              className="w-5 h-5 rounded bg-ocean-700 border-white/10 text-med-500 focus:ring-med-500"
            />
            <div>
              <div className="font-medium text-white">Orqaga qaytish</div>
              <div className="text-xs text-slate-500">Oldingi savollarga</div>
            </div>
          </label>
        </div>

        {/* Start Button */}
        <button
          onClick={handleStart}
          disabled={starting}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-rose-500 to-pink-600
                     text-white font-bold text-lg shadow-lg shadow-rose-500/25
                     hover:from-rose-400 hover:to-pink-500 transition-all duration-300
                     disabled:opacity-50 disabled:cursor-not-allowed
                     flex items-center justify-center gap-3"
        >
          {starting ? (
            <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <HiOutlinePlay className="w-6 h-6" />
              Imtihonni boshlash
            </>
          )}
        </button>
      </div>
    </motion.div>
  )
}

function ExamQuestion({ exam, question, onAnswer, onNext, onPrev, onGoTo, onFinish, onMark, loadingNext }) {
  const [selectedAnswer, setSelectedAnswer] = useState(question?.tanlangan_javob || null)
  const [timeLeft, setTimeLeft] = useState(question?.qolgan_vaqt || null)
  const timerRef = useRef(null)

  useEffect(() => {
    setSelectedAnswer(question?.tanlangan_javob || null)
    setTimeLeft(question?.qolgan_vaqt)
  }, [question])

  useEffect(() => {
    if (timeLeft === null || timeLeft === undefined) return

    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current)
          if (exam.turi === 'imtihon') {
            handleAnswer(null, true)
          }
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timerRef.current)
  }, [question?.savol_indeksi])

  const handleAnswer = async (answer, skip = false) => {
    await onAnswer({
      savol_indeksi: question.savol_indeksi,
      tanlangan_javob: answer,
      otkazish: skip,
      belgilangan: question.belgilangan
    })
  }

  const handleSelect = (answer) => {
    setSelectedAnswer(answer)
    handleAnswer(answer)
  }

  const isTimeCritical = timeLeft !== null && timeLeft < 30

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header with Timer */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <span className="text-slate-400">
            Savol {question.savol_indeksi + 1} / {exam.jami_savollar}
          </span>
          {question.belgilangan && (
            <span className="flex items-center gap-1 text-amber-400 text-sm">
              <HiOutlineFlag className="w-4 h-4" />
              Belgilangan
            </span>
          )}
        </div>

        {timeLeft !== null && (
          <div className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-lg
                          ${isTimeCritical
                            ? 'bg-red-500/20 text-red-400 animate-pulse'
                            : 'bg-ocean-700/50 text-white'}`}>
            <HiOutlineClock className="w-5 h-5" />
            {formatTime(timeLeft)}
          </div>
        )}
      </div>

      {/* Progress */}
      <div className="h-1.5 rounded-full bg-ocean-700 mb-8 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-med-500 to-med-400 rounded-full transition-all duration-300"
          style={{ width: `${((question.savol_indeksi + 1) / exam.jami_savollar) * 100}%` }}
        />
      </div>

      {/* Question Card */}
      <motion.div
        key={question.savol_indeksi}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass-card p-8"
      >
        {/* Difficulty */}
        <div className="flex items-center gap-3 mb-4">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            question.qiyinlik === 'oson' ? 'bg-green-500/20 text-green-400' :
            question.qiyinlik === 'ortacha' ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {question.qiyinlik?.toUpperCase()}
          </span>
        </div>

        {/* Scenario */}
        <div className="prose prose-invert max-w-none mb-6">
          <p className="text-slate-300 leading-relaxed whitespace-pre-line">
            {question.klinik_stsenariy}
          </p>
        </div>

        {/* Question */}
        <div className="p-4 bg-med-500/10 border border-med-500/20 rounded-xl mb-6">
          <p className="text-white font-medium">{question.savol}</p>
        </div>

        {/* Options */}
        <div className="space-y-3">
          {question.variantlar?.map((variant) => (
            <button
              key={variant.belgi}
              onClick={() => handleSelect(variant.belgi)}
              className={`w-full flex items-start gap-4 p-5 rounded-xl text-left transition-all duration-200
                         ${selectedAnswer === variant.belgi
                           ? 'bg-med-500/20 border-2 border-med-500 shadow-lg shadow-med-500/10'
                           : 'bg-ocean-800/50 border-2 border-transparent hover:border-white/10'}`}
            >
              <span className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold
                              ${selectedAnswer === variant.belgi
                                ? 'bg-med-500 text-white'
                                : 'bg-ocean-700 text-slate-400'}`}>
                {variant.belgi}
              </span>
              <span className={`flex-1 pt-2 ${selectedAnswer === variant.belgi ? 'text-white' : 'text-slate-300'}`}>
                {variant.matn}
              </span>
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/5">
          <div className="flex items-center gap-2">
            {exam.orqaga_qaytish && question.savol_indeksi > 0 && (
              <button
                onClick={onPrev}
                disabled={loadingNext}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-ocean-700/50
                           text-slate-300 hover:bg-ocean-700 transition-colors disabled:opacity-50"
              >
                <HiOutlineChevronLeft className="w-5 h-5" />
                Oldingi
              </button>
            )}

            <button
              onClick={() => onMark(!question.belgilangan)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-colors
                         ${question.belgilangan
                           ? 'bg-amber-500/20 text-amber-400'
                           : 'bg-ocean-700/50 text-slate-400 hover:text-amber-400'}`}
            >
              <HiOutlineFlag className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            {question.savol_indeksi < exam.jami_savollar - 1 ? (
              <button
                onClick={onNext}
                disabled={loadingNext}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-med-500
                           text-white font-medium hover:bg-med-400 transition-colors disabled:opacity-50"
              >
                {loadingNext ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    Keyingi
                    <HiOutlineChevronRight className="w-5 h-5" />
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={onFinish}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r
                           from-emerald-500 to-teal-500 text-white font-medium
                           hover:from-emerald-400 hover:to-teal-400 transition-all"
              >
                <HiOutlineCheck className="w-5 h-5" />
                Yakunlash
              </button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Question Navigator */}
      {exam.orqaga_qaytish && (
        <div className="mt-6 glass-card p-4">
          <div className="flex flex-wrap gap-2">
            {Array.from({ length: exam.jami_savollar }, (_, i) => (
              <button
                key={i}
                onClick={() => onGoTo(i)}
                className={`w-10 h-10 rounded-lg font-medium text-sm transition-all duration-200
                           ${i === question.savol_indeksi
                             ? 'bg-med-500 text-white'
                             : 'bg-ocean-700/50 text-slate-400 hover:bg-ocean-700'}`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ExamResult({ result, onRetry, onHome }) {
  const passed = result.otgan
  const percentage = result.ball_foizi || 0

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-2xl mx-auto"
    >
      <div className="glass-card p-8 text-center">
        {/* Result Icon */}
        <div className={`w-24 h-24 mx-auto rounded-3xl flex items-center justify-center mb-6
                        ${passed
                          ? 'bg-gradient-to-br from-emerald-500/20 to-teal-600/20 border border-emerald-500/20'
                          : 'bg-gradient-to-br from-red-500/20 to-rose-600/20 border border-red-500/20'}`}>
          {passed ? (
            <HiOutlineCheck className="w-12 h-12 text-emerald-400" />
          ) : (
            <HiOutlineX className="w-12 h-12 text-red-400" />
          )}
        </div>

        <h1 className={`text-3xl font-display font-bold mb-2 ${passed ? 'text-emerald-400' : 'text-red-400'}`}>
          {passed ? "Tabriklaymiz!" : "Qayta urinib ko'ring"}
        </h1>
        <p className="text-slate-400 mb-8">
          {passed ? "Imtihonni muvaffaqiyatli topshirdingiz" : "O'tish balliga yetmadingiz"}
        </p>

        {/* Score Circle */}
        <div className="relative w-40 h-40 mx-auto mb-8">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80" cy="80" r="70"
              className="fill-none stroke-ocean-700"
              strokeWidth="10"
            />
            <circle
              cx="80" cy="80" r="70"
              className={`fill-none ${passed ? 'stroke-emerald-500' : 'stroke-red-500'}`}
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={`${percentage * 4.4} 440`}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-display font-bold">{percentage}%</span>
            <span className="text-sm text-slate-500">ball</span>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <div className="text-2xl font-bold text-emerald-400">{result.togri_javoblar}</div>
            <div className="text-xs text-slate-500">To'g'ri</div>
          </div>
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
            <div className="text-2xl font-bold text-red-400">{result.notogri_javoblar}</div>
            <div className="text-xs text-slate-500">Noto'g'ri</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-500/10 border border-slate-500/20">
            <div className="text-2xl font-bold text-slate-400">{result.otkazilgan_savollar}</div>
            <div className="text-xs text-slate-500">O'tkazilgan</div>
          </div>
        </div>

        {/* Time */}
        <p className="text-sm text-slate-500 mb-8">
          Sarflangan vaqt: {formatTime(result.sarflangan_vaqt)}
        </p>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={onRetry}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl
                       bg-ocean-700/50 text-white font-medium hover:bg-ocean-700 transition-colors"
          >
            <HiOutlineRefresh className="w-5 h-5" />
            Qayta urinish
          </button>
          <button
            onClick={onHome}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl
                       bg-med-500 text-white font-medium hover:bg-med-400 transition-colors"
          >
            <HiOutlineHome className="w-5 h-5" />
            Boshqaruvga
          </button>
        </div>
      </div>
    </motion.div>
  )
}

export default function ExamMode() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [stage, setStage] = useState('setup') // setup, exam, result
  const [exam, setExam] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [changingQuestion, setChangingQuestion] = useState(false)

  const handleStart = async (config) => {
    setLoading(true)
    try {
      const response = await imtihonAPI.start(config)
      setExam(response.data)

      const questionRes = await imtihonAPI.getCurrentQuestion(response.data.id)
      setCurrentQuestion(questionRes.data)

      setStage('exam')
    } catch (error) {
      console.error('Error starting exam:', error)
      toast.error(error.response?.data?.detail || "Imtihonni boshlashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const handleAnswer = async (data) => {
    try {
      await imtihonAPI.submitAnswer(exam.id, data)
    } catch (error) {
      toast.error("Javobni saqlashda xatolik")
    }
  }

  const handleNext = async () => {
    if (changingQuestion) return
    setChangingQuestion(true)
    try {
      const response = await imtihonAPI.nextQuestion(exam.id)
      setCurrentQuestion(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setChangingQuestion(false)
    }
  }

  const handlePrev = async () => {
    if (changingQuestion) return
    setChangingQuestion(true)
    try {
      const response = await imtihonAPI.prevQuestion(exam.id)
      setCurrentQuestion(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setChangingQuestion(false)
    }
  }

  const handleGoTo = async (index) => {
    if (changingQuestion) return
    setChangingQuestion(true)
    try {
      const response = await imtihonAPI.goToQuestion(exam.id, index)
      setCurrentQuestion(response.data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setChangingQuestion(false)
    }
  }

  const handleMark = async (marked) => {
    try {
      await imtihonAPI.submitAnswer(exam.id, {
        savol_indeksi: currentQuestion.savol_indeksi,
        tanlangan_javob: currentQuestion.tanlangan_javob,
        belgilangan: marked,
        otkazish: false
      })
      setCurrentQuestion(prev => ({ ...prev, belgilangan: marked }))
    } catch (error) {
      console.error('Error:', error)
    }
  }

  const handleFinish = async () => {
    if (!confirm("Imtihonni yakunlashni xohlaysizmi?")) return

    try {
      const response = await imtihonAPI.finish(exam.id)
      setResult(response.data)
      setStage('result')
    } catch (error) {
      toast.error("Yakunlashda xatolik")
    }
  }

  const handleRetry = () => {
    setStage('setup')
    setExam(null)
    setCurrentQuestion(null)
    setResult(null)
  }

  const handleHome = () => {
    navigate('/boshqaruv')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-med-500/30 border-t-med-500 rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-slate-400">Imtihon tayyorlanmoqda...</p>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="py-4"
    >
      <AnimatePresence mode="wait">
        {stage === 'setup' && (
          <ExamSetup key="setup" onStart={handleStart} />
        )}

        {stage === 'exam' && exam && currentQuestion && (
          <ExamQuestion
            key="exam"
            exam={exam}
            question={currentQuestion}
            onAnswer={handleAnswer}
            onNext={handleNext}
            onPrev={handlePrev}
            onGoTo={handleGoTo}
            onMark={handleMark}
            onFinish={handleFinish}
            loadingNext={changingQuestion}
          />
        )}

        {stage === 'result' && result && (
          <ExamResult
            key="result"
            result={result}
            onRetry={handleRetry}
            onHome={handleHome}
          />
        )}
      </AnimatePresence>
    </motion.div>
  )
}
