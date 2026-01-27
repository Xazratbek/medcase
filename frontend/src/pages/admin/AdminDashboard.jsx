import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import api from '../../utils/api'
import {
  HiOutlineUsers,
  HiOutlineCollection,
  HiOutlineDocumentText,
  HiOutlineUpload,
  HiOutlineChartBar,
  HiOutlineCog,
  HiOutlineFolder,
  HiOutlineCloudUpload
} from 'react-icons/hi'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await api.get('/admin/statistika')
      setStats(response.data)
    } catch (error) {
      console.error('Admin stats error:', error)
    } finally {
      setLoading(false)
    }
  }

  const adminMenus = [
    {
      title: "Excel Import",
      description: "Case'larni Excel dan import qilish",
      icon: HiOutlineCloudUpload,
      href: "/admin/import",
      color: "bg-med-500/20 text-med-400"
    },
    {
      title: "Foydalanuvchilar",
      description: "Foydalanuvchilarni boshqarish",
      icon: HiOutlineUsers,
      href: "/admin/foydalanuvchilar",
      color: "bg-purple-500/20 text-purple-400"
    },
    {
      title: "Kategoriyalar",
      description: "Kategoriya, bo'lim va mavzular",
      icon: HiOutlineFolder,
      href: "/admin/kategoriyalar",
      color: "bg-gold-500/20 text-gold-400"
    },
    {
      title: "Holatlar",
      description: "Barcha holatlarni ko'rish va tahrirlash",
      icon: HiOutlineDocumentText,
      href: "/admin/holatlar",
      color: "bg-coral-500/20 text-coral-400"
    },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-display font-bold">Admin Panel</h1>
        <p className="text-slate-400 mt-2">Platformani boshqarish</p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
      >
        <StatCard
          icon={HiOutlineUsers}
          label="Foydalanuvchilar"
          value={stats?.foydalanuvchilar_soni || 0}
          loading={loading}
          color="text-purple-400"
        />
        <StatCard
          icon={HiOutlineCollection}
          label="Kategoriyalar"
          value={stats?.kategoriyalar_soni || 0}
          loading={loading}
          color="text-gold-400"
        />
        <StatCard
          icon={HiOutlineFolder}
          label="Bo'limlar"
          value={stats?.bolimlar_soni || 0}
          loading={loading}
          color="text-med-400"
        />
        <StatCard
          icon={HiOutlineDocumentText}
          label="Holatlar"
          value={stats?.holatlar_soni || 0}
          loading={loading}
          color="text-coral-400"
        />
      </motion.div>

      {/* Admin Menus */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        {adminMenus.map((menu, index) => (
          <Link
            key={menu.href}
            to={menu.href}
            className="glass-card p-6 hover:border-white/20 transition-all group"
          >
            <div className="flex items-start gap-4">
              <div className={`w-14 h-14 rounded-xl ${menu.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                <menu.icon className="w-7 h-7" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-display font-semibold group-hover:text-white transition-colors">
                  {menu.title}
                </h3>
                <p className="text-sm text-slate-400 mt-1">{menu.description}</p>
              </div>
            </div>
          </Link>
        ))}
      </motion.div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, loading, color }) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center gap-3">
        <Icon className={`w-6 h-6 ${color}`} />
        <div>
          {loading ? (
            <div className="h-6 w-16 skeleton rounded" />
          ) : (
            <p className="text-2xl font-display font-bold">{value.toLocaleString()}</p>
          )}
          <p className="text-xs text-slate-500">{label}</p>
        </div>
      </div>
    </div>
  )
}
