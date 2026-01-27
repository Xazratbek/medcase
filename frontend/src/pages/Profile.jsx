import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import {
  HiOutlineCamera,
  HiOutlinePencil,
  HiOutlineAcademicCap,
  HiOutlineBriefcase,
  HiOutlineCalendar,
  HiOutlineMail,
  HiOutlineStar,
  HiOutlineFire,
  HiOutlineChartBar
} from 'react-icons/hi'
import toast from 'react-hot-toast'

const roles = {
  TALABA: { label: 'Talaba', icon: '🎓' },
  REZIDENT: { label: 'Rezident', icon: '👨‍⚕️' },
  SHIFOKOR: { label: 'Shifokor', icon: '⚕️' },
  OQITUVCHI: { label: "O'qituvchi", icon: '📚' },
  ADMIN: { label: 'Administrator', icon: '🔧' },
}

export default function Profile() {
  const { user, updateProfile, updateAvatar } = useAuthStore()
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef(null)

  const [formData, setFormData] = useState({
    ism: user?.ism || '',
    familiya: user?.familiya || '',
    bio: user?.bio || '',
    mutaxassislik: user?.mutaxassislik || '',
    muassasa: user?.muassasa || '',
  })

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 5 * 1024 * 1024) {
      toast.error("Rasm hajmi 5MB dan oshmasligi kerak")
      return
    }

    try {
      setLoading(true)
      const result = await updateAvatar(file, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        setUploadProgress(percentCompleted)
      })

      if (result.success || result.data?.muvaffaqiyat) {
        toast.success("Avatar yangilandi")
        // Refresh page or update state to show new avatar immediately is handled by store update usually
      }
    } catch (error) {
      console.error(error)
      toast.error("Avatar yuklashda xatolik")
    } finally {
      setLoading(false)
      setUploadProgress(0)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const result = await updateProfile(formData)

    if (result.success) {
      setEditing(false)
    }

    setLoading(false)
  }

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const role = roles[user?.rol] || roles.TALABA

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto space-y-6"
    >
      {/* Profile Header Card */}
      <div className="glass-card overflow-hidden">
        {/* Cover */}
        <div className="h-32 bg-gradient-to-r from-med-600 via-med-500 to-med-400 relative">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,...')] opacity-10" />
        </div>

        {/* Profile info */}
        <div className="px-6 pb-6">
          {/* Avatar */}
          <div className="relative -mt-16 mb-4">
            <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-med-400 to-med-600 p-1">
              <div className="w-full h-full rounded-xl bg-ocean-900 flex items-center justify-center overflow-hidden">
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-5xl font-display font-bold">{user?.ism?.[0] || 'F'}</span>
                )}
              </div>
            </div>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || uploadProgress > 0}
              className="absolute bottom-2 right-2 p-2 rounded-lg bg-ocean-800 border border-white/10 hover:bg-ocean-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <HiOutlineCamera className="w-5 h-5" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              disabled={loading || uploadProgress > 0}
              className="hidden"
            />

            {/* Upload Progress Overlay */}
            {uploadProgress > 0 && (
              <div className="absolute inset-0 rounded-2xl bg-black/60 flex flex-col items-center justify-center p-4 backdrop-blur-sm z-10">
                <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full bg-med-400 transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <span className="text-xs font-semibold text-white">{uploadProgress}%</span>
              </div>
            )}
          </div>

          {/* Name & Role */}
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-display font-bold">
                {user?.ism} {user?.familiya}
              </h1>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xl">{role.icon}</span>
                <span className="text-slate-400">{role.label}</span>
                {user?.muassasa && (
                  <>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-500">{user.muassasa}</span>
                  </>
                )}
              </div>
              {user?.bio && (
                <p className="mt-3 text-slate-400 max-w-lg">{user.bio}</p>
              )}
            </div>

            <button
              onClick={() => setEditing(!editing)}
              className="btn-secondary flex items-center gap-2"
            >
              <HiOutlinePencil className="w-5 h-5" />
              <span>{editing ? 'Bekor qilish' : 'Tahrirlash'}</span>
            </button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/5">
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-gradient">{user?.daraja || 1}</div>
              <div className="text-sm text-slate-500">Daraja</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-display font-bold">{user?.jami_holatlar || 0}</div>
              <div className="text-sm text-slate-500">Holatlar</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-gold-400">{user?.nishonlar_soni || 0}</div>
              <div className="text-sm text-slate-500">Nishonlar</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-display font-bold text-orange-400">{user?.streak || 0}</div>
              <div className="text-sm text-slate-500">Streak</div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Form */}
      {editing && (
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          onSubmit={handleSubmit}
          className="glass-card p-6"
        >
          <h2 className="text-lg font-display font-semibold mb-6">Profilni tahrirlash</h2>

          <div className="grid sm:grid-cols-2 gap-6">
            <div>
              <label className="input-label">Ism</label>
              <input
                type="text"
                name="ism"
                value={formData.ism}
                onChange={handleChange}
                className="input-field"
              />
            </div>
            <div>
              <label className="input-label">Familiya</label>
              <input
                type="text"
                name="familiya"
                value={formData.familiya}
                onChange={handleChange}
                className="input-field"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="input-label">Bio</label>
              <textarea
                name="bio"
                value={formData.bio}
                onChange={handleChange}
                rows={3}
                className="input-field resize-none"
                placeholder="O'zingiz haqingizda qisqacha..."
              />
            </div>
            <div>
              <label className="input-label">Mutaxassislik</label>
              <input
                type="text"
                name="mutaxassislik"
                value={formData.mutaxassislik}
                onChange={handleChange}
                className="input-field"
                placeholder="Masalan: Kardiologiya"
              />
            </div>
            <div>
              <label className="input-label">Muassasa</label>
              <input
                type="text"
                name="muassasa"
                value={formData.muassasa}
                onChange={handleChange}
                className="input-field"
                placeholder="Masalan: TTA"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={() => setEditing(false)}
              className="btn-secondary"
            >
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center min-w-[100px]"
            >
              {loading ? 'Saqlanmoqda...' : 'Saqlash'}
            </button>
          </div>
        </motion.form>
      )}

      {/* Info Cards */}
      <div className="grid sm:grid-cols-2 gap-6">
        {/* Account Info */}
        <div className="glass-card p-6">
          <h3 className="font-display font-semibold mb-4">Hisob ma'lumotlari</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-ocean-700/50 flex items-center justify-center">
                <HiOutlineMail className="w-5 h-5 text-slate-400" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Email</p>
                <p className="font-medium">{user?.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-ocean-700/50 flex items-center justify-center">
                <HiOutlineCalendar className="w-5 h-5 text-slate-400" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Ro'yxatdan o'tgan</p>
                <p className="font-medium">
                  {user?.yaratilgan_vaqt
                    ? new Date(user.yaratilgan_vaqt).toLocaleDateString('uz-UZ')
                    : 'Noma\'lum'
                  }
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-ocean-700/50 flex items-center justify-center">
                <HiOutlineAcademicCap className="w-5 h-5 text-slate-400" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Rol</p>
                <p className="font-medium">{role.label}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Achievements */}
        <div className="glass-card p-6">
          <h3 className="font-display font-semibold mb-4">Oxirgi yutuqlar</h3>
          {user?.oxirgi_nishonlar?.length > 0 ? (
            <div className="space-y-3">
              {user.oxirgi_nishonlar.slice(0, 3).map((achievement, index) => (
                <div key={index} className="flex items-center gap-3 p-3 rounded-xl bg-ocean-700/30">
                  <div className="w-10 h-10 rounded-xl bg-gold-500/20 flex items-center justify-center text-xl">
                    {achievement.icon || '⭐'}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{achievement.nomi}</p>
                    <p className="text-xs text-slate-500">{achievement.tavsif}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-slate-500 py-8">Hali nishonlar yo'q</p>
          )}
        </div>
      </div>
    </motion.div>
  )
}
