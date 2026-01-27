import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import toast from 'react-hot-toast'
import {
  HiOutlineDocumentText,
  HiOutlineSearch,
  HiOutlinePlus,
  HiOutlineDotsVertical,
  HiOutlineTrash,
  HiOutlinePencil,
  HiOutlineEye,
  HiOutlineArrowLeft,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineX,
  HiOutlineFilter,
  HiOutlinePhotograph
} from 'react-icons/hi'

const DIFFICULTIES = [
  { value: '', label: 'Barchasi' },
  { value: 'oson', label: 'Oson', color: 'bg-green-500/20 text-green-400' },
  { value: 'ortacha', label: "O'rtacha", color: 'bg-yellow-500/20 text-yellow-400' },
  { value: 'qiyin', label: 'Qiyin', color: 'bg-red-500/20 text-red-400' },
]

export default function AdminCases() {
  const navigate = useNavigate()
  const [cases, setCases] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [diffFilter, setDiffFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 0 })
  const [selectedCase, setSelectedCase] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadCases()
  }, [pagination.page, diffFilter, categoryFilter])

  useEffect(() => {
    const timer = setTimeout(() => {
      if (pagination.page !== 1) {
        setPagination(p => ({ ...p, page: 1 }))
      } else {
        loadCases()
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [search])

  const loadCategories = async () => {
    try {
      const response = await api.get('/kategoriya/')
      const data = response.data
      // kategoriyalar massiv ekanligini tekshirish
      if (Array.isArray(data)) {
        setCategories(data)
      } else if (Array.isArray(data?.kategoriyalar)) {
        setCategories(data.kategoriyalar)
      } else {
        setCategories([])
      }
    } catch (error) {
      console.error('Categories error:', error)
      setCategories([])
    }
  }

  const loadCases = async () => {
    setLoading(true)
    try {
      const params = {
        sahifa: pagination.page,
        hajm: 20,
        qidiruv: search || undefined,
        qiyinlik: diffFilter || undefined,
        kategoriya_id: categoryFilter || undefined
      }
      const response = await api.get('/holat/', { params })
      const data = response.data.malumot || response.data
      setCases(data?.elementlar || data?.holatlar || [])
      setPagination(p => ({
        ...p,
        total: data?.jami || 0,
        pages: data?.sahifalar_soni || Math.ceil((data?.jami || 0) / 20)
      }))
    } catch (error) {
      toast.error("Holatlarni yuklashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (caseId) => {
    if (!confirm("Rostdan ham o'chirmoqchimisiz? Bu amalni qaytarib bo'lmaydi.")) return
    
    setActionLoading(true)
    try {
      await api.delete(`/admin/holat/${caseId}`)
      toast.success("Holat o'chirildi")
      loadCases()
      setShowModal(false)
    } catch (error) {
      toast.error(error.response?.data?.detail || "O'chirishda xatolik")
    } finally {
      setActionLoading(false)
    }
  }

  const getDiffStyle = (diff) => {
    const d = DIFFICULTIES.find(d => d.value === diff?.toLowerCase())
    return d?.color || 'bg-slate-500/20 text-slate-400'
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
            <h1 className="text-3xl font-display font-bold">Holatlar</h1>
            <p className="text-slate-400 mt-1">Jami: {pagination.total} ta holat</p>
          </div>
          <Link
            to="/admin/import"
            className="btn-primary flex items-center gap-2"
          >
            <HiOutlinePlus className="w-5 h-5" />
            <span className="hidden sm:inline">Import qilish</span>
          </Link>
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
              placeholder="Sarlavha yoki matn bo'yicha qidirish..."
              className="input-field pl-10 w-full"
            />
          </div>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value)
              setPagination(p => ({ ...p, page: 1 }))
            }}
            className="input-field w-full md:w-56"
          >
            <option value="">Barcha kategoriyalar</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.nomi}</option>
            ))}
          </select>

          {/* Difficulty Filter */}
          <select
            value={diffFilter}
            onChange={(e) => {
              setDiffFilter(e.target.value)
              setPagination(p => ({ ...p, page: 1 }))
            }}
            className="input-field w-full md:w-40"
          >
            {DIFFICULTIES.map(d => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Cases List */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card overflow-hidden"
      >
        {loading ? (
          <div className="p-8 space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-20 skeleton rounded-xl" />
            ))}
          </div>
        ) : cases.length > 0 ? (
          <>
            {/* Cases */}
            <div className="divide-y divide-white/5">
              {cases.map((caseItem) => (
                <div key={caseItem.id} className="p-4 hover:bg-white/5 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium truncate">{caseItem.sarlavha}</h3>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium flex-shrink-0 ${getDiffStyle(caseItem.qiyinlik)}`}>
                          {caseItem.qiyinlik?.toUpperCase() || 'N/A'}
                        </span>
                        {caseItem.media?.length > 0 && (
                          <HiOutlinePhotograph className="w-4 h-4 text-slate-500 flex-shrink-0" title="Media mavjud" />
                        )}
                      </div>
                      <p className="text-sm text-slate-400 line-clamp-2 mb-2">
                        {caseItem.klinik_stsenariy || caseItem.tavsif || caseItem.savol}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span>{caseItem.kategoriya_nomi || caseItem.bolim_nomi}</span>
                        <span>•</span>
                        <span>{caseItem.ball || 10} ball</span>
                        <span>•</span>
                        <span>{caseItem.urinishlar_soni || 0} urinish</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Link
                        to={`/holat/${caseItem.id}`}
                        className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                        title="Ko'rish"
                      >
                        <HiOutlineEye className="w-5 h-5" />
                      </Link>
                      <button
                        onClick={() => {
                          setSelectedCase(caseItem)
                          setShowModal(true)
                        }}
                        className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                      >
                        <HiOutlineDotsVertical className="w-5 h-5 text-slate-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex items-center justify-between p-4 border-t border-white/5">
                <p className="text-sm text-slate-400">
                  Sahifa {pagination.page} / {pagination.pages} (Jami: {pagination.total})
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="p-2 rounded-lg hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <HiOutlineChevronLeft className="w-5 h-5" />
                  </button>
                  
                  {/* Page numbers */}
                  <div className="hidden sm:flex items-center gap-1">
                    {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                      let pageNum
                      if (pagination.pages <= 5) {
                        pageNum = i + 1
                      } else if (pagination.page <= 3) {
                        pageNum = i + 1
                      } else if (pagination.page >= pagination.pages - 2) {
                        pageNum = pagination.pages - 4 + i
                      } else {
                        pageNum = pagination.page - 2 + i
                      }
                      
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setPagination(p => ({ ...p, page: pageNum }))}
                          className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                            pagination.page === pageNum
                              ? 'bg-med-500 text-white'
                              : 'hover:bg-white/10 text-slate-400'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                  </div>
                  
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
            <HiOutlineDocumentText className="w-16 h-16 mx-auto text-slate-600 mb-4" />
            <p className="text-slate-400 mb-4">Holatlar topilmadi</p>
            <Link to="/admin/import" className="btn-primary inline-flex items-center gap-2">
              <HiOutlinePlus className="w-5 h-5" />
              Excel dan import qilish
            </Link>
          </div>
        )}
      </motion.div>

      {/* Case Actions Modal */}
      <AnimatePresence>
        {showModal && selectedCase && (
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
                <h3 className="font-display font-semibold">Holat amallari</h3>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-2 rounded-lg hover:bg-white/10"
                >
                  <HiOutlineX className="w-5 h-5" />
                </button>
              </div>

              <div className="mb-4 p-4 rounded-xl bg-ocean-800/50">
                <h4 className="font-medium mb-1 line-clamp-2">{selectedCase.sarlavha}</h4>
                <p className="text-sm text-slate-400 line-clamp-2">
                  {selectedCase.klinik_stsenariy || selectedCase.savol}
                </p>
              </div>

              <div className="space-y-3">
                <Link
                  to={`/holat/${selectedCase.id}`}
                  className="w-full flex items-center gap-3 p-4 rounded-xl bg-ocean-700/50 hover:bg-ocean-700 transition-colors"
                >
                  <HiOutlineEye className="w-5 h-5 text-slate-400" />
                  <span>Ko'rish</span>
                </Link>

                <button
                  onClick={() => handleDelete(selectedCase.id)}
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
