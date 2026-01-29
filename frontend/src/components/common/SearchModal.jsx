import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  HiOutlineSearch,
  HiOutlineX,
  HiOutlineDocumentText,
  HiOutlineCollection,
  HiOutlineUser,
  HiOutlineClock,
  HiOutlineArrowRight
} from 'react-icons/hi'
import { useDebounce } from '../../hooks'
import api from '../../utils/api'
import { formatQiyinlik } from '../../utils/format'

export default function SearchModal({ isOpen, onClose, initialQuery = '' }) {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [suggestions, setSuggestions] = useState([])
  const [recentSearches, setRecentSearches] = useState([])
  const [activeTab, setActiveTab] = useState('all')
  
  const debouncedQuery = useDebounce(query, 300)

  useEffect(() => {
    if (isOpen && initialQuery !== query) {
      setQuery(initialQuery)
    }
  }, [isOpen, initialQuery, query])

  // Focus input on open
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  // Load recent searches
  useEffect(() => {
    const saved = localStorage.getItem('recent_searches')
    if (saved) {
      setRecentSearches(JSON.parse(saved).slice(0, 5))
    }
  }, [isOpen])

  // Search on query change
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      performSearch(debouncedQuery)
    } else {
      setResults(null)
      setSuggestions([])
    }
  }, [debouncedQuery])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Escape to close
      if (e.key === 'Escape') {
        onClose()
      }
      // Ctrl/Cmd + K to open (handled in parent)
    }

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, onClose])

  const performSearch = async (searchQuery) => {
    setLoading(true)
    try {
      const response = await api.get('/qidiruv/', { params: { q: searchQuery } })
      setResults(response.data)
      
      // Also get suggestions
      const suggestResponse = await api.get('/qidiruv/taklif', { params: { q: searchQuery, limit: 5 } })
      setSuggestions(suggestResponse.data.takliflar || [])
    } catch (error) {
      console.error('Search error:', error)
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const saveRecentSearch = (searchTerm) => {
    const updated = [searchTerm, ...recentSearches.filter(s => s !== searchTerm)].slice(0, 5)
    setRecentSearches(updated)
    localStorage.setItem('recent_searches', JSON.stringify(updated))
  }

  const handleResultClick = (type, item) => {
    saveRecentSearch(query)
    onClose()
    
    switch (type) {
      case 'holat':
        navigate(`/holat/${item.id}`)
        break
      case 'kategoriya':
        navigate(`/holatlar/${item.id}`)
        break
      case 'foydalanuvchi':
        navigate(`/profil/${item.foydalanuvchi_nomi}`)
        break
      default:
        break
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.nom)
    handleResultClick(suggestion.turi, suggestion)
  }

  const clearRecentSearches = () => {
    setRecentSearches([])
    localStorage.removeItem('recent_searches')
  }

  const tabs = [
    { id: 'all', label: 'Barchasi' },
    { id: 'holatlar', label: 'Holatlar' },
    { id: 'kategoriyalar', label: 'Kategoriyalar' },
    { id: 'foydalanuvchilar', label: 'Foydalanuvchilar' },
  ]

  const getResultsForTab = () => {
    if (!results) return []
    
    switch (activeTab) {
      case 'holatlar':
        return results.holatlar?.natijalar || []
      case 'kategoriyalar':
        return results.kategoriyalar?.natijalar || []
      case 'foydalanuvchilar':
        return results.foydalanuvchilar?.natijalar || []
      default:
        return [
          ...(results.holatlar?.natijalar || []).map(r => ({ ...r, _type: 'holat' })),
          ...(results.kategoriyalar?.natijalar || []).map(r => ({ ...r, _type: 'kategoriya' })),
          ...(results.foydalanuvchilar?.natijalar || []).map(r => ({ ...r, _type: 'foydalanuvchi' })),
        ]
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'holat':
        return HiOutlineDocumentText
      case 'kategoriya':
        return HiOutlineCollection
      case 'foydalanuvchi':
        return HiOutlineUser
      default:
        return HiOutlineDocumentText
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'holat':
        return 'text-med-400 bg-med-500/20'
      case 'kategoriya':
        return 'text-purple-400 bg-purple-500/20'
      case 'foydalanuvchi':
        return 'text-gold-400 bg-gold-500/20'
      default:
        return 'text-slate-400 bg-slate-500/20'
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-[10vh] px-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl glass-card overflow-hidden"
        >
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-4 border-b border-white/5">
            <HiOutlineSearch className="w-6 h-6 text-slate-400 flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Holatlar, kategoriyalar yoki foydalanuvchilarni qidiring..."
              className="flex-1 bg-transparent text-lg outline-none placeholder:text-slate-500"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400"
              >
                <HiOutlineX className="w-5 h-5" />
              </button>
            )}
            <kbd className="hidden sm:inline-flex items-center px-2 py-1 rounded bg-ocean-700/50 text-xs text-slate-400 border border-white/10">
              ESC
            </kbd>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && query && (
            <div className="px-4 py-2 border-b border-white/5 flex flex-wrap gap-2">
              {suggestions.map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-ocean-700/50 hover:bg-ocean-700 text-sm transition-colors"
                >
                  {(() => {
                    const Icon = getTypeIcon(suggestion.turi)
                    return <Icon className="w-4 h-4 text-slate-400" />
                  })()}
                  <span>{suggestion.nom}</span>
                </button>
              ))}
            </div>
          )}

          {/* Tabs (when results exist) */}
          {results && (
            <div className="flex items-center gap-1 px-4 py-2 border-b border-white/5 overflow-x-auto scrollbar-hide">
              {tabs.map((tab) => {
                let count = 0
                if (results) {
                  switch (tab.id) {
                    case 'holatlar':
                      count = results.holatlar?.jami || 0
                      break
                    case 'kategoriyalar':
                      count = results.kategoriyalar?.jami || 0
                      break
                    case 'foydalanuvchilar':
                      count = results.foydalanuvchilar?.jami || 0
                      break
                    case 'all':
                      count = results.jami_topildi || 0
                      break
                  }
                }
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'bg-med-500/20 text-med-400'
                        : 'text-slate-400 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <span>{tab.label}</span>
                    {count > 0 && (
                      <span className="px-1.5 py-0.5 rounded-md bg-white/10 text-xs">
                        {count}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          )}

          {/* Content */}
          <div className="max-h-[50vh] overflow-y-auto">
            {loading ? (
              <div className="p-6 space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 skeleton rounded-xl" />
                ))}
              </div>
            ) : query && results ? (
              getResultsForTab().length > 0 ? (
                <div className="divide-y divide-white/5">
                  {getResultsForTab().map((item, index) => {
                    const type = item._type || activeTab.slice(0, -3) // Remove 'lar'
                    const Icon = getTypeIcon(type)
                    const colorClass = getTypeColor(type)
                    
                    return (
                      <button
                        key={`${type}-${item.id}-${index}`}
                        onClick={() => handleResultClick(type, item)}
                        className="w-full flex items-center gap-4 p-4 hover:bg-white/5 transition-colors text-left group"
                      >
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">
                            {item.sarlavha || item.nomi || item.toliq_ism || item.foydalanuvchi_nomi}
                          </p>
                          <p className="text-sm text-slate-500 truncate">
                            {item.tavsif || item.muassasa || item.kategoriya_nomi || ''}
                          </p>
                          {item.qiyinlik && (
                            <span className={`inline-block mt-1 text-xs font-mono uppercase ${
                              item.qiyinlik === 'oson' ? 'text-green-400' :
                              item.qiyinlik === 'orta' ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {formatQiyinlik(item.qiyinlik)}
                            </span>
                          )}
                        </div>
                        <HiOutlineArrowRight className="w-5 h-5 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    )
                  })}
                </div>
              ) : (
                <div className="p-8 text-center">
                  <HiOutlineSearch className="w-12 h-12 mx-auto text-slate-600" />
                  <p className="mt-3 text-slate-400">"{query}" bo'yicha natija topilmadi</p>
                  <p className="text-sm text-slate-500 mt-1">Boshqa so'zlar bilan qidirib ko'ring</p>
                </div>
              )
            ) : !query && recentSearches.length > 0 ? (
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm text-slate-500 font-medium">So'nggi qidiruvlar</p>
                  <button
                    onClick={clearRecentSearches}
                    className="text-xs text-slate-500 hover:text-white transition-colors"
                  >
                    Tozalash
                  </button>
                </div>
                <div className="space-y-1">
                  {recentSearches.map((search, i) => (
                    <button
                      key={i}
                      onClick={() => setQuery(search)}
                      className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors text-left"
                    >
                      <HiOutlineClock className="w-5 h-5 text-slate-500" />
                      <span className="text-slate-300">{search}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : !query ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 mx-auto rounded-full bg-ocean-700/50 flex items-center justify-center mb-3">
                  <HiOutlineSearch className="w-8 h-8 text-slate-500" />
                </div>
                <p className="text-slate-400">Qidirishni boshlang</p>
                <p className="text-sm text-slate-500 mt-1">Holatlar, kategoriyalar va foydalanuvchilarni toping</p>
              </div>
            ) : null}
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-ocean-700/50 border border-white/10">↵</kbd>
                tanlash
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-ocean-700/50 border border-white/10">↑↓</kbd>
                harakat
              </span>
            </div>
            <span>MedCase Pro qidiruv</span>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
