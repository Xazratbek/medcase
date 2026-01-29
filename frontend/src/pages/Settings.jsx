import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { userAPI } from '../utils/api'
import { ensurePushSubscription, removePushSubscription } from '../utils/push'
import {
  HiOutlineCog,
  HiOutlineBell,
  HiOutlineShieldCheck,
  HiOutlineGlobe,
  HiOutlineMoon,
  HiOutlineTrash,
  HiOutlineLogout,
  HiOutlineEye,
  HiOutlineEyeOff,
  HiOutlineMail,
  HiOutlineDeviceMobile,
  HiOutlineClock,
  HiOutlineVolumeOff,
  HiOutlineDownload,
  HiOutlineDocumentReport
} from 'react-icons/hi'
import toast from 'react-hot-toast'

export default function Settings() {
  const { user, logout } = useAuthStore()
  const [activeTab, setActiveTab] = useState('notifications')
  const [loading, setLoading] = useState(false)
  const [settingsLoading, setSettingsLoading] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)
  
  // Bildirishnoma sozlamalari - backend bilan to'liq integratsiya
  const [notifications, setNotifications] = useState({
    // Email bildirishnomalari
    email_yutuqlar: true,
    email_streak: true,
    email_yangi_kontent: false,
    email_haftalik_hisobot: true,
    // Push bildirishnomalari
    push_yutuqlar: true,
    push_streak: true,
    push_eslatma: true,
    push_reyting: false,
    push_yangi_kontent: true,
    // Ilova ichidagi
    ilova_yutuqlar: true,
    ilova_streak: true,
    ilova_yangi_kontent: true,
    ilova_tizim: true,
    // Sokin rejim
    sokin_rejim: false,
    sokin_boshlanish: '22:00',
    sokin_tugash: '07:00',
  })

  // Eslatma vaqtlari
  const [eslatmaVaqtlari, setEslatmaVaqtlari] = useState({
    soat: 9,
    daqiqa: 0,
    kunlar: [1, 2, 3, 4, 5] // Dush-Jum
  })

  const [passwords, setPasswords] = useState({
    joriy_parol: '',
    yangi_parol: '',
    parol_tasdiqlash: ''
  })

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setSettingsLoading(true)
    try {
      const response = await userAPI.getNotificationSettings()
      const data = response.data
      if (data) {
        const next = {
          email_yutuqlar: data.email_yutuqlar ?? true,
          email_streak: data.email_streak ?? true,
          email_yangi_kontent: data.email_yangi_kontent ?? false,
          email_haftalik_hisobot: data.email_haftalik_hisobot ?? true,
          push_yutuqlar: data.push_yutuqlar ?? true,
          push_streak: data.push_streak ?? true,
          push_eslatma: data.push_eslatma ?? true,
          push_reyting: data.push_reyting ?? false,
          push_yangi_kontent: data.push_yangi_kontent ?? true,
          ilova_yutuqlar: data.ilova_yutuqlar ?? true,
          ilova_streak: data.ilova_streak ?? true,
          ilova_yangi_kontent: data.ilova_yangi_kontent ?? true,
          ilova_tizim: data.ilova_tizim ?? true,
          sokin_rejim: data.sokin_rejim ?? false,
          sokin_boshlanish: data.sokin_boshlanish ?? '22:00',
          sokin_tugash: data.sokin_tugash ?? '07:00',
        }
        setNotifications(next)
        const pushKeys = ['push_yutuqlar', 'push_streak', 'push_eslatma', 'push_reyting', 'push_yangi_kontent']
        if (pushKeys.some((k) => next[k])) {
          ensurePushSubscription().catch(() => {})
        }
        if (data.eslatma_vaqtlari) {
          setEslatmaVaqtlari(data.eslatma_vaqtlari)
        }
      }
    } catch (error) {
      console.error('Settings loading error:', error)
    } finally {
      setSettingsLoading(false)
    }
  }

  const handleNotificationChange = async (key) => {
    const newValue = !notifications[key]
    setNotifications(prev => ({ ...prev, [key]: newValue }))
    
    try {
      const pushKeys = ['push_yutuqlar', 'push_streak', 'push_eslatma', 'push_reyting', 'push_yangi_kontent']
      if (pushKeys.includes(key) && newValue) {
        await ensurePushSubscription()
      }
      if (pushKeys.includes(key) && !newValue) {
        const anyPushEnabled = pushKeys.some((k) => (k === key ? false : notifications[k]))
        if (!anyPushEnabled) {
          await removePushSubscription()
        }
      }

      await userAPI.updateNotificationSettings({ [key]: newValue })
      toast.success("Saqlandi", { duration: 1500 })
    } catch (error) {
      setNotifications(prev => ({ ...prev, [key]: !newValue }))
      toast.error("Xatolik yuz berdi")
    }
  }

  const handleSokinRejimVaqti = async (field, value) => {
    setNotifications(prev => ({ ...prev, [field]: value }))
    
    try {
      await userAPI.updateNotificationSettings({ [field]: value })
    } catch (error) {
      toast.error("Vaqtni saqlashda xatolik")
    }
  }

  const handleEslatmaVaqtlari = async () => {
    try {
      await userAPI.updateNotificationSettings({ eslatma_vaqtlari: eslatmaVaqtlari })
      toast.success("Eslatma vaqtlari saqlandi")
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    
    if (passwords.yangi_parol !== passwords.parol_tasdiqlash) {
      toast.error("Parollar mos kelmadi")
      return
    }

    if (passwords.yangi_parol.length < 8) {
      toast.error("Parol kamida 8 belgidan iborat bo'lishi kerak")
      return
    }

    setLoading(true)
    try {
      await userAPI.changePassword({
        joriy_parol: passwords.joriy_parol,
        yangi_parol: passwords.yangi_parol
      })
      toast.success("Parol muvaffaqiyatli o'zgartirildi")
      setPasswords({ joriy_parol: '', yangi_parol: '', parol_tasdiqlash: '' })
    } catch (error) {
      toast.error(error.response?.data?.xato || "Parolni o'zgartirishda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format) => {
    setExportLoading(true)
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || '/api/v1'}/export/rivojlanish/${format}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      
      if (!response.ok) throw new Error('Export xatosi')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rivojlanish_hisoboti.${format === 'pdf' ? 'pdf' : 'xlsx'}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      a.remove()
      
      toast.success(`${format.toUpperCase()} yuklab olindi`)
    } catch (error) {
      toast.error("Yuklab olishda xatolik")
    } finally {
      setExportLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    try {
      await userAPI.deleteAccount()
      toast.success("Hisobingiz o'chirildi")
      logout()
    } catch (error) {
      toast.error("Hisobni o'chirishda xatolik")
    }
  }

  const tabs = [
    { id: 'notifications', label: 'Bildirishnomalar', icon: HiOutlineBell },
    { id: 'security', label: 'Xavfsizlik', icon: HiOutlineShieldCheck },
    { id: 'data', label: "Ma'lumotlar", icon: HiOutlineDownload },
    { id: 'account', label: 'Hisob', icon: HiOutlineCog },
  ]

  const kunlar = [
    { id: 1, nom: 'Du' },
    { id: 2, nom: 'Se' },
    { id: 3, nom: 'Ch' },
    { id: 4, nom: 'Pa' },
    { id: 5, nom: 'Ju' },
    { id: 6, nom: 'Sh' },
    { id: 7, nom: 'Ya' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto"
    >
      <h1 className="text-2xl lg:text-3xl font-display font-bold mb-6">Sozlamalar</h1>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar */}
        <div className="lg:w-64 flex-shrink-0">
          <div className="glass-card p-2 flex lg:flex-col gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all w-full text-left ${
                  activeTab === tab.id
                    ? 'bg-med-500/10 text-med-400'
                    : 'text-slate-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="hidden lg:inline">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'notifications' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {settingsLoading ? (
                <div className="glass-card p-6">
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map(i => (
                      <div key={i} className="h-16 skeleton rounded-xl" />
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {/* Push Bildirishnomalar */}
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-med-500/20 flex items-center justify-center">
                        <HiOutlineDeviceMobile className="w-5 h-5 text-med-400" />
                      </div>
                      <div>
                        <h2 className="text-lg font-display font-semibold">Push Bildirishnomalar</h2>
                        <p className="text-sm text-slate-500">Qurilmangizga real-time xabarlar</p>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <ToggleSetting
                        label="Yutuqlar"
                        description="Yangi nishon yoki daraja olganingizda"
                        checked={notifications.push_yutuqlar}
                        onChange={() => handleNotificationChange('push_yutuqlar')}
                      />
                      <ToggleSetting
                        label="Streak eslatmasi"
                        description="Kunlik streakni saqlab qolish uchun"
                        checked={notifications.push_streak}
                        onChange={() => handleNotificationChange('push_streak')}
                      />
                      <ToggleSetting
                        label="O'qish eslatmasi"
                        description="Belgilangan vaqtda eslatma olish"
                        checked={notifications.push_eslatma}
                        onChange={() => handleNotificationChange('push_eslatma')}
                      />
                      <ToggleSetting
                        label="Yangi kontent"
                        description="Yangi holatlar qo'shilganda"
                        checked={notifications.push_yangi_kontent}
                        onChange={() => handleNotificationChange('push_yangi_kontent')}
                      />
                      <ToggleSetting
                        label="Reyting yangilanishi"
                        description="Reytingdagi o'rningiz o'zgarganda"
                        checked={notifications.push_reyting}
                        onChange={() => handleNotificationChange('push_reyting')}
                      />
                    </div>
                  </div>

                  {/* Email Bildirishnomalar */}
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-coral-500/20 flex items-center justify-center">
                        <HiOutlineMail className="w-5 h-5 text-coral-400" />
                      </div>
                      <div>
                        <h2 className="text-lg font-display font-semibold">Email Bildirishnomalar</h2>
                        <p className="text-sm text-slate-500">{user?.email} manziliga</p>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      <ToggleSetting
                        label="Yutuq xabarlari"
                        description="Muhim yutuqlar haqida email"
                        checked={notifications.email_yutuqlar}
                        onChange={() => handleNotificationChange('email_yutuqlar')}
                      />
                      <ToggleSetting
                        label="Streak eslatmasi"
                        description="Streakni yo'qotmaslik uchun"
                        checked={notifications.email_streak}
                        onChange={() => handleNotificationChange('email_streak')}
                      />
                      <ToggleSetting
                        label="Yangi kontent"
                        description="Yangi holatlar qo'shilganda"
                        checked={notifications.email_yangi_kontent}
                        onChange={() => handleNotificationChange('email_yangi_kontent')}
                      />
                      <ToggleSetting
                        label="Haftalik hisobot"
                        description="Har hafta rivojlanish xulosasi"
                        checked={notifications.email_haftalik_hisobot}
                        onChange={() => handleNotificationChange('email_haftalik_hisobot')}
                      />
                    </div>
                  </div>

                  {/* Eslatma Vaqtlari */}
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-gold-500/20 flex items-center justify-center">
                        <HiOutlineClock className="w-5 h-5 text-gold-400" />
                      </div>
                      <div>
                        <h2 className="text-lg font-display font-semibold">Eslatma Vaqtlari</h2>
                        <p className="text-sm text-slate-500">Kunlik o'qish eslatmasi</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {/* Vaqt tanlash */}
                      <div className="flex items-center gap-4">
                        <label className="text-sm text-slate-400 w-20">Vaqt:</label>
                        <div className="flex items-center gap-2">
                          <select 
                            value={eslatmaVaqtlari.soat}
                            onChange={(e) => setEslatmaVaqtlari(prev => ({ ...prev, soat: parseInt(e.target.value) }))}
                            className="input-field w-20 py-2 text-center"
                          >
                            {[...Array(24)].map((_, i) => (
                              <option key={i} value={i}>{i.toString().padStart(2, '0')}</option>
                            ))}
                          </select>
                          <span className="text-slate-500">:</span>
                          <select
                            value={eslatmaVaqtlari.daqiqa}
                            onChange={(e) => setEslatmaVaqtlari(prev => ({ ...prev, daqiqa: parseInt(e.target.value) }))}
                            className="input-field w-20 py-2 text-center"
                          >
                            {[0, 15, 30, 45].map((m) => (
                              <option key={m} value={m}>{m.toString().padStart(2, '0')}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      {/* Kunlar tanlash */}
                      <div className="flex items-center gap-4">
                        <label className="text-sm text-slate-400 w-20">Kunlar:</label>
                        <div className="flex gap-2">
                          {kunlar.map(kun => (
                            <button
                              key={kun.id}
                              onClick={() => {
                                const yangiKunlar = eslatmaVaqtlari.kunlar.includes(kun.id)
                                  ? eslatmaVaqtlari.kunlar.filter(k => k !== kun.id)
                                  : [...eslatmaVaqtlari.kunlar, kun.id].sort()
                                setEslatmaVaqtlari(prev => ({ ...prev, kunlar: yangiKunlar }))
                              }}
                              className={`w-10 h-10 rounded-lg font-medium text-sm transition-all ${
                                eslatmaVaqtlari.kunlar.includes(kun.id)
                                  ? 'bg-med-500 text-white'
                                  : 'bg-ocean-700/50 text-slate-400 hover:bg-ocean-700'
                              }`}
                            >
                              {kun.nom}
                            </button>
                          ))}
                        </div>
                      </div>
                      
                      <button
                        onClick={handleEslatmaVaqtlari}
                        className="btn-secondary text-sm px-4 py-2"
                      >
                        Saqlash
                      </button>
                    </div>
                  </div>

                  {/* Sokin Rejim */}
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                        <HiOutlineVolumeOff className="w-5 h-5 text-purple-400" />
                      </div>
                      <div>
                        <h2 className="text-lg font-display font-semibold">Sokin Rejim</h2>
                        <p className="text-sm text-slate-500">Belgilangan vaqtda bildirishnomalar o'chiriladi</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <ToggleSetting
                        label="Sokin rejimni yoqish"
                        description="Tanlangan vaqt oralig'ida bildirishnomalar kelmasin"
                        checked={notifications.sokin_rejim}
                        onChange={() => handleNotificationChange('sokin_rejim')}
                      />
                      
                      {notifications.sokin_rejim && (
                        <motion.div 
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="flex items-center gap-4 pt-2"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-400">Dan:</span>
                            <input
                              type="time"
                              value={notifications.sokin_boshlanish}
                              onChange={(e) => handleSokinRejimVaqti('sokin_boshlanish', e.target.value)}
                              className="input-field w-28 py-2 text-center"
                            />
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-400">Gacha:</span>
                            <input
                              type="time"
                              value={notifications.sokin_tugash}
                              onChange={(e) => handleSokinRejimVaqti('sokin_tugash', e.target.value)}
                              className="input-field w-28 py-2 text-center"
                            />
                          </div>
                        </motion.div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          )}

          {activeTab === 'security' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-6"
            >
              <h2 className="text-lg font-display font-semibold mb-6">Parolni o'zgartirish</h2>
              
              <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
                <div>
                  <label className="input-label">Joriy parol</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={passwords.joriy_parol}
                      onChange={(e) => setPasswords(prev => ({ ...prev, joriy_parol: e.target.value }))}
                      className="input-field pr-12"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500"
                    >
                      {showPassword ? <HiOutlineEyeOff className="w-5 h-5" /> : <HiOutlineEye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="input-label">Yangi parol</label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={passwords.yangi_parol}
                    onChange={(e) => setPasswords(prev => ({ ...prev, yangi_parol: e.target.value }))}
                    className="input-field"
                    minLength={8}
                    required
                  />
                </div>

                <div>
                  <label className="input-label">Yangi parolni tasdiqlang</label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={passwords.parol_tasdiqlash}
                    onChange={(e) => setPasswords(prev => ({ ...prev, parol_tasdiqlash: e.target.value }))}
                    className="input-field"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? "O'zgartirilmoqda..." : "Parolni o'zgartirish"}
                </button>
              </form>
            </motion.div>
          )}

          {activeTab === 'data' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Export */}
              <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-xl bg-med-500/20 flex items-center justify-center">
                    <HiOutlineDocumentReport className="w-5 h-5 text-med-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-display font-semibold">Hisobotni Yuklab Olish</h2>
                    <p className="text-sm text-slate-500">Rivojlanish statistikangizni eksport qiling</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <button
                    onClick={() => handleExport('pdf')}
                    disabled={exportLoading}
                    className="flex items-center gap-4 p-4 rounded-xl bg-ocean-700/50 hover:bg-ocean-700 border border-white/5 hover:border-red-500/30 transition-all group"
                  >
                    <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-red-400 font-bold text-sm">PDF</span>
                    </div>
                    <div className="text-left">
                      <p className="font-medium">PDF Hisobot</p>
                      <p className="text-xs text-slate-500">Chop etish uchun qulay</p>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => handleExport('excel')}
                    disabled={exportLoading}
                    className="flex items-center gap-4 p-4 rounded-xl bg-ocean-700/50 hover:bg-ocean-700 border border-white/5 hover:border-green-500/30 transition-all group"
                  >
                    <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <span className="text-green-400 font-bold text-sm">XLS</span>
                    </div>
                    <div className="text-left">
                      <p className="font-medium">Excel Hisobot</p>
                      <p className="text-xs text-slate-500">Tahlil qilish uchun</p>
                    </div>
                  </button>
                </div>
                
                {exportLoading && (
                  <div className="flex items-center gap-3 mt-4 p-3 rounded-lg bg-med-500/10 border border-med-500/20">
                    <div className="w-5 h-5 border-2 border-med-500/30 border-t-med-500 rounded-full animate-spin" />
                    <span className="text-sm text-med-400">Hisobot tayyorlanmoqda...</span>
                  </div>
                )}
              </div>

              {/* Ma'lumotlar haqida */}
              <div className="glass-card p-6">
                <h2 className="text-lg font-display font-semibold mb-4">Sizning ma'lumotlaringiz</h2>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between py-2 border-b border-white/5">
                    <span className="text-slate-500">Yechilgan holatlar</span>
                    <span className="font-medium">{user?.statistika?.jami_yechilgan || 0} ta</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/5">
                    <span className="text-slate-500">Nishonlar</span>
                    <span className="font-medium">{user?.statistika?.nishonlar_soni || 0} ta</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/5">
                    <span className="text-slate-500">Xatcholar</span>
                    <span className="font-medium">{user?.statistika?.xatcholar_soni || 0} ta</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-slate-500">Ro'yxatdan o'tgan</span>
                    <span className="font-medium">
                      {user?.yaratilgan_vaqt 
                        ? new Date(user.yaratilgan_vaqt).toLocaleDateString('uz-UZ') 
                        : '-'}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'account' && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div className="glass-card p-6">
                <h2 className="text-lg font-display font-semibold mb-4">Hisob ma'lumotlari</h2>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between py-2 border-b border-white/5">
                    <span className="text-slate-500">Email</span>
                    <span>{user?.email}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/5">
                    <span className="text-slate-500">Foydalanuvchi nomi</span>
                    <span>@{user?.foydalanuvchi_nomi}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-white/5">
                    <span className="text-slate-500">Rol</span>
                    <span className="badge-primary capitalize">{user?.rol || 'Talaba'}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-slate-500">Hisob turi</span>
                    <span className="badge-gold">Bepul</span>
                  </div>
                </div>
              </div>

              <div className="glass-card p-6 border border-red-500/20">
                <h2 className="text-lg font-display font-semibold mb-2 text-red-400">Xavfli zona</h2>
                <p className="text-sm text-slate-500 mb-4">
                  Bu amallar qaytarib bo'lmaydi. Ehtiyot bo'ling.
                </p>
                
                <div className="space-y-3">
                  <button
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-ocean-700/50 hover:bg-ocean-700 transition-colors text-left"
                  >
                    <HiOutlineLogout className="w-5 h-5 text-slate-400" />
                    <div>
                      <p className="font-medium">Chiqish</p>
                      <p className="text-xs text-slate-500">Tizimdan chiqish</p>
                    </div>
                  </button>

                  <button 
                    onClick={() => setShowDeleteModal(true)}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 hover:bg-red-500/20 transition-colors text-left border border-red-500/20"
                  >
                    <HiOutlineTrash className="w-5 h-5 text-red-400" />
                    <div>
                      <p className="font-medium text-red-400">Hisobni o'chirish</p>
                      <p className="text-xs text-slate-500">Barcha ma'lumotlar o'chiriladi</p>
                    </div>
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Delete Account Modal */}
          <AnimatePresence>
            {showDeleteModal && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                onClick={() => setShowDeleteModal(false)}
              >
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.95, opacity: 0 }}
                  onClick={(e) => e.stopPropagation()}
                  className="glass-card p-6 max-w-md w-full"
                >
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto rounded-full bg-red-500/20 flex items-center justify-center mb-4">
                      <HiOutlineTrash className="w-8 h-8 text-red-400" />
                    </div>
                    <h3 className="text-xl font-display font-bold mb-2">Hisobni o'chirish</h3>
                    <p className="text-slate-400 mb-6">
                      Bu amalni qaytarib bo'lmaydi. Barcha ma'lumotlaringiz, yutuqlaringiz va rivojlanish tarixingiz o'chiriladi.
                    </p>
                    
                    <div className="flex gap-3">
                      <button
                        onClick={() => setShowDeleteModal(false)}
                        className="flex-1 btn-secondary"
                      >
                        Bekor qilish
                      </button>
                      <button
                        onClick={handleDeleteAccount}
                        className="flex-1 px-6 py-3 rounded-xl font-display font-medium bg-red-500 hover:bg-red-600 text-white transition-colors"
                      >
                        O'chirish
                      </button>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  )
}

function ToggleSetting({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
      <div>
        <p className="font-medium">{label}</p>
        <p className="text-sm text-slate-500">{description}</p>
      </div>
      <button
        onClick={onChange}
        className={`relative w-12 h-7 rounded-full transition-colors ${
          checked ? 'bg-med-500' : 'bg-ocean-700'
        }`}
      >
        <div className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${
          checked ? 'left-6' : 'left-1'
        }`} />
      </button>
    </div>
  )
}
