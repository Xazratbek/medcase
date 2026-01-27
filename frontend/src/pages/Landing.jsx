import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useMemo } from 'react'
import {
  HiOutlineAcademicCap,
  HiOutlineChartBar,
  HiOutlineLightningBolt,
  HiOutlineUserGroup,
  HiOutlinePlay,
  HiOutlineArrowRight,
  HiOutlineCheck,
  HiOutlineSparkles
} from 'react-icons/hi'
import { FaTelegram } from 'react-icons/fa'
import { umumiyAPI } from '../utils/api'

const iconMap = {
  HiOutlineAcademicCap,
  HiOutlineChartBar,
  HiOutlineLightningBolt,
  HiOutlineUserGroup,
};

// Floating particles component for atmosphere
function FloatingParticles() {
  const particles = useMemo(() =>
    Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 1,
      duration: Math.random() * 20 + 10,
      delay: Math.random() * 5,
    })), []
  );

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-med-400/30"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size,
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.6, 0.2],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

// Animated counter for stats
function AnimatedCounter({ value, duration = 2 }) {
  const [count, setCount] = useState(0);
  const numValue = parseInt(value.replace(/[^0-9]/g, '')) || 0;
  const suffix = value.replace(/[0-9]/g, '');

  useEffect(() => {
    let start = 0;
    const end = numValue;
    const incrementTime = (duration * 1000) / end;

    const timer = setInterval(() => {
      start += Math.ceil(end / 50);
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [numValue, duration]);

  return <span>{count}{suffix}</span>;
}

// Animated gradient orb
function GradientOrb({ className, delay = 0 }) {
  return (
    <motion.div
      className={className}
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.3, 0.5, 0.3],
      }}
      transition={{
        duration: 8,
        delay,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  );
}

// Glowing line decoration
function GlowingLine() {
  return (
    <div className="absolute left-0 right-0 h-px top-1/2 overflow-hidden">
      <motion.div
        className="h-full w-32 bg-gradient-to-r from-transparent via-med-400 to-transparent"
        animate={{ x: ['-100%', '400%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
      />
    </div>
  );
}

// Medical icons floating animation
const floatingIcons = ['🩺', '💊', '🫀', '🧬', '🔬', '💉', '🩻', '🧠'];

function FloatingMedicalIcons() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {floatingIcons.map((icon, index) => (
        <motion.div
          key={index}
          className="absolute text-4xl opacity-10"
          style={{
            left: `${10 + (index * 12)}%`,
            top: `${20 + (index % 3) * 25}%`,
          }}
          animate={{
            y: [0, -30, 0],
            rotate: [0, 10, -10, 0],
            opacity: [0.05, 0.15, 0.05],
          }}
          transition={{
            duration: 6 + index,
            delay: index * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          {icon}
        </motion.div>
      ))}
    </div>
  );
}

// Staggered container variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.1,
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 12
    }
  }
};

const scaleVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 15
    }
  }
};

