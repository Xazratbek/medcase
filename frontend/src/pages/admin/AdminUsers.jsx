import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../../utils/api'
import toast from 'react-hot-toast'
import {
  HiOutlineUsers,
  HiOutlineSearch,
  HiOutlineFilter,
  HiOutlineDotsVertical,
  HiOutlineTrash,
  HiOutlinePencil,
  HiOutlineBan,
  HiOutlineCheckCircle,
  HiOutlineShieldCheck,
  HiOutlineArrowLeft,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineX
} from 'react-icons/hi'

const ROLES = [
  { value: '', label: 'Barchasi' },
  { value: 'talaba', label: 'Talaba', color: 'bg-blue-500/20 text-blue-400' },
  { value: 'oqituvchi', label: "O'qituvchi", color: 'bg-green-500/20 text-green-400' },
  { value: 'admin', label: 'Admin', color: 'bg-purple-500/20 text-purple-400' },
  { value: 'super_admin', label: 'Super Admin', color: 'bg-red-500/20 text-red-400' },
]

export default function AdminUsers() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState(null)
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 0 })
  const [selectedUser, setSelectedUser] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [pagination.page, roleFilter, statusFilter])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (pagination.page !== 1) {
        setPagination(p => ({ ...p, page: 1 }))
      } else {
        loadUsers()
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [search])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const params = {
        sahifa: pagination.page,
        hajm: 20,
        qidiruv: search || undefined,
        rol: roleFilter || undefined,
        faol: statusFilter
      }
      const response = await api.get('/admin/foydalanuvchilar', { params })
      setUsers(response.data.foydalanuvchilar || [])
      setPagination(p => ({
        ...p,
        total: response.data.jami || 0,
        pages: response.data.sahifalar_soni || 0
      }))
    } catch (error) {
      toast.error("Foydalanuvchilarni yuklashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = async (userId, newRole) => {
    setActionLoading(true)
    try {
      await api.put(`/admin/foydalanuvchi/${userId}/rol`, { yangi_rol: newRole })
      toast.success("Rol o'zgartirildi")
      loadUsers()
      setShowModal(false)
    } catch (error) {
      toast.error("Rolni o'zgartirishda xatolik")
    } finally {
      setActionLoading(false)
    }
  }

  const handleToggleStatus = async (userId, currentStatus) => {
    setActionLoading(true)
    try {
      await api.put(`/admin/foydalanuvchi/${userId}/faollik`, { faol: !currentStatus })
      toast.success(currentStatus ? "Foydalanuvchi bloklandi" : "Foydalanuvchi faollashtirildi")
      loadUsers()
      setShowModal(false)
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async (userId) => {
    if (!confirm("Rostdan ham o'chirmoqchimisiz?")) return
    
    setActionLoading(true)
    try {
      await api.delete(`/admin/foydalanuvchi/${userId}`)
      toast.success("Foydalanuvchi o'chirildi")
      loadUsers()
      setShowModal(false)
    } catch (error) {
      toast.error(error.response?.data?.detail || "O'chirishda xatolik")
    } finally {
      setActionLoading(false)
    }
  }

  const getRoleStyle = (role) => {
    const r = ROLES.find(r => r.value === role?.toLowerCase())
    return r?.color || 'bg-slate-500/20 text-slate-400'
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <Link to="/admin" className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-4 transition-colors">
          <HiOutlineArrowLeft className="w-5 h-5" />
          <span>Admin Panel</span>
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold">Foydalanuvchilar</h1>
            <p className="text-slate-400 mt-1">Jami: {pagination.total} ta foydalanuvchi</p>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-4 mb-6"
      >
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Ism, email yoki username bo'yicha qidirish..."
              className="input-field pl-10 w-full"
            />
          </div>

          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value)
              setPagination(p => ({ ...p, page: 1 }))
            }}
            className="input-field w-full md:w-48"
          >
            {ROLES.map(r => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter === null ? '' : statusFilter ? 'true' : 'false'}
            onChange={(e) => {
              const val = e.target.value
              setStatusFilter(val === '' ? null : val === 'true')
              setPagination(p => ({ ...p, page: 1 }))
            }}
            className="input-field w-full md:w-40"
          >
            <option value="">Barcha holat</option>
            <option value="true">Faol</option>
            <option value="false">Bloklangan</option>
          </select>
        </div>
      </motion.div>

      {/* Users Table */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card overflow-hidden"
      >
        {loading ? (
          <div className="p-8 space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-16 skeleton rounded-xl" />
            ))}
          </div>
        ) : users.length > 0 ? (
          <>
            {/* Desktop Table */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full">
                <thead className="bg-ocean-800/50">
                  <tr>
                    <th className="text-left py-4 px-6 text-sm font-medium text-slate-400">Foydalanuvchi</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-slate-400">Email</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-slate-400">Rol</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-slate-400">Daraja</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-slate-400">Holat</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-slate-400">Ro'yxatdan</th>
                    <th className="text-right py-4 px-6 text-sm font-medium text-slate-400">Amallar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-white/5 transition-colors">
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-med-500/20 flex items-center justify-center">
                            {user.avatar_url ? (
                              <img src={user.avatar_url} alt="" className="w-full h-full rounded-xl object-cover" />
                            ) : (
                              <span className="text-med-400 font-bold">
                                {user.ism?.[0]?.toUpperCase() || '?'}
                              </span>
                            )}
                          </div>
                          <div>
                            <p className="font-medium">{user.toliq_ism || user.foydalanuvchi_nomi}</p>
                            <p className="text-sm text-slate-500">@{user.foydalanuvchi_nomi}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-slate-300">{user.email}</td>
                      <td className="py-4 px-4">
                        <span className={`px-3 py-1 rounded-lg text-xs font-medium ${getRoleStyle(user.rol)}`}>
                          {user.rol?.toUpperCase() || 'N/A'}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-gold-400 font-medium">{user.daraja}</span>
                          <span className="text-xs text-slate-500">({user.jami_ball} ball)</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        {user.faol ? (
                          <span className="flex items-center gap-1 text-green-400 text-sm">
                            <HiOutlineCheckCircle className="w-4 h-4" />
                            Faol
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-400 text-sm">
                            <HiOutlineBan className="w-4 h-4" />
                            Bloklangan
                          </span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-sm text-slate-400">
                        {user.yaratilgan_vaqt ? new Date(user.yaratilgan_vaqt).toLocaleDateString('uz-UZ') : '-'}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <button
                          onClick={() => {
                            setSelectedUser(user)
                            setShowModal(true)
                          }}
                          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                        >
                          <HiOutlineDotsVertical className="w-5 h-5 text-slate-400" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile Cards */}
            <div className="md:hidden divide-y divide-white/5">
              {users.map((user) => (
                <div key={user.id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-med-500/20 flex items-center justify-center">
                        {user.avatar_url ? (
                          <img src={user.avatar_url} alt="" className="w-full h-full rounded-xl object-cover" />
                        ) : (
                          <span className="text-med-400 font-bold text-lg">
                            {user.ism?.[0]?.toUpperCase() || '?'}
                          </span>
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{user.toliq_ism}</p>
                        <p className="text-sm text-slate-500">@{user.foydalanuvchi_nomi}</p>
                        <p className="text-xs text-slate-400 mt-1">{user.email}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedUser(user)
                        setShowModal(true)
                      }}
                      className="p-2 rounded-lg hover:bg-white/10"
                    >
                      <HiOutlineDotsVertical className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="flex items-center gap-3 mt-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getRoleStyle(user.rol)}`}>
                      {user.rol?.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400">Daraja: {user.daraja}</span>
                    {user.faol ? (
                      <span className="text-xs text-green-400">Faol</span>
                    ) : (
                      <span className="text-xs text-red-400">Bloklangan</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex items-center justify-between p-4 border-t border-white/5">
                <p className="text-sm text-slate-400">
                  Sahifa {pagination.page} / {pagination.pages}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="p-2 rounded-lg hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <HiOutlineChevronLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
                    disabled={pagination.page >= pagination.pages}
                    className="p-2 rounded-lg hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <HiOutlineChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="p-12 text-center">
            <HiOutlineUsers className="w-16 h-16 mx-auto text-slate-600 mb-4" />
            <p className="text-slate-400">Foydalanuvchilar topilmadi</p>
          </div>
        )}
      </motion.div>

      {/* User Actions Modal */}
      <AnimatePresence>
        {showModal && selectedUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card p-6 max-w-md w-full"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-med-500/20 flex items-center justify-center">
                    <span className="text-med-400 font-bold">
                      {selectedUser.ism?.[0]?.toUpperCase() || '?'}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-display font-semibold">{selectedUser.toliq_ism}</h3>
                    <p className="text-sm text-slate-400">{selectedUser.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-2 rounded-lg hover:bg-white/10"
                >
                  <HiOutlineX className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3">
                {/* Change Role */}
                <div className="p-4 rounded-xl bg-ocean-800/50">
                  <p className="text-sm text-slate-400 mb-2">Rolni o'zgartirish</p>
                  <div className="grid grid-cols-2 gap-2">
                    {ROLES.filter(r => r.value).map(role => (
                      <button
                        key={role.value}
                        onClick={() => handleRoleChange(selectedUser.id, role.value)}
                        disabled={actionLoading || selectedUser.rol?.toLowerCase() === role.value}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                          selectedUser.rol?.toLowerCase() === role.value
                            ? role.color + ' ring-2 ring-current'
                            : 'bg-ocean-700/50 hover:bg-ocean-700 text-slate-300'
                        } disabled:opacity-50`}
                      >
                        {role.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Toggle Status */}
                <button
                  onClick={() => handleToggleStatus(selectedUser.id, selectedUser.faol)}
                  disabled={actionLoading}
                  className={`w-full flex items-center gap-3 p-4 rounded-xl transition-colors ${
                    selectedUser.faol
                      ? 'bg-red-500/10 hover:bg-red-500/20 text-red-400'
                      : 'bg-green-500/10 hover:bg-green-500/20 text-green-400'
                  }`}
                >
                  {selectedUser.faol ? (
                    <>
                      <HiOutlineBan className="w-5 h-5" />
                      <span>Bloklash</span>
                    </>
                  ) : (
                    <>
                      <HiOutlineCheckCircle className="w-5 h-5" />
                      <span>Faollashtirish</span>
                    </>
                  )}
                </button>

                {/* Delete */}
                <button
                  onClick={() => handleDelete(selectedUser.id)}
                  disabled={actionLoading}
                  className="w-full flex items-center gap-3 p-4 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"
                >
                  <HiOutlineTrash className="w-5 h-5" />
                  <span>O'chirish</span>
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
