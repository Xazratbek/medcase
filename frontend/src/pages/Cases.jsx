import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { caseAPI, categoryAPI } from '../utils/api'
import {
  HiOutlineSearch,
  HiOutlineFilter,
  HiOutlineDocumentText,
  HiOutlineBookmark,
  HiOutlinePlay,
  HiOutlineChevronDown,
  HiOutlineX,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineChat
} from 'react-icons/hi'

const difficulties = [
  { value: '', label: 'Barchasi', color: 'text-slate-400' },
  { value: 'oson', label: 'Oson', color: 'text-green-400', bgColor: 'bg-green-500/20' },
  { value: 'ortacha', label: "O'rtacha", color: 'text-yellow-400', bgColor: 'bg-yellow-500/20' },
  { value: 'qiyin', label: 'Qiyin', color: 'text-red-400', bgColor: 'bg-red-500/20' },
]

const ITEMS_PER_PAGE = 20

export default function Cases() {
  const [searchParams, setSearchParams] = useSearchParams()
  const bolimId = searchParams.get('bolim_id')
  
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [section, setSection] = useState(null)
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 0 })
  
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    difficulty: searchParams.get('qiyinlik') || '',
    sortBy: 'yaratilgan_vaqt',
    sortOrder: 'desc',
    showFilters: false
  })

  useEffect(() => {
    loadCases()
    if (bolimId) loadSection()
  }, [bolimId, pagination.page, filters.difficulty])

  const loadCases = async () => {
    setLoading(true)
    try {
      const params = {
        sahifa: pagination.page,
        hajm: ITEMS_PER_PAGE,
        qiyinlik: filters.difficulty || undefined,
        qidiruv: filters.search || undefined,
        bolim_id: bolimId || undefined,
        saralash: filters.sortBy || 'yaratilgan_vaqt',
        tartib: filters.sortOrder || 'desc'
      }
      const response = await caseAPI.getAll(params)
      const data = response.data.malumot || response.data
      setCases(data?.elementlar || data?.holatlar || [])
      setPagination(prev => ({
        ...prev,
        total: data?.jami || 0,
        pages: data?.sahifalar_soni || Math.ceil((data?.jami || 0) / ITEMS_PER_PAGE)
      }))
    } catch (error) {
      console.error('Cases loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSection = async () => {
    try {
      const response = await categoryAPI.getSectionDetail(bolimId)
      setSection(response.data)
    } catch (error) {
      console.error('Section loading error:', error)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    loadCases()
  }

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
      <div>
        <h1 className="text-2xl lg:text-3xl font-display font-bold">
          {section ? section.nomi : 'Barcha holatlar'}
        </h1>
        {section && (
          <p className="text-slate-400 mt-1">{section.tavsif}</p>
        )}
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <form onSubmit={handleSearch} className="flex-1 relative">
          <HiOutlineSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <input
            type="text"
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            placeholder="Holat qidirish..."
            className="input-field pl-12 pr-24"
          />
          <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 btn-primary py-2 px-4">
            Qidirish
          </button>
        </form>

        <button
          onClick={() => setFilters(prev => ({ ...prev, showFilters: !prev.showFilters }))}
          className={`btn-secondary flex items-center gap-2 ${filters.showFilters ? 'bg-white/10' : ''}`}
        >
          <HiOutlineFilter className="w-5 h-5" />
          <span>Filterlar</span>
          <HiOutlineChevronDown className={`w-4 h-4 transition-transform ${filters.showFilters ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Filters Panel */}
      {filters.showFilters && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-4 space-y-4"
        >
          {/* Qiyinlik */}
          <div className="flex flex-wrap items-center gap-4">
            <span className="text-sm text-slate-400 w-20">Qiyinlik:</span>
            <div className="flex flex-wrap gap-2">
              {difficulties.map((d) => (
                <button
                  key={d.value}
                  onClick={() => {
                    setFilters(prev => ({ ...prev, difficulty: d.value }))
                    setPagination(prev => ({ ...prev, page: 1 }))
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    filters.difficulty === d.value
                      ? `${d.bgColor || 'bg-med-500/20'} ${d.color} border border-current/30`
                      : 'bg-ocean-700/50 text-slate-400 hover:bg-ocean-700'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Saralash */}
          <div className="flex flex-wrap items-center gap-4">
            <span className="text-sm text-slate-400 w-20">Saralash:</span>
            <div className="flex flex-wrap gap-2">
              {[
                { value: 'yaratilgan_vaqt', label: 'Yangi' },
                { value: 'qiyinlik', label: 'Qiyinlik' },
                { value: 'urinishlar_soni', label: 'Mashhurligi' },
              ].map((s) => (
                <button
                  key={s.value}
                  onClick={() => {
                    setFilters(prev => ({
                      ...prev,
                      sortBy: s.value,
                      sortOrder: prev.sortBy === s.value && prev.sortOrder === 'desc' ? 'asc' : 'desc'
                    }))
                    setPagination(prev => ({ ...prev, page: 1 }))
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-1 ${
                    filters.sortBy === s.value
                      ? 'bg-med-500/20 text-med-400 border border-med-500/30'
                      : 'bg-ocean-700/50 text-slate-400 hover:bg-ocean-700'
                  }`}
                >
                  {s.label}
                  {filters.sortBy === s.value && (
                    <span className="text-xs">{filters.sortOrder === 'desc' ? '↓' : '↑'}</span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Tozalash */}
          {(filters.difficulty || filters.search) && (
            <div className="flex justify-end pt-2 border-t border-white/5">
              <button
                onClick={() => {
                  setFilters(prev => ({ ...prev, difficulty: '', search: '', sortBy: 'yaratilgan_vaqt', sortOrder: 'desc' }))
                  setPagination(prev => ({ ...prev, page: 1 }))
                }}
                className="text-sm text-slate-400 hover:text-white flex items-center gap-1"
              >
                <HiOutlineX className="w-4 h-4" />
                Filtrlarni tozalash
              </button>
            </div>
          )}
        </motion.div>
      )}

      {/* Cases Grid */}
      {loading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-56 skeleton rounded-2xl" />
          ))}
        </div>
      ) : cases.length > 0 ? (
        <>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cases.map((caseItem, index) => (
              <motion.div
                key={caseItem.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <CaseCard caseItem={caseItem} getDifficultyStyle={getDifficultyStyle} />
              </motion.div>
            ))}
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <Pagination
              currentPage={pagination.page}
              totalPages={pagination.pages}
              totalItems={pagination.total}
              onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
            />
          )}
        </>
      ) : (
        <div className="text-center py-16">
          <div className="w-20 h-20 mx-auto rounded-full bg-ocean-800 flex items-center justify-center">
            <HiOutlineDocumentText className="w-10 h-10 text-slate-500" />
          </div>
          <h3 className="mt-4 text-lg font-medium">Holatlar topilmadi</h3>
          <p className="mt-2 text-slate-500">Filterlarni o'zgartiring yoki boshqa kategoriyani tanlang</p>
        </div>
      )}
    </motion.div>
  )
}

