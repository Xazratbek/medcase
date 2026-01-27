import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../../utils/api'
import toast from 'react-hot-toast'
import {
  HiOutlineCloudUpload,
  HiOutlineDocumentText,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineExclamation,
  HiOutlineArrowLeft,
  HiOutlineDownload,
  HiOutlineRefresh,
  HiOutlineTable
} from 'react-icons/hi'

export default function ExcelImport() {
  const fileInputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [importing, setImporting] = useState(false)
  const [tahlilNatija, setTahlilNatija] = useState(null)
  const [importNatija, setImportNatija] = useState(null)
  const [step, setStep] = useState('upload') // upload, analyze, import, done

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!selectedFile.name.match(/\.(xlsx|xls)$/i)) {
        toast.error("Faqat Excel fayllar qabul qilinadi (.xlsx, .xls)")
        return
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast.error("Fayl hajmi 10MB dan oshmasligi kerak")
        return
      }
      setFile(selectedFile)
      setTahlilNatija(null)
      setImportNatija(null)
      setStep('upload')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      if (!droppedFile.name.match(/\.(xlsx|xls)$/i)) {
        toast.error("Faqat Excel fayllar qabul qilinadi")
        return
      }
      setFile(droppedFile)
      setTahlilNatija(null)
      setImportNatija(null)
      setStep('upload')
    }
  }

  const handleAnalyze = async () => {
    if (!file) return
    
    setUploading(true)
    setStep('analyze')
    
    try {
      const formData = new FormData()
      formData.append('fayl', file)
      
      const response = await api.post('/admin/import/excel/tahlil', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setTahlilNatija(response.data)
      
      if (response.data.muvaffaqiyat) {
        toast.success(`${response.data.yaroqli_holatlar} ta holat topildi`)
      } else {
        toast.error("Faylda xatoliklar mavjud")
      }
    } catch (error) {
      console.error('Analyze error:', error)
      toast.error(error.response?.data?.detail || "Tahlil qilishda xatolik")
      setTahlilNatija({ muvaffaqiyat: false, xato: error.response?.data?.detail })
    } finally {
      setUploading(false)
    }
  }

  const handleImport = async () => {
    if (!tahlilNatija?.holatlar) return
    
    setImporting(true)
    setStep('import')
    
    try {
      // Import uchun uzoqroq timeout (5 daqiqa)
      const response = await api.post('/admin/import/excel/import', tahlilNatija.holatlar, {
        timeout: 300000  // 5 daqiqa
      })
      
      console.log('Import natijasi:', response.data)
      setImportNatija(response.data)
      setStep('done')
      
      if (response.data.muvaffaqiyat) {
        toast.success(`${response.data.yaratilgan} ta holat import qilindi!`)
      } else {
        // Xatoliklar bo'lsa ham yaratilgan holatlar bo'lishi mumkin
        if (response.data.yaratilgan > 0) {
          toast.success(`${response.data.yaratilgan} ta holat import qilindi (ba'zi xatoliklar bor)`)
        } else {
          toast.error("Import qilishda xatoliklar yuz berdi")
        }
      }
    } catch (error) {
      console.error('Import error:', error)
      const errorMessage = error.code === 'ECONNABORTED' 
        ? "Import jarayoni uzoq davom etmoqda. Iltimos, sahifani yangilang va natijani tekshiring."
        : (error.response?.data?.detail || "Import qilishda xatolik")
      toast.error(errorMessage)
      setImportNatija({ muvaffaqiyat: false, xato: errorMessage })
    } finally {
      setImporting(false)
    }
  }

  const resetAll = () => {
    setFile(null)
    setTahlilNatija(null)
    setImportNatija(null)
    setStep('upload')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
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
        <h1 className="text-3xl font-display font-bold">Excel Import</h1>
        <p className="text-slate-400 mt-2">Case'larni Excel fayldan import qilish</p>
      </motion.div>

      {/* Steps Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-center gap-4 mb-8"
      >
        {['upload', 'analyze', 'import', 'done'].map((s, i) => (
          <div key={s} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
              step === s ? 'bg-med-500 text-white' :
              ['upload', 'analyze', 'import', 'done'].indexOf(step) > i ? 'bg-green-500 text-white' :
              'bg-ocean-700 text-slate-400'
            }`}>
              {['upload', 'analyze', 'import', 'done'].indexOf(step) > i ? '✓' : i + 1}
            </div>
            {i < 3 && (
              <div className={`w-12 h-0.5 mx-2 ${
                ['upload', 'analyze', 'import', 'done'].indexOf(step) > i ? 'bg-green-500' : 'bg-ocean-700'
              }`} />
            )}
          </div>
        ))}
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6 mb-6"
      >
        <h2 className="text-lg font-display font-semibold mb-4 flex items-center gap-2">
          <HiOutlineCloudUpload className="w-5 h-5 text-med-400" />
          Excel Fayl Yuklash
        </h2>

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
            file ? 'border-med-500/50 bg-med-500/5' : 'border-white/10 hover:border-white/20 hover:bg-white/5'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {file ? (
            <div className="flex items-center justify-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-green-500/20 flex items-center justify-center">
                <HiOutlineDocumentText className="w-7 h-7 text-green-400" />
              </div>
              <div className="text-left">
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-slate-400">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
          ) : (
            <>
              <HiOutlineCloudUpload className="w-12 h-12 mx-auto text-slate-500 mb-4" />
              <p className="text-slate-300 mb-2">Excel faylni bu yerga tashlang</p>
              <p className="text-sm text-slate-500">yoki bosib tanlang</p>
              <p className="text-xs text-slate-600 mt-4">.xlsx, .xls (max 10MB)</p>
            </>
          )}
        </div>

        {/* Action Buttons */}
        {file && !tahlilNatija && (
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleAnalyze}
              disabled={uploading}
              className="btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Tahlil qilinmoqda...</span>
                </>
              ) : (
                <>
                  <HiOutlineTable className="w-5 h-5" />
                  <span>Tahlil qilish</span>
                </>
              )}
            </button>
            <button onClick={resetAll} className="btn-secondary px-4">
              Bekor qilish
            </button>
          </div>
        )}
      </motion.div>

      {/* Analysis Results */}
      <AnimatePresence>
        {tahlilNatija && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass-card p-6 mb-6"
          >
            <h2 className="text-lg font-display font-semibold mb-4 flex items-center gap-2">
              {tahlilNatija.muvaffaqiyat ? (
                <HiOutlineCheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <HiOutlineXCircle className="w-5 h-5 text-red-400" />
              )}
              Tahlil Natijasi
            </h2>

            {tahlilNatija.xato ? (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
                {tahlilNatija.xato}
              </div>
            ) : (
              <>
                {/* Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="p-4 rounded-xl bg-ocean-700/50">
                    <p className="text-2xl font-bold text-white">{tahlilNatija.jami_qatorlar}</p>
                    <p className="text-xs text-slate-400">Jami qatorlar</p>
                  </div>
                  <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                    <p className="text-2xl font-bold text-green-400">{tahlilNatija.yaroqli_holatlar}</p>
                    <p className="text-xs text-slate-400">Yaroqli holatlar</p>
                  </div>
                  <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                    <p className="text-2xl font-bold text-red-400">{tahlilNatija.xatoli_qatorlar}</p>
                    <p className="text-xs text-slate-400">Xatoli qatorlar</p>
                  </div>
                  <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20">
                    <p className="text-2xl font-bold text-purple-400">{tahlilNatija.kategoriyalar?.length || 0}</p>
                    <p className="text-xs text-slate-400">Kategoriyalar</p>
                  </div>
                </div>

                {/* Categories Preview */}
                {tahlilNatija.kategoriyalar?.length > 0 && (
                  <div className="mb-6">
                    <p className="text-sm text-slate-400 mb-2">Topilgan kategoriyalar:</p>
                    <div className="flex flex-wrap gap-2">
                      {tahlilNatija.kategoriyalar.map((kat, i) => (
                        <span key={i} className="px-3 py-1 rounded-lg bg-purple-500/20 text-purple-300 text-sm capitalize">
                          {kat}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Errors */}
                {tahlilNatija.xatolar?.length > 0 && (
                  <div className="mb-6">
                    <p className="text-sm text-red-400 mb-2 font-medium">
                      Xatoliklar ({tahlilNatija.xatolar.length}):
                    </p>
                    <div className="max-h-48 overflow-y-auto space-y-2 scrollbar-hide">
                      {tahlilNatija.xatolar.slice(0, 10).map((err, i) => (
                        <div key={i} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm">
                          <span className="font-medium text-red-400">Qator {err.qator}:</span>
                          <span className="text-slate-300 ml-2">{err.xatolar?.join(', ')}</span>
                        </div>
                      ))}
                      {tahlilNatija.xatolar.length > 10 && (
                        <p className="text-sm text-slate-500 text-center">
                          va yana {tahlilNatija.xatolar.length - 10} ta xatolik...
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Warnings */}
                {tahlilNatija.ogohlantirishlar?.length > 0 && (
                  <div className="mb-6">
                    <p className="text-sm text-yellow-400 mb-2 font-medium flex items-center gap-1">
                      <HiOutlineExclamation className="w-4 h-4" />
                      Ogohlantirishlar ({tahlilNatija.ogohlantirishlar.length}):
                    </p>
                    <div className="max-h-32 overflow-y-auto space-y-1 scrollbar-hide">
                      {tahlilNatija.ogohlantirishlar.slice(0, 5).map((warn, i) => (
                        <p key={i} className="text-sm text-yellow-300/70">
                          Qator {warn.qator}: {warn.xabar}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Import Button */}
                {tahlilNatija.muvaffaqiyat && tahlilNatija.yaroqli_holatlar > 0 && (
                  <div className="flex gap-3">
                    <button
                      onClick={handleImport}
                      disabled={importing}
                      className="btn-primary flex-1 flex items-center justify-center gap-2"
                    >
                      {importing ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          <span>Import qilinmoqda...</span>
                        </>
                      ) : (
                        <>
                          <HiOutlineDownload className="w-5 h-5" />
                          <span>{tahlilNatija.yaroqli_holatlar} ta holatni import qilish</span>
                        </>
                      )}
                    </button>
                    <button onClick={resetAll} className="btn-secondary px-4">
                      <HiOutlineRefresh className="w-5 h-5" />
                    </button>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Import Results */}
      <AnimatePresence>
        {importNatija && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`glass-card p-6 ${
              importNatija.yaratilgan > 0 ? 'border-green-500/30' : 'border-red-500/30'
            }`}
          >
            <h2 className="text-lg font-display font-semibold mb-4 flex items-center gap-2">
              {importNatija.yaratilgan > 0 ? (
                <>
                  <HiOutlineCheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-green-400">Import muvaffaqiyatli!</span>
                </>
              ) : (
                <>
                  <HiOutlineXCircle className="w-5 h-5 text-red-400" />
                  <span className="text-red-400">Import xatosi</span>
                </>
              )}
            </h2>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-center">
                <p className="text-3xl font-bold text-green-400">{importNatija.yaratilgan || 0}</p>
                <p className="text-sm text-slate-400">Yangi holatlar</p>
              </div>
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-center">
                <p className="text-3xl font-bold text-blue-400">{importNatija.yangilangan || 0}</p>
                <p className="text-sm text-slate-400">Yangilangan</p>
              </div>
            </div>

            {/* Xatoliklar */}
            {importNatija.xatolar?.length > 0 && (
              <div className="mb-6">
                <p className="text-sm text-yellow-400 mb-2 font-medium flex items-center gap-1">
                  <HiOutlineExclamation className="w-4 h-4" />
                  Xatoliklar ({importNatija.xatolar.length}):
                </p>
                <div className="max-h-32 overflow-y-auto space-y-2 scrollbar-hide">
                  {importNatija.xatolar.slice(0, 5).map((err, i) => (
                    <div key={i} className="p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-sm text-yellow-300">
                      {err.qator && <span className="font-medium">Qator {err.qator}: </span>}
                      {err.xato || err.xatolar?.join(', ') || JSON.stringify(err)}
                    </div>
                  ))}
                  {importNatija.xatolar.length > 5 && (
                    <p className="text-sm text-slate-500 text-center">
                      va yana {importNatija.xatolar.length - 5} ta xatolik...
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Umumiy xato */}
            {importNatija.xato && !importNatija.yaratilgan && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 mb-6">
                {importNatija.xato}
              </div>
            )}

            <div className="flex gap-3">
              <button onClick={resetAll} className="btn-primary flex-1">
                Yangi import
              </button>
              <Link to="/admin/holatlar" className="btn-secondary px-6">
                Holatlarni ko'rish
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Excel Format Guide */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card p-6 mt-6"
      >
        <h2 className="text-lg font-display font-semibold mb-4">Excel Format</h2>
        <p className="text-sm text-slate-400 mb-4">
          Excel faylda quyidagi ustunlar bo'lishi kerak:
        </p>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-2 px-3 text-slate-400 font-medium">Ustun</th>
                <th className="text-left py-2 px-3 text-slate-400 font-medium">Tavsif</th>
                <th className="text-left py-2 px-3 text-slate-400 font-medium">Majburiy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {[
                ['id', 'Holat identifikatori', 'Yo\'q'],
                ['main_category', 'Asosiy kategoriya', 'Ha'],
                ['sub_category', 'Kichik kategoriya', 'Ha'],
                ['section', 'Bo\'lim/Mavzu', 'Ha'],
                ['case', 'Klinik holat matni', 'Ha'],
                ['question', 'Savol', 'Ha'],
                ['opt_a, opt_b, opt_c, opt_d', 'Javob variantlari', 'Ha'],
                ['correct', 'To\'g\'ri javob (A/B/C/D)', 'Ha'],
                ['expl_a, expl_b, expl_c, expl_d', 'Tushuntirishlar', 'Yo\'q'],
                ['diff', 'Qiyinlik (basic/intermediate/advanced)', 'Yo\'q'],
                ['link', 'Video/rasm havolasi', 'Yo\'q'],
              ].map(([col, desc, req], i) => (
                <tr key={i} className="hover:bg-white/5">
                  <td className="py-2 px-3 font-mono text-med-400">{col}</td>
                  <td className="py-2 px-3 text-slate-300">{desc}</td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      req === 'Ha' ? 'bg-red-500/20 text-red-400' : 'bg-slate-500/20 text-slate-400'
                    }`}>
                      {req}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
