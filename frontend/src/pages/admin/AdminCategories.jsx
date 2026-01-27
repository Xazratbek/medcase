import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../../utils/api'
import toast from 'react-hot-toast'
import {
  HiOutlineCollection,
  HiOutlinePlus,
  HiOutlineDotsVertical,
  HiOutlineTrash,
  HiOutlinePencil,
  HiOutlineArrowLeft,
  HiOutlineChevronRight,
  HiOutlineChevronDown,
  HiOutlineX,
  HiOutlineFolder,
  HiOutlineFolderOpen
} from 'react-icons/hi'

export default function AdminCategories() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandedCategories, setExpandedCategories] = useState({})
  const [expandedSubCategories, setExpandedSubCategories] = useState({})
  const [showModal, setShowModal] = useState(false)
  const [modalType, setModalType] = useState('category') // category, subcategory, section
  const [parentId, setParentId] = useState(null)
  const [editItem, setEditItem] = useState(null)
  const [formData, setFormData] = useState({ nomi: '', tavsif: '', rang: '#3B82F6' })
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    setLoading(true)
    try {
      const response = await api.get('/kategoriya/toliq')
      setCategories(response.data.kategoriyalar || response.data || [])
    } catch (error) {
      toast.error("Kategoriyalarni yuklashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const toggleCategory = (catId) => {
    setExpandedCategories(prev => ({ ...prev, [catId]: !prev[catId] }))
  }

  const toggleSubCategory = (subCatId) => {
    setExpandedSubCategories(prev => ({ ...prev, [subCatId]: !prev[subCatId] }))
  }

  const openCreateModal = (type, parentId = null) => {
    setModalType(type)
    setParentId(parentId)
    setEditItem(null)
    setFormData({ nomi: '', tavsif: '', rang: '#3B82F6' })
    setShowModal(true)
  }

  const openEditModal = (type, item, parentId = null) => {
    setModalType(type)
    setParentId(parentId)
    setEditItem(item)
    setFormData({
      nomi: item.nomi || '',
      tavsif: item.tavsif || '',
      rang: item.rang || '#3B82F6'
    })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.nomi.trim()) {
      toast.error("Nom kiritilishi shart")
      return
    }

    setActionLoading(true)
    try {
      if (modalType === 'category') {
        if (editItem) {
          await api.put(`/admin/kategoriya/asosiy/${editItem.id}`, formData)
          toast.success("Kategoriya yangilandi")
        } else {
          await api.post('/admin/kategoriya/asosiy', formData)
          toast.success("Kategoriya yaratildi")
        }
      } else if (modalType === 'subcategory') {
        const data = { ...formData, kategoriya_id: parentId }
        if (editItem) {
          await api.put(`/admin/kategoriya/kichik/${editItem.id}`, data)
          toast.success("Kichik kategoriya yangilandi")
        } else {
          await api.post('/admin/kategoriya/kichik', data)
          toast.success("Kichik kategoriya yaratildi")
        }
      } else if (modalType === 'section') {
        const data = { ...formData, kichik_kategoriya_id: parentId }
        if (editItem) {
          await api.put(`/admin/kategoriya/bolim/${editItem.id}`, data)
          toast.success("Bo'lim yangilandi")
        } else {
          await api.post('/admin/kategoriya/bolim', data)
          toast.success("Bo'lim yaratildi")
        }
      }
      
      setShowModal(false)
      loadCategories()
    } catch (error) {
      toast.error(error.response?.data?.detail || "Xatolik yuz berdi")
    } finally {
      setActionLoading(false)
    }
  }

  const handleDelete = async (type, id) => {
    if (!confirm("Rostdan ham o'chirmoqchimisiz?")) return

    setActionLoading(true)
    try {
      if (type === 'category') {
        await api.delete(`/admin/kategoriya/asosiy/${id}`)
      } else if (type === 'subcategory') {
        await api.delete(`/admin/kategoriya/kichik/${id}`)
      } else if (type === 'section') {
        await api.delete(`/admin/kategoriya/bolim/${id}`)
      }
      toast.success("O'chirildi")
      loadCategories()
    } catch (error) {
      toast.error(error.response?.data?.detail || "O'chirishda xatolik")
    } finally {
      setActionLoading(false)
    }
  }

  const getModalTitle = () => {
    const action = editItem ? "Tahrirlash" : "Yaratish"
    if (modalType === 'category') return `Kategoriya ${action.toLowerCase()}`
    if (modalType === 'subcategory') return `Kichik kategoriya ${action.toLowerCase()}`
    return `Bo'lim ${action.toLowerCase()}`
  }

  return (
    <div className="max-w-5xl mx-auto">
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
            <h1 className="text-3xl font-display font-bold">Kategoriyalar</h1>
            <p className="text-slate-400 mt-1">Kategoriya, kichik kategoriya va bo'limlar</p>
          </div>
          <button
            onClick={() => openCreateModal('category')}
            className="btn-primary flex items-center gap-2"
          >
            <HiOutlinePlus className="w-5 h-5" />
            <span className="hidden sm:inline">Yangi kategoriya</span>
          </button>
        </div>
      </motion.div>

      {/* Categories Tree */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card overflow-hidden"
      >
        {loading ? (
          <div className="p-8 space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 skeleton rounded-xl" />
            ))}
          </div>
        ) : categories.length > 0 ? (
          <div className="divide-y divide-white/5">
            {categories.map((category) => (
              <div key={category.id} className="group">
                {/* Main Category */}
                <div className="flex items-center gap-3 p-4 hover:bg-white/5 transition-colors">
                  <button
                    onClick={() => toggleCategory(category.id)}
                    className="p-1 rounded hover:bg-white/10 transition-colors"
                  >
                    {expandedCategories[category.id] ? (
                      <HiOutlineChevronDown className="w-5 h-5 text-slate-400" />
                    ) : (
                      <HiOutlineChevronRight className="w-5 h-5 text-slate-400" />
                    )}
                  </button>
                  
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${category.rang || '#3B82F6'}20` }}
                  >
                    <HiOutlineCollection className="w-5 h-5" style={{ color: category.rang || '#3B82F6' }} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium">{category.nomi}</h3>
                    <p className="text-sm text-slate-500">
                      {category.kichik_kategoriyalar?.length || 0} kichik kategoriya • {category.holatlar_soni || 0} holat
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => openCreateModal('subcategory', category.id)}
                      className="p-2 rounded-lg hover:bg-white/10 text-med-400"
                      title="Kichik kategoriya qo'shish"
                    >
                      <HiOutlinePlus className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openEditModal('category', category)}
                      className="p-2 rounded-lg hover:bg-white/10 text-slate-400"
                      title="Tahrirlash"
                    >
                      <HiOutlinePencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete('category', category.id)}
                      className="p-2 rounded-lg hover:bg-white/10 text-red-400"
                      title="O'chirish"
                    >
                      <HiOutlineTrash className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Sub Categories */}
                <AnimatePresence>
                  {expandedCategories[category.id] && category.kichik_kategoriyalar?.length > 0 && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden bg-ocean-800/30"
                    >
                      {category.kichik_kategoriyalar.map((subCat) => (
                        <div key={subCat.id}>
                          {/* Sub Category */}
                          <div className="flex items-center gap-3 p-3 pl-14 hover:bg-white/5 transition-colors group/sub">
                            <button
                              onClick={() => toggleSubCategory(subCat.id)}
                              className="p-1 rounded hover:bg-white/10 transition-colors"
                            >
                              {expandedSubCategories[subCat.id] ? (
                                <HiOutlineChevronDown className="w-4 h-4 text-slate-400" />
                              ) : (
                                <HiOutlineChevronRight className="w-4 h-4 text-slate-400" />
                              )}
                            </button>
                            
                            <HiOutlineFolderOpen className="w-5 h-5 text-gold-400" />
                            
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium text-sm">{subCat.nomi}</h4>
                              <p className="text-xs text-slate-500">
                                {subCat.bolimlar?.length || 0} bo'lim
                              </p>
                            </div>
                            
                            <div className="flex items-center gap-1 opacity-0 group-hover/sub:opacity-100 transition-opacity">
                              <button
                                onClick={() => openCreateModal('section', subCat.id)}
                                className="p-1.5 rounded-lg hover:bg-white/10 text-med-400"
                                title="Bo'lim qo'shish"
                              >
                                <HiOutlinePlus className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => openEditModal('subcategory', subCat, category.id)}
                                className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400"
                              >
                                <HiOutlinePencil className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDelete('subcategory', subCat.id)}
                                className="p-1.5 rounded-lg hover:bg-white/10 text-red-400"
                              >
                                <HiOutlineTrash className="w-4 h-4" />
                              </button>
                            </div>
                          </div>

                          {/* Sections */}
                          <AnimatePresence>
                            {expandedSubCategories[subCat.id] && subCat.bolimlar?.length > 0 && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="overflow-hidden"
                              >
                                {subCat.bolimlar.map((section) => (
                                  <div
                                    key={section.id}
                                    className="flex items-center gap-3 p-2.5 pl-24 hover:bg-white/5 transition-colors group/section"
                                  >
                                    <HiOutlineFolder className="w-4 h-4 text-slate-500" />
                                    
                                    <div className="flex-1 min-w-0">
                                      <p className="text-sm">{section.nomi}</p>
                                      <p className="text-xs text-slate-500">{section.holatlar_soni || 0} holat</p>
                                    </div>
                                    
                                    <div className="flex items-center gap-1 opacity-0 group-hover/section:opacity-100 transition-opacity">
                                      <button
                                        onClick={() => openEditModal('section', section, subCat.id)}
                                        className="p-1 rounded-lg hover:bg-white/10 text-slate-400"
                                      >
                                        <HiOutlinePencil className="w-3.5 h-3.5" />
                                      </button>
                                      <button
                                        onClick={() => handleDelete('section', section.id)}
                                        className="p-1 rounded-lg hover:bg-white/10 text-red-400"
                                      >
                                        <HiOutlineTrash className="w-3.5 h-3.5" />
                                      </button>
                                    </div>
                                  </div>
                                ))}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <HiOutlineCollection className="w-16 h-16 mx-auto text-slate-600 mb-4" />
            <p className="text-slate-400 mb-4">Kategoriyalar topilmadi</p>
            <button
              onClick={() => openCreateModal('category')}
              className="btn-primary inline-flex items-center gap-2"
            >
              <HiOutlinePlus className="w-5 h-5" />
              Birinchi kategoriyani yarating
            </button>
          </div>
        )}
      </motion.div>

      {/* Create/Edit Modal */}
      <AnimatePresence>
        {showModal && (
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
                <h3 className="font-display font-semibold text-lg">{getModalTitle()}</h3>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-2 rounded-lg hover:bg-white/10"
                >
                  <HiOutlineX className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">Nomi *</label>
                  <input
                    type="text"
                    value={formData.nomi}
                    onChange={(e) => setFormData(prev => ({ ...prev, nomi: e.target.value }))}
                    placeholder="Masalan: Fiziologiya"
                    className="input-field w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-400 mb-2">Tavsif</label>
                  <textarea
                    value={formData.tavsif}
                    onChange={(e) => setFormData(prev => ({ ...prev, tavsif: e.target.value }))}
                    placeholder="Qisqacha tavsif..."
                    rows={3}
                    className="input-field w-full resize-none"
                  />
                </div>

                {modalType === 'category' && (
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Rang</label>
                    <div className="flex items-center gap-3">
                      <input
                        type="color"
                        value={formData.rang}
                        onChange={(e) => setFormData(prev => ({ ...prev, rang: e.target.value }))}
                        className="w-12 h-10 rounded-lg cursor-pointer border-0 bg-transparent"
                      />
                      <input
                        type="text"
                        value={formData.rang}
                        onChange={(e) => setFormData(prev => ({ ...prev, rang: e.target.value }))}
                        placeholder="#3B82F6"
                        className="input-field flex-1"
                      />
                    </div>
                  </div>
                )}

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn-secondary flex-1"
                  >
                    Bekor qilish
                  </button>
                  <button
                    type="submit"
                    disabled={actionLoading}
                    className="btn-primary flex-1"
                  >
                    {actionLoading ? 'Saqlanmoqda...' : editItem ? 'Saqlash' : 'Yaratish'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