export default function Landing() {
  const [landingData, setLandingData] = useState({
    features: [],
    stats: [],
    categories: [],
  });
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const fetchLandingData = async () => {
      try {
        const response = await umumiyAPI.getLandingData();
        setLandingData(response.data);
        setTimeout(() => setIsLoaded(true), 100);
      } catch (error) {
        console.error("Error fetching landing data:", error);
        setIsLoaded(true);
      }
    };
    fetchLandingData();
  }, []);

  const { features, stats, categories } = landingData;

  return (
    <div className="min-h-screen overflow-hidden bg-gradient-to-b from-ocean-900 via-ocean-900 to-ocean-950">
      {/* Animated background */}
      <div className="fixed inset-0 pointer-events-none">
        <FloatingParticles />
        <FloatingMedicalIcons />

        {/* Animated gradient orbs */}
        <GradientOrb
          className="absolute top-20 left-1/4 w-[500px] h-[500px] bg-med-500/20 rounded-full blur-[150px]"
          delay={0}
        />
        <GradientOrb
          className="absolute bottom-20 right-1/4 w-[400px] h-[400px] bg-med-600/15 rounded-full blur-[120px]"
          delay={2}
        />
        <GradientOrb
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-ocean-700/20 rounded-full blur-[180px]"
          delay={4}
        />

        {/* Grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(16, 185, 129, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(16, 185, 129, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '80px 80px'
          }}
        />
      </div>

      {/* Navbar with blur backdrop */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="fixed top-0 inset-x-0 z-50 backdrop-blur-xl bg-ocean-900/70 border-b border-white/5"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <Link to="/" className="flex items-center gap-3 group">
              <motion.div
                className="w-11 h-11 rounded-xl bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center shadow-lg shadow-med-500/30"
                whileHover={{ scale: 1.1, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="text-xl font-display font-bold text-white">M</span>
              </motion.div>
              <span className="font-display font-bold text-xl hidden sm:block group-hover:text-med-400 transition-colors">
                MedCase Pro
              </span>
            </Link>

            <div className="flex items-center gap-4">
              <Link to="/kirish" className="btn-ghost relative overflow-hidden group">
                <span className="relative z-10">Kirish</span>
                <motion.div
                  className="absolute inset-0 bg-white/5 rounded-lg"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
              </Link>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link to="/royxatdan-otish" className="btn-primary flex items-center gap-2">
                  <HiOutlineSparkles className="w-4 h-4" />
                  Boshlash
                </Link>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-44 lg:pb-36">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center max-w-4xl mx-auto"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Badge */}
            <motion.div variants={itemVariants}>
              <motion.span
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-med-500/10 to-med-400/10 border border-med-500/20 text-med-400 text-sm font-medium backdrop-blur-sm"
                whileHover={{ scale: 1.05, borderColor: 'rgba(16, 185, 129, 0.5)' }}
              >
                <motion.span
                  className="w-2 h-2 rounded-full bg-med-400"
                  animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                Tibbiyot ta'limining yangi davri
              </motion.span>
            </motion.div>

            {/* Main heading with gradient animation */}
            <motion.h1
              variants={itemVariants}
              className="mt-10 text-5xl sm:text-6xl lg:text-8xl font-display font-bold leading-[1.1] tracking-tight"
            >
              Klinik fikrlash
              <motion.span
                className="block mt-2 bg-gradient-to-r from-med-400 via-emerald-400 to-med-500 bg-clip-text text-transparent bg-[length:200%_auto]"
                animate={{ backgroundPosition: ['0% center', '200% center'] }}
                transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
              >
                ko'nikmalaringizni rivojlantiring
              </motion.span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={itemVariants}
              className="mt-8 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed"
            >
              Real klinik holatlar asosida o'rganing. Interaktiv savollar, batafsil tushuntirishlar
              va gamifikatsiya tizimi bilan tibbiyot ta'limini <span className="text-med-400 font-medium">yangi bosqichga</span> olib chiqing.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={itemVariants}
              className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-5"
            >
              <motion.div
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Link
                  to="/royxatdan-otish"
                  className="btn-primary text-lg px-10 py-5 w-full sm:w-auto flex items-center justify-center gap-3 shadow-xl shadow-med-500/30 relative overflow-hidden group"
                >
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"
                  />
                  <span className="relative">Bepul boshlash</span>
                  <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <HiOutlineArrowRight className="w-5 h-5" />
                  </motion.span>
                </Link>
              </motion.div>

              <motion.button
                className="btn-secondary flex items-center gap-3 text-lg px-10 py-5 w-full sm:w-auto group"
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <motion.span
                  className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-white/20 transition-colors"
                  whileHover={{ scale: 1.1 }}
                >
                  <HiOutlinePlay className="w-5 h-5 ml-0.5" />
                </motion.span>
                Demo ko'rish
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Stats with animated counters */}
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="mt-24 grid grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                className="glass-card p-7 text-center group cursor-default relative overflow-hidden"
                whileHover={{
                  y: -8,
                  boxShadow: '0 25px 50px -12px rgba(16, 185, 129, 0.25)',
                  borderColor: 'rgba(16, 185, 129, 0.3)'
                }}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
              >
                {/* Hover glow effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-med-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                />

                <motion.div
                  className="relative text-4xl sm:text-5xl font-display font-bold bg-gradient-to-r from-med-400 to-med-200 bg-clip-text text-transparent"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.8 + index * 0.1, type: "spring" }}
                >
                  {isLoaded ? <AnimatedCounter value={stat.value} /> : stat.value}
                </motion.div>
                <div className="relative mt-3 text-sm text-slate-400 font-medium">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 lg:py-36 relative">
        <GlowingLine />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <motion.span
              className="inline-block px-4 py-1.5 rounded-full bg-med-500/10 text-med-400 text-sm font-medium mb-4"
              whileHover={{ scale: 1.05 }}
            >
              Imkoniyatlar
            </motion.span>
            <h2 className="text-4xl sm:text-5xl font-display font-bold text-white">
              Nima uchun <span className="bg-gradient-to-r from-med-400 to-med-200 bg-clip-text text-transparent">MedCase Pro</span>?
            </h2>
            <p className="mt-5 text-lg text-slate-400">
              Zamonaviy ta'lim platformasi barcha kerakli vositalar bilan jihozlangan
            </p>
          </motion.div>

          <div className="mt-20 grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = iconMap[feature.icon];
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.15 }}
                  whileHover={{ y: -10, scale: 1.02 }}
                  className="glass-card-hover p-7 group relative overflow-hidden"
                >
                  {/* Animated border glow */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{
                      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), transparent)',
                    }}
                  />

                  <motion.div
                    className={`relative w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg`}
                    whileHover={{ scale: 1.15, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    {Icon && <Icon className="w-8 h-8 text-white" />}
                  </motion.div>
                  <h3 className="relative mt-6 text-xl font-display font-semibold group-hover:text-med-400 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="relative mt-3 text-slate-400 leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Categories Preview */}
      <section className="py-24 lg:py-36 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-ocean-800/50 to-transparent pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
            >
              <motion.span
                className="inline-block px-4 py-1.5 rounded-full bg-med-500/10 text-med-400 text-sm font-medium mb-4"
                whileHover={{ scale: 1.05 }}
              >
                Katalog
              </motion.span>
              <h2 className="text-4xl sm:text-5xl font-display font-bold leading-tight">
                50+ tibbiyot
                <motion.span
                  className="block mt-2 bg-gradient-to-r from-med-400 via-emerald-400 to-med-500 bg-clip-text text-transparent"
                  animate={{ backgroundPosition: ['0% center', '200% center'] }}
                  transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                  style={{ backgroundSize: '200% auto' }}
                >
                  kategoriyalari
                </motion.span>
              </h2>
              <p className="mt-6 text-lg text-slate-400 leading-relaxed">
                Barcha tibbiyot sohalari bo'yicha keng qamrovli holatlar to'plami.
                Asosiy fanlardan tortib klinik mutaxassisliklargacha.
              </p>

              <motion.ul
                className="mt-10 space-y-5"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                {['Fundamental fanlar', 'Klinik fanlar', 'Diagnostika'].map((item, i) => (
                  <motion.li
                    key={item}
                    className="flex items-center gap-4 group"
                    variants={itemVariants}
                  >
                    <motion.div
                      className="w-8 h-8 rounded-full bg-gradient-to-br from-med-500/30 to-med-400/10 flex items-center justify-center border border-med-500/30"
                      whileHover={{ scale: 1.2, borderColor: 'rgba(16, 185, 129, 0.6)' }}
                    >
                      <HiOutlineCheck className="w-4 h-4 text-med-400" />
                    </motion.div>
                    <span className="text-lg group-hover:text-med-400 transition-colors">{item}</span>
                  </motion.li>
                ))}
              </motion.ul>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4 }}
                className="mt-10"
              >
                <motion.div whileHover={{ scale: 1.05, x: 5 }} whileTap={{ scale: 0.95 }}>
                  <Link to="/royxatdan-otish" className="btn-primary inline-flex items-center gap-3 px-8 py-4">
                    Kategoriyalarni ko'rish
                    <HiOutlineArrowRight className="w-5 h-5" />
                  </Link>
                </motion.div>
              </motion.div>
            </motion.div>

            <motion.div
              className="grid grid-cols-2 gap-5"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
            >
              {categories.map((category, index) => (
                <motion.div
                  key={category.name}
                  variants={scaleVariants}
                  whileHover={{
                    y: -8,
                    scale: 1.03,
                    boxShadow: '0 25px 50px -12px rgba(16, 185, 129, 0.2)'
                  }}
                  className="glass-card-hover p-6 group cursor-pointer"
                >
                  <motion.span
                    className="text-4xl block"
                    animate={{ rotate: [0, 5, -5, 0] }}
                    transition={{ duration: 4, repeat: Infinity, delay: index * 0.3 }}
                  >
                    {category.emoji}
                  </motion.span>
                  <h3 className="mt-4 font-display font-semibold text-lg group-hover:text-med-400 transition-colors">
                    {category.name}
                  </h3>
                  <p className="mt-2 text-sm text-slate-500">
                    <span className="text-med-400 font-medium">{category.count}</span> holat
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 lg:py-36">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative rounded-3xl overflow-hidden"
          >
            {/* Background with animated gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-ocean-800 via-ocean-800/95 to-ocean-900">
              <motion.div
                className="absolute inset-0"
                style={{
                  background: 'radial-gradient(circle at 30% 30%, rgba(16, 185, 129, 0.15), transparent 50%)',
                }}
                animate={{
                  background: [
                    'radial-gradient(circle at 30% 30%, rgba(16, 185, 129, 0.15), transparent 50%)',
                    'radial-gradient(circle at 70% 70%, rgba(16, 185, 129, 0.15), transparent 50%)',
                    'radial-gradient(circle at 30% 30%, rgba(16, 185, 129, 0.15), transparent 50%)',
                  ]
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              />
            </div>

            <div className="relative px-8 sm:px-12 lg:px-20 py-16 lg:py-24 text-center border border-white/10 rounded-3xl">
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                viewport={{ once: true }}
                transition={{ type: "spring", delay: 0.2 }}
                className="mb-8"
              >
                <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-med-500/20 text-med-400 text-sm font-medium">
                  <HiOutlineSparkles className="w-4 h-4" />
                  100% bepul
                </span>
              </motion.div>

              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold leading-tight">
                Bugun <span className="bg-gradient-to-r from-med-400 to-emerald-400 bg-clip-text text-transparent">o'qishni boshlang</span>
              </h2>
              <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto">
                Minglab shifokor va tibbiyot talabalariga qo'shiling.
                Bepul hisob yarating va klinik fikrlash ko'nikmalaringizni rivojlantiring.
              </p>
              <motion.div
                className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-5"
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <motion.div variants={itemVariants} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Link to="/royxatdan-otish" className="btn-primary text-lg px-10 py-5 shadow-xl shadow-med-500/30">
                    Bepul ro'yxatdan o'tish
                  </Link>
                </motion.div>
                <motion.div variants={itemVariants} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Link to="/kirish" className="btn-ghost text-lg px-8 py-5">
                    Hisobim bor
                  </Link>
                </motion.div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 border-t border-white/5 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.02 }}
            >
              <motion.div
                className="w-11 h-11 rounded-xl bg-gradient-to-br from-med-400 to-med-600 flex items-center justify-center shadow-lg shadow-med-500/20"
                whileHover={{ rotate: 5 }}
              >
                <span className="text-xl font-display font-bold text-white">M</span>
              </motion.div>
              <span className="font-display font-bold text-xl">MedCase Pro</span>
            </motion.div>

            <nav className="flex flex-wrap items-center justify-center gap-8 text-sm text-slate-400">
              {[
                { to: '/haqida', text: 'Biz haqimizda' },
                { to: '/shartlar', text: 'Shartlar' },
                { to: '/maxfiylik', text: 'Maxfiylik' },
                { to: '/aloqa', text: 'Aloqa' },
              ].map((link) => (
                <motion.span key={link.to} whileHover={{ scale: 1.05, color: '#fff' }}>
                  <Link to={link.to} className="hover:text-white transition-colors">
                    {link.text}
                  </Link>
                </motion.span>
              ))}
              <motion.a
                href="https://t.me/Xazratbek"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 hover:text-[#0088cc] transition-colors"
                whileHover={{ scale: 1.1 }}
              >
                <FaTelegram className="w-5 h-5" />
                <span>@Xazratbek</span>
              </motion.a>
            </nav>

            <p className="text-sm text-slate-500">
              © 2024-2026 MedCase Pro. Barcha huquqlar himoyalangan.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
