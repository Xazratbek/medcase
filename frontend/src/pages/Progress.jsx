import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { progressAPI } from '../utils/api'
import {
  HiOutlineChartBar,
  HiOutlineTrendingUp,
  HiOutlineClock,
  HiOutlineCalendar,
  HiOutlineAcademicCap,
  HiOutlineFire
} from 'react-icons/hi'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

export default function Progress() {
  const [stats, setStats] = useState(null)
  const [history, setHistory] = useState([])
  const [categoryStats, setCategoryStats] = useState([])
  const [calendarData, setCalendarData] = useState([])
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState('hafta') // hafta, oy, yil

  useEffect(() => {
    loadData()
  }, [period])

  const loadData = async () => {
    try {
      // Davr bo'yicha kunlar soni
      const kunlarMap = { hafta: 7, oy: 30, yil: 365 }
      const kunlar = kunlarMap[period] || 7
      
      const [statsRes, historyRes, categoryRes, calendarRes] = await Promise.all([
        progressAPI.getOverview(),
        progressAPI.getDailyStats({ kunlar }),
        progressAPI.getCategoryStats(),
        progressAPI.getDailyStats({ kunlar: 35 }) // Kalendar uchun 35 kun
      ])
      
      // Stats - rivojlanish ma'lumotlari
      const statsData = statsRes.data
      setStats({
        jami_holatlar: statsData.jami_urinishlar || 0,
        bu_hafta_holatlar: statsData.jami_urinishlar || 0, // Hisoblash kerak
        aniqlik: statsData.aniqlik_foizi || 0,
        streak: statsData.joriy_streak || 0,
        eng_uzun_streak: statsData.eng_uzun_streak || 0,
        daraja: statsData.daraja || 1,
        jami_ball: statsData.jami_ball || 0,
        jami_vaqt: statsData.jami_vaqt || 0,
        ortacha_vaqt: statsData.ortacha_vaqt || 0,
        togri_javoblar: statsData.togri_javoblar || 0,
        notogri_javoblar: statsData.notogri_javoblar || 0,
        oson_yechilgan: statsData.oson_yechilgan || 0,
        oson_togri: statsData.oson_togri || 0,
        ortacha_yechilgan: statsData.ortacha_yechilgan || 0,
        ortacha_togri: statsData.ortacha_togri || 0,
        qiyin_yechilgan: statsData.qiyin_yechilgan || 0,
        qiyin_togri: statsData.qiyin_togri || 0
      })
      
      // History - kunlik statistikalar (grafik uchun)
      const historyData = historyRes.data || []
      const formattedHistory = historyData.map(item => ({
        sana: item.sana,
        kun: new Date(item.sana).toLocaleDateString('uz-UZ', { weekday: 'short' }),
        holatlar: item.yechilgan_holatlar || 0,
        togri: item.togri_javoblar || 0,
        notogri: item.notogri_javoblar || 0,
        vaqt: Math.round((item.jami_vaqt || 0) / 60), // daqiqaga
        ball: item.olingan_ball || 0
      })).reverse() // Eski -> yangi tartibda
      setHistory(formattedHistory)
      
      // Category stats
      setCategoryStats(categoryRes.data || [])
      
      // Calendar data
      setCalendarData(calendarRes.data || [])
    } catch (error) {
      console.error('Progress loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-12 skeleton rounded-xl w-48" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-32 skeleton rounded-2xl" />)}
        </div>
        <div className="h-80 skeleton rounded-2xl" />
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-display font-bold">Rivojlanish</h1>
          <p className="text-slate-400 mt-1">Sizning o'quv statistikangiz</p>
        </div>

        {/* Period selector */}
        <div className="flex items-center gap-2 p-1 rounded-xl bg-ocean-800/50">
          {[
            { value: 'hafta', label: 'Hafta' },
            { value: 'oy', label: 'Oy' },
            { value: 'yil', label: 'Yil' }
          ].map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                period === p.value
                  ? 'bg-med-500 text-white'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={HiOutlineAcademicCap}
          label="Jami holatlar"
          value={stats?.jami_holatlar || 0}
          subtext={`${stats?.bu_hafta_holatlar || 0} bu hafta`}
          color="med"
        />
        <StatCard
          icon={HiOutlineChartBar}
          label="Aniqlik"
          value={`${stats?.aniqlik || 0}%`}
          subtext={stats?.aniqlik_ozgarishi > 0 ? `+${stats.aniqlik_ozgarishi}%` : `${stats?.aniqlik_ozgarishi || 0}%`}
          trend={stats?.aniqlik_ozgarishi >= 0 ? 'up' : 'down'}
          color="blue"
        />
        <StatCard
          icon={HiOutlineClock}
          label="O'qish vaqti"
          value={formatTime(stats?.jami_vaqt || 0)}
          subtext={`O'rtacha ${stats?.ortacha_vaqt || 0} daq/holat`}
          color="purple"
        />
        <StatCard
          icon={HiOutlineFire}
          label="Eng uzun streak"
          value={`${stats?.eng_uzun_streak || 0} kun`}
          subtext={`Hozirgi: ${stats?.streak || 0} kun`}
          color="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="glass-card p-6">
          <h3 className="font-display font-semibold mb-6 flex items-center gap-2">
            <HiOutlineTrendingUp className="w-5 h-5 text-med-400" />
            Faoliyat
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b89c" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#14b89c" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="kun" 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f2137',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
                  }}
                  labelStyle={{ color: '#fff' }}
                />
                <Area
                  type="monotone"
                  dataKey="holatlar"
                  stroke="#14b89c"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorActivity)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Accuracy Chart */}
        <div className="glass-card p-6">
          <h3 className="font-display font-semibold mb-6 flex items-center gap-2">
            <HiOutlineChartBar className="w-5 h-5 text-blue-400" />
            Aniqlik dinamikasi
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis 
                  dataKey="kun" 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  domain={[0, 100]}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f2137',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px'
                  }}
                  formatter={(value) => [`${value}%`, 'Aniqlik']}
                />
                <Area
                  type="monotone"
                  dataKey="aniqlik"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorAccuracy)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Category Performance */}
      <div className="glass-card p-6">
        <h3 className="font-display font-semibold mb-6">Kategoriya bo'yicha natijalar</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryStats} layout="vertical">
              <XAxis type="number" stroke="#64748b" fontSize={12} domain={[0, 100]} />
              <YAxis 
                type="category" 
                dataKey="kategoriya" 
                stroke="#64748b" 
                fontSize={12}
                width={120}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f2137',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
                formatter={(value) => [`${value}%`, 'Aniqlik']}
              />
              <Bar 
                dataKey="aniqlik" 
                fill="#14b89c" 
                radius={[0, 4, 4, 0]}
                barSize={24}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Activity Calendar - Real ma'lumotlar bilan */}
      <ActivityCalendar calendarData={calendarData} />
    </motion.div>
  )
}

