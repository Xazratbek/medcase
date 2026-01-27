import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { caseAPI, takrorlashAPI } from '../utils/api'
import {
  HiOutlineArrowLeft,
  HiOutlineBookmark,
  HiOutlineBookmarkAlt,
  HiOutlineShare,
  HiOutlineFlag,
  HiOutlinePlay,
  HiOutlinePhotograph,
  HiOutlineVideoCamera,
  HiOutlineTag,
  HiOutlineRefresh
} from 'react-icons/hi'
import toast from 'react-hot-toast'
import CommentSection from '../components/comments/CommentSection'

// Video URL ni detect qilish
const isVideoUrl = (url) => {
  if (!url) return false
  const videoPatterns = [
    /youtube\.com\/watch/i,
    /youtu\.be\//i,
    /vimeo\.com/i,
    /\.mp4$/i,
    /\.webm$/i,
    /\.mov$/i,
  ]
  return videoPatterns.some(pattern => pattern.test(url))
}

// YouTube embed URL ga o'zgartirish
const getEmbedUrl = (url) => {
  if (!url) return null
  
  // YouTube
  const youtubeMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/)
  if (youtubeMatch) {
    return `https://www.youtube.com/embed/${youtubeMatch[1]}`
  }
  
  // Vimeo
  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/)
  if (vimeoMatch) {
    return `https://player.vimeo.com/video/${vimeoMatch[1]}`
  }
  
  // Direct video URL
  if (url.match(/\.(mp4|webm|mov)$/i)) {
    return url
  }
  
  return url
}

// Media komponenti
function MediaItem({ item }) {
  const url = item.url
  const isVideo = item.turi === 'VIDEO' || item.turi === 'video' || isVideoUrl(url)
  const embedUrl = getEmbedUrl(url)
  
  if (isVideo) {
    // YouTube/Vimeo embed
    if (embedUrl?.includes('youtube.com/embed') || embedUrl?.includes('vimeo.com')) {
      return (
        <div className="rounded-xl overflow-hidden bg-ocean-800">
          <div className="aspect-video">
            <iframe
              src={embedUrl}
              title={item.nom || 'Video'}
              className="w-full h-full"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
          {item.tavsif && (
            <p className="p-3 text-sm text-slate-400 border-t border-white/5">{item.tavsif}</p>
          )}
        </div>
      )
    }
    
    // Direct video
    return (
      <div className="rounded-xl overflow-hidden bg-ocean-800">
        <video
          src={embedUrl}
          controls
          className="w-full aspect-video"
          poster={item.thumbnail}
        >
          Brauzeringiz video qo'llab-quvvatlamaydi
        </video>
        {item.tavsif && (
          <p className="p-3 text-sm text-slate-400 border-t border-white/5">{item.tavsif}</p>
        )}
      </div>
    )
  }
  
  // Rasm
  return (
    <div className="rounded-xl overflow-hidden bg-ocean-800">
      <a href={url} target="_blank" rel="noopener noreferrer" className="block">
        <img
          src={url}
          alt={item.nom || item.tavsif || 'Rasm'}
          className="w-full max-h-96 object-contain bg-black/20"
          loading="lazy"
        />
      </a>
      {item.tavsif && (
        <p className="p-3 text-sm text-slate-400 border-t border-white/5">{item.tavsif}</p>
      )}
    </div>
  )
}

