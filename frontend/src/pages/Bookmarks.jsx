import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { caseAPI } from '../utils/api'
import {
  HiOutlineBookmark,
  HiOutlineTrash,
  HiOutlinePlay,
  HiOutlineSearch,
  HiOutlineFolderOpen
} from 'react-icons/hi'
import toast from 'react-hot-toast'

export default function Bookmarks() {
  const [bookmarks, setBookmarks] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadBookmarks()
  }, [])

  const loadBookmarks = async () => {
    try {
      const response = await caseAPI.getBookmarks()
      setBookmarks(response.data.malumot?.elementlar || [])
    } catch (error) {
      console.error('Bookmarks loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  const removeBookmark = async (id) => {
    try {
      await caseAPI.removeBookmark(id)
      setBookmarks(prev => prev.filter(b => b.id !== id))
      toast.success("Xatchodan olib tashlandi")
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const filteredBookmarks = bookmarks.filter(b =>
    b.sarlavha?.toLowerCase().includes(search.toLowerCase()) ||
    b.kategoriya_nomi?.toLowerCase().includes(search.toLowerCase())
  )

  const getDifficultyStyle = (difficulty) => {
    switch (difficulty?.toUpperCase()) {
      case 'OSON': return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'ORTACHA': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'QIYIN': return 'bg-red-500/20 text-red-400 border-red-500/30'
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30'
    }
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
          <h1 className="text-2xl lg:text-3xl font-display font-bold flex items-center gap-3">
            <HiOutlineBookmark className="w-8 h-8 text-med-400" />
            Xatcholar
          </h1>
          <p className="text-slate-400 mt-1">Saqlangan holatlar</p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <HiOutlineSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Qidirish..."
            className="input-field pl-12"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="glass-card p-4 flex items-center justify-between">
        <span className="text-slate-400">Jami saqlangan</span>
        <span className="font-display font-bold text-lg">{bookmarks.length}</span>
      </div>

      {/* Bookmarks List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-24 skeleton rounded-2xl" />
          ))}
        </div>
      ) : filteredBookmarks.length > 0 ? (
        <div className="space-y-4">
          {filteredBookmarks.map((bookmark, index) => (
            <motion.div
              key={bookmark.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-card p-5 flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <span className={`badge text-xs ${getDifficultyStyle(bookmark.qiyinlik)}`}>
                    {bookmark.qiyinlik}
                  </span>
                  <span className="text-sm text-slate-500">{bookmark.kategoriya_nomi}</span>
                </div>
                <h3 className="font-display font-semibold truncate">
                  {bookmark.sarlavha || bookmark.savol?.substring(0, 60) + '...'}
                </h3>
                <p className="text-sm text-slate-400 mt-1 line-clamp-1">
                  {bookmark.ssenariy?.substring(0, 100)}...
                </p>
              </div>

              <div className="flex items-center gap-2 sm:flex-shrink-0">
                <Link
                  to={`/holat/${bookmark.id}/yechish`}
                  className="btn-primary py-2 px-4 flex items-center gap-2"
                >
                  <HiOutlinePlay className="w-4 h-4" />
                  <span>Yechish</span>
                </Link>
                <button
                  onClick={() => removeBookmark(bookmark.id)}
                  className="p-2.5 rounded-xl bg-ocean-700/50 text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <HiOutlineTrash className="w-5 h-5" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="w-20 h-20 mx-auto rounded-full bg-ocean-800 flex items-center justify-center">
            <HiOutlineFolderOpen className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="mt-4 text-lg font-medium">
            {search ? 'Topilmadi' : 'Xatcholar bo\'sh'}
          </h3>
          <p className="mt-2 text-slate-500">
            {search ? 'Qidiruv so\'zini o\'zgartiring' : 'Holatlarni saqlash uchun xatcho belgisini bosing'}
          </p>
          {!search && (
            <Link to="/holatlar" className="btn-primary mt-4 inline-flex">
              Holatlarni ko'rish
            </Link>
          )}
        </div>
      )}
    </motion.div>
  )
}