function StatCard({ icon: Icon, label, value, subtext, trend, color }) {
  const colors = {
    med: 'from-med-500/20 to-med-600/20 text-med-400',
    blue: 'from-blue-500/20 to-blue-600/20 text-blue-400',
    purple: 'from-purple-500/20 to-purple-600/20 text-purple-400',
    orange: 'from-orange-500/20 to-orange-600/20 text-orange-400',
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
      {subtext && (
        <div className={`mt-2 text-xs ${
          trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-slate-500'
        }`}>
          {subtext}
        </div>
      )}
    </div>
  )
}

function formatTime(minutes) {
  if (minutes < 60) return `${minutes} daq`
  const hours = Math.floor(minutes / 60)
  return `${hours} soat`
}

// Faoliyat kalendari komponenti - Real ma'lumotlar bilan
function ActivityCalendar({ calendarData }) {
  // Oxirgi 35 kunni hisoblash (5 hafta)
  const calendarDays = useMemo(() => {
    const days = []
    const today = new Date()
    
    // Kalendar uchun ma'lumotlarni map qilib olish
    const dataMap = {}
    if (Array.isArray(calendarData)) {
      calendarData.forEach(item => {
        // Backend dan kelgan sana formati: "2024-01-26" yoki ISO format
        const dateKey = item.sana ? item.sana.split('T')[0] : null
        if (dateKey) {
          dataMap[dateKey] = {
            holatlar: item.yechilgan_holatlar || 0,
            togri: item.togri_javoblar || 0,
            ball: item.olingan_ball || 0,
            vaqt: item.jami_vaqt || 0
          }
        }
      })
    }
    
    // 35 kunni orqaga hisoblash
    for (let i = 34; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateKey = date.toISOString().split('T')[0]
      
      const data = dataMap[dateKey] || null
      
      days.push({
        date: date,
        dateKey: dateKey,
        dayOfWeek: date.getDay(), // 0 = Yakshanba
        isToday: i === 0,
        data: data
      })
    }
    
    // Hafta boshidan to'ldirish (birinchi kun dushanba bo'lishi uchun)
    const firstDayOfWeek = days[0].date.getDay()
    const paddingDays = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1
    
    for (let i = 0; i < paddingDays; i++) {
      days.unshift({ empty: true })
    }
    
    return days
  }, [calendarData])

  // Faollik darajasini aniqlash
  const getActivityLevel = (data) => {
    if (!data || data.holatlar === 0) return 0
    if (data.holatlar >= 10) return 4
    if (data.holatlar >= 5) return 3
    if (data.holatlar >= 2) return 2
    return 1
  }

  const getActivityColor = (level) => {
    switch (level) {
      case 4: return 'bg-med-500 shadow-sm shadow-med-500/50'
      case 3: return 'bg-med-500/70'
      case 2: return 'bg-med-500/40'
      case 1: return 'bg-med-500/20'
      default: return 'bg-ocean-700/50'
    }
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short' })
  }

  // Jami statistika
  const totalStats = useMemo(() => {
    let holatlar = 0, togri = 0, kunlar = 0
    calendarDays.forEach(day => {
      if (day.data && day.data.holatlar > 0) {
        holatlar += day.data.holatlar
        togri += day.data.togri
        kunlar++
      }
    })
    return { holatlar, togri, kunlar }
  }, [calendarDays])

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-display font-semibold flex items-center gap-2">
          <HiOutlineCalendar className="w-5 h-5 text-gold-400" />
          Faoliyat kalendari
        </h3>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-slate-400">
            <span className="text-white font-medium">{totalStats.kunlar}</span> faol kun
          </span>
          <span className="text-slate-400">
            <span className="text-white font-medium">{totalStats.holatlar}</span> holat
          </span>
        </div>
      </div>
      
      {/* Hafta kunlari */}
      <div className="grid grid-cols-7 gap-1.5 sm:gap-2 mb-2">
        {['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'].map(day => (
          <div key={day} className="text-center text-xs text-slate-500 py-1 font-medium">
            {day}
          </div>
        ))}
      </div>
      
      {/* Kalendar */}
      <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
        {calendarDays.map((day, i) => {
          if (day.empty) {
            return <div key={`empty-${i}`} className="aspect-square" />
          }
          
          const level = getActivityLevel(day.data)
          const colorClass = getActivityColor(level)
          
          return (
            <div
              key={day.dateKey}
              className={`
                aspect-square rounded-lg transition-all duration-200 cursor-pointer
                ${colorClass}
                ${day.isToday ? 'ring-2 ring-white/30 ring-offset-1 ring-offset-ocean-900' : ''}
                hover:scale-110 hover:z-10
                group relative
              `}
            >
              {/* Tooltip */}
              <div className="
                absolute bottom-full left-1/2 -translate-x-1/2 mb-2 
                opacity-0 group-hover:opacity-100 pointer-events-none
                transition-opacity duration-200 z-20
              ">
                <div className="bg-ocean-800 border border-white/10 rounded-lg px-3 py-2 shadow-xl whitespace-nowrap">
                  <p className="text-xs font-medium text-white">{formatDate(day.date)}</p>
                  {day.data ? (
                    <>
                      <p className="text-xs text-slate-400 mt-1">
                        {day.data.holatlar} holat yechildi
                      </p>
                      <p className="text-xs text-slate-400">
                        {day.data.togri} to'g'ri ({day.data.holatlar > 0 ? Math.round(day.data.togri / day.data.holatlar * 100) : 0}%)
                      </p>
                      {day.data.ball > 0 && (
                        <p className="text-xs text-med-400">+{day.data.ball} ball</p>
                      )}
                    </>
                  ) : (
                    <p className="text-xs text-slate-500 mt-1">Faoliyat yo'q</p>
                  )}
                </div>
                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-ocean-800" />
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Legend */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/5">
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Faoliyat:</span>
          <div className="flex gap-1">
            <div className="w-3 h-3 rounded bg-ocean-700/50" title="Faoliyat yo'q" />
            <div className="w-3 h-3 rounded bg-med-500/20" title="1 holat" />
            <div className="w-3 h-3 rounded bg-med-500/40" title="2-4 holat" />
            <div className="w-3 h-3 rounded bg-med-500/70" title="5-9 holat" />
            <div className="w-3 h-3 rounded bg-med-500" title="10+ holat" />
          </div>
        </div>
        
        {totalStats.holatlar === 0 && (
          <p className="text-xs text-slate-500 italic">
            Hali faoliyat yo'q. Holatlarni yechib boshlang!
          </p>
        )}
      </div>
    </div>
  )
}

// useMemo import qo'shish uchun yuqoriga qarang