// Pagination komponenti
function Pagination({ currentPage, totalPages, totalItems, onPageChange }) {
  const getPageNumbers = () => {
    const pages = []
    const showPages = 5 // Ko'rsatiladigan sahifalar soni
    
    let startPage = Math.max(1, currentPage - Math.floor(showPages / 2))
    let endPage = Math.min(totalPages, startPage + showPages - 1)
    
    if (endPage - startPage + 1 < showPages) {
      startPage = Math.max(1, endPage - showPages + 1)
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }
    
    return pages
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4">
      {/* Info */}
      <p className="text-sm text-slate-500">
        Jami <span className="font-medium text-white">{totalItems}</span> ta holat, 
        sahifa <span className="font-medium text-white">{currentPage}</span> / {totalPages}
      </p>
      
      {/* Buttons */}
      <div className="flex items-center gap-1">
        {/* Oldingi */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={`p-2 rounded-lg transition-colors ${
            currentPage === 1
              ? 'text-slate-600 cursor-not-allowed'
              : 'text-slate-400 hover:bg-ocean-700 hover:text-white'
          }`}
        >
          <HiOutlineChevronLeft className="w-5 h-5" />
        </button>
        
        {/* Birinchi sahifa */}
        {getPageNumbers()[0] > 1 && (
          <>
            <button
              onClick={() => onPageChange(1)}
              className="w-10 h-10 rounded-lg font-medium bg-ocean-700/50 text-slate-400 hover:bg-ocean-700 transition-colors"
            >
              1
            </button>
            {getPageNumbers()[0] > 2 && (
              <span className="px-2 text-slate-600">...</span>
            )}
          </>
        )}
        
        {/* Sahifalar */}
        {getPageNumbers().map((page) => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`w-10 h-10 rounded-lg font-medium transition-colors ${
              currentPage === page
                ? 'bg-med-500 text-white shadow-lg shadow-med-500/30'
                : 'bg-ocean-700/50 text-slate-400 hover:bg-ocean-700'
            }`}
          >
            {page}
          </button>
        ))}
        
        {/* Oxirgi sahifa */}
        {getPageNumbers()[getPageNumbers().length - 1] < totalPages && (
          <>
            {getPageNumbers()[getPageNumbers().length - 1] < totalPages - 1 && (
              <span className="px-2 text-slate-600">...</span>
            )}
            <button
              onClick={() => onPageChange(totalPages)}
              className="w-10 h-10 rounded-lg font-medium bg-ocean-700/50 text-slate-400 hover:bg-ocean-700 transition-colors"
            >
              {totalPages}
            </button>
          </>
        )}
        
        {/* Keyingi */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`p-2 rounded-lg transition-colors ${
            currentPage === totalPages
              ? 'text-slate-600 cursor-not-allowed'
              : 'text-slate-400 hover:bg-ocean-700 hover:text-white'
          }`}
        >
          <HiOutlineChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}

function CaseCard({ caseItem, getDifficultyStyle }) {
  return (
    <div className="case-card group h-full flex flex-col">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <span className={`badge ${getDifficultyStyle(caseItem.qiyinlik)} text-xs`}>
          {caseItem.qiyinlik}
        </span>
        <button className="p-2 -m-2 text-slate-500 hover:text-med-400 transition-colors">
          <HiOutlineBookmark className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 mt-4">
        <h3 className="font-display font-semibold line-clamp-2 group-hover:text-med-400 transition-colors">
          {caseItem.sarlavha || caseItem.savol?.substring(0, 60) + '...'}
        </h3>
        <p className="text-sm text-slate-400 mt-2 line-clamp-3">
          {(caseItem.klinik_stsenariy || caseItem.ssenariy)?.substring(0, 150)}...
        </p>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">{caseItem.kichik_kategoriya_nomi || caseItem.bolim_nomi || caseItem.kategoriya_nomi}</span>
            {caseItem.izohlar_soni > 0 && (
              <span className="flex items-center gap-1 text-xs text-slate-500">
                <HiOutlineChat className="w-3.5 h-3.5" />
                {caseItem.izohlar_soni}
              </span>
            )}
          </div>
          <Link
            to={`/holat/${caseItem.id}/yechish`}
            className="flex items-center gap-1 text-sm text-med-400 hover:text-med-300 font-medium"
          >
            <HiOutlinePlay className="w-4 h-4" />
            Yechish
          </Link>
        </div>
      </div>
    </div>
  )
}
