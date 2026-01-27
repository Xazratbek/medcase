import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { categoryAPI } from '../utils/api'
import {
  HiOutlineArrowLeft,
  HiOutlineChevronRight,
  HiOutlineCollection,
  HiOutlineDocumentText
} from 'react-icons/hi'

export default function Sections() {
  const { kategoriyaId } = useParams()
  const [category, setCategory] = useState(null)
  const [sections, setSections] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [kategoriyaId])

  const loadData = async () => {
    try {
      // Kichik kategoriya ma'lumotlari
      const catResponse = await categoryAPI.getSubcategoryDetail(kategoriyaId)
      console.log('Category response:', catResponse.data)
      setCategory(catResponse.data)
      
      // Bo'limlar
      const sectionsResponse = await categoryAPI.getSections(kategoriyaId)
      console.log('Sections response:', sectionsResponse.data)
      // Bo'limlar massiv yoki {bolimlar: []} formatda kelishi mumkin
      const bolimlar = Array.isArray(sectionsResponse.data) 
        ? sectionsResponse.data 
        : (sectionsResponse.data?.bolimlar || [])
      setSections(bolimlar)
    } catch (error) {
      console.error('Sections loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 skeleton rounded w-48" />
        <div className="h-24 skeleton rounded-2xl" />
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-32 skeleton rounded-xl" />
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
      {/* Back button */}
      <Link
        to="/kategoriyalar"
        className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
      >
        <HiOutlineArrowLeft className="w-5 h-5" />
        <span>Kategoriyalarga qaytish</span>
      </Link>

      {/* Header */}
      {category && (
        <div className="glass-card p-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-med-500/20 to-med-600/20 flex items-center justify-center">
              <HiOutlineCollection className="w-8 h-8 text-med-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-display font-bold">{category.nomi}</h1>
              {category.tavsif && (
                <p className="text-slate-400 mt-1">{category.tavsif}</p>
              )}
              <div className="flex items-center gap-4 mt-3">
                <span className="text-sm text-slate-500">
                  {sections.length} bo'lim
                </span>
                <span className="text-sm text-slate-500">
                  {category.holatlar_soni || 0} holat
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Sections Grid */}
      {sections.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sections.map((section, index) => (
            <motion.div
              key={section.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link
                to={`/holatlar?bolim_id=${section.id}`}
                className="glass-card p-5 block hover:bg-white/5 transition-colors group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-display font-semibold group-hover:text-med-400 transition-colors">
                      {section.nomi}
                    </h3>
                    {section.tavsif && (
                      <p className="text-sm text-slate-500 mt-1 line-clamp-2">
                        {section.tavsif}
                      </p>
                    )}
                  </div>
                  <HiOutlineChevronRight className="w-5 h-5 text-slate-500 group-hover:text-med-400 transition-colors flex-shrink-0 ml-3" />
                </div>
                
                {/* Stats */}
                <div className="flex items-center gap-4 mt-4 pt-4 border-t border-white/5">
                  <div className="flex items-center gap-2">
                    <HiOutlineDocumentText className="w-4 h-4 text-slate-500" />
                    <span className="text-sm text-slate-400">{section.holatlar_soni || 0} holat</span>
                  </div>
                  {section.qiyin_holatlar > 0 && (
                    <span className="text-xs px-2 py-1 rounded-full bg-red-500/20 text-red-400">
                      {section.qiyin_holatlar} qiyin
                    </span>
                  )}
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="w-20 h-20 mx-auto rounded-full bg-ocean-800 flex items-center justify-center">
            <HiOutlineCollection className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="mt-4 text-lg font-medium">Bo'limlar yo'q</h3>
          <p className="mt-2 text-slate-500">Bu kategoriyada hali bo'limlar yaratilmagan</p>
        </div>
      )}
    </motion.div>
  )
}