export default function CaseDetail() {
  const { id } = useParams()
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [bookmarked, setBookmarked] = useState(false)
  const [addingToRepeat, setAddingToRepeat] = useState(false)

  useEffect(() => {
    loadCase()
  }, [id])

  const loadCase = async () => {
    try {
      const response = await caseAPI.getById(id)
      // API returns HolatJavob directly, not wrapped in malumot
      const data = response.data
      setCaseData(data)
      setBookmarked(data?.xatcholangan || false)
    } catch (error) {
      console.error('Case loading error:', error)
      toast.error("Holatni yuklashda xatolik")
    } finally {
      setLoading(false)
    }
  }

  const handleBookmark = async () => {
    try {
      if (bookmarked) {
        await caseAPI.removeBookmark(id)
        toast.success("Xatcholardan olib tashlandi")
      } else {
        await caseAPI.bookmark(id)
        toast.success("Xatcholarga qo'shildi")
      }
      setBookmarked(!bookmarked)
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const handleAddToRepeat = async () => {
    setAddingToRepeat(true)
    try {
      await takrorlashAPI.addCase(id)
      toast.success("Takrorlash kartasiga qo'shildi")
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    } finally {
      setAddingToRepeat(false)
    }
  }

  const getDifficultyStyle = (difficulty) => {
    switch (difficulty?.toUpperCase()) {
      case 'OSON': return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'ORTACHA': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'QIYIN': return 'bg-red-500/20 text-red-400 border-red-500/30'
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30'
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="h-8 skeleton rounded w-32" />
        <div className="h-64 skeleton rounded-2xl" />
        <div className="h-32 skeleton rounded-2xl" />
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl font-medium">Holat topilmadi</h2>
        <Link to="/holatlar" className="btn-primary mt-4 inline-flex">
          Holatlarga qaytish
        </Link>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto"
    >
      {/* Back button */}
      <Link
        to="/holatlar"
        className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6"
      >
        <HiOutlineArrowLeft className="w-5 h-5" />
        <span>Holatlarga qaytish</span>
      </Link>

      {/* Header */}
      <div className="glass-card p-6 lg:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className={`badge ${getDifficultyStyle(caseData.qiyinlik)}`}>
              {caseData.qiyinlik}
            </span>
            <span className="badge-primary">{caseData.kichik_kategoriya_nomi || caseData.bolim_nomi}</span>
            {caseData.turi && (
              <span className="text-sm text-slate-500">{caseData.turi}</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleBookmark}
              className={`p-2.5 rounded-xl transition-colors ${
                bookmarked 
                  ? 'bg-med-500/20 text-med-400' 
                  : 'bg-ocean-700/50 text-slate-400 hover:text-white'
              }`}
            >
              {bookmarked ? <HiOutlineBookmarkAlt className="w-5 h-5" /> : <HiOutlineBookmark className="w-5 h-5" />}
            </button>
            <button className="p-2.5 rounded-xl bg-ocean-700/50 text-slate-400 hover:text-white transition-colors">
              <HiOutlineShare className="w-5 h-5" />
            </button>
            <button className="p-2.5 rounded-xl bg-ocean-700/50 text-slate-400 hover:text-red-400 transition-colors">
              <HiOutlineFlag className="w-5 h-5" />
            </button>
            <button
              onClick={handleAddToRepeat}
              disabled={addingToRepeat}
              className="p-2.5 rounded-xl bg-ocean-700/50 text-slate-400 hover:text-med-400 transition-colors disabled:opacity-50"
              title="Takrorlash kartasiga qo'shish"
            >
              {addingToRepeat ? (
                <div className="w-5 h-5 border-2 border-med-400/30 border-t-med-400 rounded-full animate-spin" />
              ) : (
                <HiOutlineRefresh className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Scenario */}
        <div className="mt-6">
          <h1 className="text-xl lg:text-2xl font-display font-bold">
            {caseData.sarlavha || 'Klinik holat'}
          </h1>
          
          <div className="mt-6 prose prose-invert max-w-none">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
              Klinik ssenariy
            </h3>
            <p className="text-slate-300 leading-relaxed whitespace-pre-line">
              {caseData.klinik_stsenariy}
            </p>
          </div>
          
          {/* Savol */}
          {caseData.savol && (
            <div className="mt-6 p-4 bg-med-500/10 border border-med-500/20 rounded-xl">
              <h3 className="text-sm font-medium text-med-400 uppercase tracking-wider mb-2">
                Savol
              </h3>
              <p className="text-white font-medium">
                {caseData.savol}
              </p>
            </div>
          )}
        </div>

        {/* Media - Video va Rasm */}
        {caseData.media && caseData.media.length > 0 && (
          <div className="mt-8">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">
              Media materiallar
            </h3>
            <div className="space-y-4">
              {caseData.media.map((item, index) => (
                <MediaItem key={index} item={item} />
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {caseData.teglar && caseData.teglar.length > 0 && (
          <div className="mt-8 flex flex-wrap items-center gap-2">
            <HiOutlineTag className="w-4 h-4 text-slate-500" />
            {caseData.teglar.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 rounded-full bg-ocean-700/50 text-sm text-slate-400"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Action */}
        <div className="mt-8 pt-6 border-t border-white/5">
          <Link
            to={`/holat/${id}/yechish`}
            className="btn-primary w-full lg:w-auto flex items-center justify-center gap-2 py-4"
          >
            <HiOutlinePlay className="w-5 h-5" />
            <span>Holatni yechish</span>
          </Link>
        </div>

        {/* Comment Section */}
        <CommentSection holatId={id} />
      </div>
    </motion.div>
  )
}
