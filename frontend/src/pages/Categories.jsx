import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { categoryAPI } from '../utils/api'
import { HiOutlineChevronRight, HiOutlineSearch, HiOutlineCollection } from 'react-icons/hi'

const categoryIcons = {
  'Fundamental fanlar': '🔬',
  'Klinik fanlar': '🏥',
  'Diagnostika': '🩺',
  'Anatomiya': '🦴',
  'Fiziologiya': '💓',
  'Biokimyo': '🧪',
  'Farmakologiya': '💊',
  'Mikrobiologiya': '🦠',
  'Patologiya': '🔍',
  'Ichki kasalliklar': '🫀',
  'Jarrohlik': '🔪',
  'Pediatriya': '👶',
  'Ginekologiya': '🤰',
  'Nevrologiya': '🧠',
  'default': '📚'
}

export default function Categories() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await categoryAPI.getAll()
      // Backend asosiy_kategoriyalar maydonini qaytaradi
      const data = response.data
      setCategories(data.asosiy_kategoriyalar || data.malumot || data || [])
    } catch (error) {
      console.error('Categories loading error:', error)
      setCategories([])
    } finally {
      setLoading(false)
    }
  }

  const filteredCategories = categories.filter(cat =>
    cat.nomi.toLowerCase().includes(search.toLowerCase()) ||
    cat.kichik_kategoriyalar?.some(sub => 
      sub.nomi.toLowerCase().includes(search.toLowerCase())
    )
  )

  const getIcon = (name) => categoryIcons[name] || categoryIcons.default

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-12 skeleton rounded-xl w-64" />
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
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
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-display font-bold">Kategoriyalar</h1>
          <p className="text-slate-400 mt-1">Tibbiyot sohalari bo'yicha o'rganing</p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <HiOutlineSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Kategoriya qidirish..."
            className="input-field pl-12"
          />
        </div>
      </div>

      {/* Categories Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCategories.map((category, index) => (
          <motion.div
            key={category.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="glass-card overflow-hidden"
          >
            {/* Category Header */}
            <div 
              className="p-6 cursor-pointer hover:bg-white/5 transition-colors"
              onClick={() => setExpandedId(expandedId === category.id ? null : category.id)}
            >
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-med-500/20 to-med-600/20 flex items-center justify-center text-2xl">
                  {getIcon(category.nomi)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-display font-semibold text-lg">{category.nomi}</h3>
                  <p className="text-sm text-slate-500 mt-1 line-clamp-2">{category.tavsif}</p>
                </div>
                <HiOutlineChevronRight 
                  className={`w-5 h-5 text-slate-500 transition-transform ${
                    expandedId === category.id ? 'rotate-90' : ''
                  }`}
                />
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 mt-4">
                <div className="flex items-center gap-2">
                  <HiOutlineCollection className="w-4 h-4 text-slate-500" />
                  <span className="text-sm text-slate-400">{category.holatlar_soni || 0} holat</span>
                </div>
                <div className="text-sm text-slate-500">
                  {category.kichik_kategoriyalar?.length || 0} bo'lim
                </div>
              </div>
            </div>

            {/* Subcategories (Expanded) */}
            <motion.div
              initial={false}
              animate={{ height: expandedId === category.id ? 'auto' : 0 }}
              className="overflow-hidden border-t border-white/5"
            >
              <div className="p-4 space-y-2">
                {category.kichik_kategoriyalar?.map((sub) => (
                  <Link
                    key={sub.id}
                    to={`/kategoriya/${sub.id}/bolimlar`}
                    className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{getIcon(sub.nomi)}</span>
                      <div>
                        <span className="font-medium">{sub.nomi}</span>
                        {sub.bolimlar_soni > 0 && (
                          <span className="ml-2 text-xs text-slate-500">({sub.bolimlar_soni} bo'lim)</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-slate-500">{sub.holatlar_soni || 0} holat</span>
                      <HiOutlineChevronRight className="w-4 h-4 text-slate-500 group-hover:text-med-400 transition-colors" />
                    </div>
                  </Link>
                ))}

                {(!category.kichik_kategoriyalar || category.kichik_kategoriyalar.length === 0) && (
                  <p className="text-center text-slate-500 py-4">Bo'limlar yo'q</p>
                )}
              </div>
            </motion.div>
          </motion.div>
        ))}
      </div>

      {filteredCategories.length === 0 && (
        <div className="text-center py-16">
          <div className="w-20 h-20 mx-auto rounded-full bg-ocean-800 flex items-center justify-center">
            <HiOutlineCollection className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="mt-4 text-lg font-medium">Kategoriya topilmadi</h3>
          <p className="mt-2 text-slate-500">Qidiruv so'zini o'zgartiring</p>
        </div>
      )}
    </motion.div>
  )
}
