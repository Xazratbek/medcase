import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { izohAPI } from '../../utils/api'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'
import {
  HiOutlineChat,
  HiOutlineHeart,
  HiHeart,
  HiOutlineReply,
  HiOutlineDotsVertical,
  HiOutlineTrash,
  HiOutlinePencil,
  HiOutlinePaperAirplane,
  HiOutlineX,
  HiOutlineChevronDown,
  HiOutlineChevronUp
} from 'react-icons/hi'

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)
  
  if (seconds < 60) return 'hozirgina'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} daqiqa oldin`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} soat oldin`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)} kun oldin`
  return date.toLocaleDateString('uz-UZ')
}

function CommentInput({ onSubmit, placeholder = "Fikringizni yozing...", buttonText = "Yuborish", autoFocus = false, onCancel = null }) {
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim() || sending) return
    
    setSending(true)
    try {
      await onSubmit(text.trim())
      setText('')
    } finally {
      setSending(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative group">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          rows={3}
          className="w-full px-4 py-3.5 pr-24 rounded-2xl bg-ocean-800/60 border border-white/5 
                     text-white placeholder:text-slate-500 resize-none
                     focus:outline-none focus:border-med-500/40 focus:ring-2 focus:ring-med-500/10
                     transition-all duration-300"
        />
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
            >
              <HiOutlineX className="w-5 h-5" />
            </button>
          )}
          <button
            type="submit"
            disabled={!text.trim() || sending}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-med-500 text-white font-medium
                       hover:bg-med-400 disabled:opacity-50 disabled:cursor-not-allowed
                       transition-all duration-200 shadow-lg shadow-med-500/20"
          >
            {sending ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <HiOutlinePaperAirplane className="w-4 h-4 rotate-90" />
                <span className="text-sm">{buttonText}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  )
}

function SingleComment({ comment, onLike, onReply, onEdit, onDelete, currentUserId, level = 0 }) {
  const [showReplies, setShowReplies] = useState(level === 0)
  const [replying, setReplying] = useState(false)
  const [editing, setEditing] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [editText, setEditText] = useState(comment.matn)

  const isOwner = currentUserId === comment.foydalanuvchi_id
  const hasReplies = comment.javoblar && comment.javoblar.length > 0

  const handleReplySubmit = async (text) => {
    await onReply(comment.id, text)
    setReplying(false)
  }

  const handleEditSubmit = async (e) => {
    e.preventDefault()
    if (!editText.trim()) return
    await onEdit(comment.id, editText.trim())
    setEditing(false)
  }

  const getAvatarColor = (name) => {
    const colors = [
      'from-rose-500 to-pink-600',
      'from-violet-500 to-purple-600',
      'from-blue-500 to-cyan-600',
      'from-emerald-500 to-teal-600',
      'from-amber-500 to-orange-600',
      'from-med-500 to-med-600',
    ]
    const index = name ? name.charCodeAt(0) % colors.length : 0
    return colors[index]
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`${level > 0 ? 'ml-8 lg:ml-12 pl-4 border-l-2 border-ocean-700/50' : ''}`}
    >
      <div className="group relative">
        <div className="flex gap-3">
          {/* Avatar */}
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getAvatarColor(comment.foydalanuvchi?.ism)} 
                          flex items-center justify-center flex-shrink-0 shadow-lg`}>
            {comment.foydalanuvchi?.avatar_url ? (
              <img 
                src={comment.foydalanuvchi.avatar_url} 
                alt="" 
                className="w-full h-full rounded-xl object-cover" 
              />
            ) : (
              <span className="font-bold text-sm text-white">
                {comment.foydalanuvchi?.ism?.[0] || 'F'}
              </span>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-semibold text-white">
                {comment.foydalanuvchi?.ism} {comment.foydalanuvchi?.familiya}
              </span>
              <span className="text-xs text-slate-500">
                {formatTimeAgo(comment.yaratilgan_vaqt)}
              </span>
              {comment.tahrirlangan && (
                <span className="text-xs text-slate-600 italic">(tahrirlangan)</span>
              )}
            </div>

            {editing ? (
              <form onSubmit={handleEditSubmit} className="mt-2">
                <textarea
                  value={editText}
                  onChange={(e) => setEditText(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-ocean-800/80 border border-white/10 
                             text-white resize-none focus:outline-none focus:border-med-500/40"
                  rows={3}
                  autoFocus
                />
                <div className="flex gap-2 mt-2">
                  <button
                    type="submit"
                    className="px-3 py-1.5 rounded-lg bg-med-500 text-white text-sm font-medium hover:bg-med-400"
                  >
                    Saqlash
                  </button>
                  <button
                    type="button"
                    onClick={() => { setEditing(false); setEditText(comment.matn) }}
                    className="px-3 py-1.5 rounded-lg bg-ocean-700 text-slate-300 text-sm hover:bg-ocean-600"
                  >
                    Bekor
                  </button>
                </div>
              </form>
            ) : (
              <p className="mt-1 text-slate-300 whitespace-pre-wrap break-words">
                {comment.matn}
              </p>
            )}

            {/* Actions */}
            {!editing && (
              <div className="flex items-center gap-4 mt-3">
                <button
                  onClick={() => onLike(comment.id)}
                  className={`flex items-center gap-1.5 text-sm transition-all duration-200 
                             ${comment.yoqtirilgan 
                               ? 'text-rose-400' 
                               : 'text-slate-500 hover:text-rose-400'}`}
                >
                  {comment.yoqtirilgan ? (
                    <HiHeart className="w-4 h-4" />
                  ) : (
                    <HiOutlineHeart className="w-4 h-4" />
                  )}
                  <span>{comment.yoqtirishlar_soni || 0}</span>
                </button>

                {level < 2 && (
                  <button
                    onClick={() => setReplying(!replying)}
                    className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-med-400 transition-colors"
                  >
                    <HiOutlineReply className="w-4 h-4" />
                    <span>Javob</span>
                  </button>
                )}

                {hasReplies && (
                  <button
                    onClick={() => setShowReplies(!showReplies)}
                    className="flex items-center gap-1 text-sm text-slate-500 hover:text-white transition-colors"
                  >
                    {showReplies ? (
                      <HiOutlineChevronUp className="w-4 h-4" />
                    ) : (
                      <HiOutlineChevronDown className="w-4 h-4" />
                    )}
                    <span>{comment.javoblar_soni} javob</span>
                  </button>
                )}

                {isOwner && (
                  <div className="relative">
                    <button
                      onClick={() => setMenuOpen(!menuOpen)}
                      className="p-1 text-slate-500 hover:text-white transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <HiOutlineDotsVertical className="w-4 h-4" />
                    </button>

                    <AnimatePresence>
                      {menuOpen && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95, y: -10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.95, y: -10 }}
                          className="absolute right-0 top-full mt-1 z-10 min-w-[140px] py-2 
                                     bg-ocean-800 border border-white/10 rounded-xl shadow-xl"
                        >
                          <button
                            onClick={() => { setEditing(true); setMenuOpen(false) }}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-300 
                                       hover:bg-white/5 hover:text-white transition-colors"
                          >
                            <HiOutlinePencil className="w-4 h-4" />
                            Tahrirlash
                          </button>
                          <button
                            onClick={() => { onDelete(comment.id); setMenuOpen(false) }}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-400 
                                       hover:bg-red-500/10 transition-colors"
                          >
                            <HiOutlineTrash className="w-4 h-4" />
                            O'chirish
                          </button>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}
              </div>
            )}

            {/* Reply input */}
            <AnimatePresence>
              {replying && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4"
                >
                  <CommentInput
                    onSubmit={handleReplySubmit}
                    placeholder={`${comment.foydalanuvchi?.ism}ga javob yozing...`}
                    buttonText="Javob"
                    autoFocus
                    onCancel={() => setReplying(false)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Replies */}
        <AnimatePresence>
          {showReplies && hasReplies && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 space-y-4"
            >
              {comment.javoblar.map((reply) => (
                <SingleComment
                  key={reply.id}
                  comment={reply}
                  onLike={onLike}
                  onReply={onReply}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  currentUserId={currentUserId}
                  level={level + 1}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default function CommentSection({ holatId }) {
  const { user } = useAuthStore()
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)

  useEffect(() => {
    loadComments()
  }, [holatId, page])

  const loadComments = async () => {
    try {
      const response = await izohAPI.getByCase(holatId, { sahifa: page, hajm: 20 })
      const data = response.data
      setComments(data.izohlar || [])
      setTotal(data.jami || 0)
    } catch (error) {
      console.error('Comments loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateComment = async (text) => {
    try {
      await izohAPI.create({ holat_id: holatId, matn: text })
      toast.success("Izoh qo'shildi")
      loadComments()
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const handleReply = async (parentId, text) => {
    try {
      await izohAPI.create({ holat_id: holatId, matn: text, ota_izoh_id: parentId })
      toast.success("Javob qo'shildi")
      loadComments()
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const handleLike = async (commentId) => {
    try {
      await izohAPI.like(commentId)
      loadComments()
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const handleEdit = async (commentId, text) => {
    try {
      await izohAPI.update(commentId, { matn: text })
      toast.success("Izoh yangilandi")
      loadComments()
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  const handleDelete = async (commentId) => {
    if (!confirm("Rostdan ham o'chirmoqchimisiz?")) return
    try {
      await izohAPI.delete(commentId)
      toast.success("Izoh o'chirildi")
      loadComments()
    } catch (error) {
      toast.error("Xatolik yuz berdi")
    }
  }

  return (
    <div className="mt-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-purple-600/20 
                        flex items-center justify-center border border-violet-500/20">
          <HiOutlineChat className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h3 className="font-display font-semibold text-lg">Muhokama</h3>
          <p className="text-sm text-slate-500">{total} ta izoh</p>
        </div>
      </div>

      {/* New comment input */}
      <div className="mb-8">
        <CommentInput
          onSubmit={handleCreateComment}
          placeholder="Fikringizni baham ko'ring..."
          buttonText="Izoh qo'shish"
        />
      </div>

      {/* Comments list */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex gap-3">
              <div className="w-10 h-10 skeleton rounded-xl" />
              <div className="flex-1 space-y-2">
                <div className="h-4 skeleton rounded w-32" />
                <div className="h-16 skeleton rounded-xl" />
              </div>
            </div>
          ))}
        </div>
      ) : comments.length > 0 ? (
        <div className="space-y-6">
          <AnimatePresence>
            {comments.map((comment, index) => (
              <motion.div
                key={comment.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <SingleComment
                  comment={comment}
                  onLike={handleLike}
                  onReply={handleReply}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  currentUserId={user?.id}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-ocean-700/50 flex items-center justify-center mb-4">
            <HiOutlineChat className="w-8 h-8 text-slate-500" />
          </div>
          <p className="text-slate-400">Hali izohlar yo'q</p>
          <p className="text-sm text-slate-500 mt-1">Birinchi bo'lib fikringizni bildiring!</p>
        </div>
      )}
    </div>
  )
}
