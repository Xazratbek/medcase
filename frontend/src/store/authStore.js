import { create } from 'zustand'
import { authAPI, userAPI } from '../utils/api'
import toast from 'react-hot-toast'

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  
  // Autentifikatsiyani tekshirish
  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ isLoading: false, isAuthenticated: false, user: null })
      return
    }
    
    try {
      const response = await userAPI.getProfile()
      const userData = response.data.malumot || response.data
      set({ 
        user: userData, 
        isAuthenticated: true, 
        isLoading: false 
      })
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ isLoading: false, isAuthenticated: false, user: null })
    }
  },
  
  // Kirish
  login: async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      // Backend TokenJavob qaytaradi
      const data = response.data.malumot || response.data
      const { kirish_tokeni, yangilash_tokeni, foydalanuvchi } = data
      
      localStorage.setItem('access_token', kirish_tokeni)
      localStorage.setItem('refresh_token', yangilash_tokeni)
      
      let user = foydalanuvchi
      
      // Agar foydalanuvchi ma'lumotlari kelmasa, profil olish
      if (!user) {
        const profileRes = await userAPI.getProfile()
        user = profileRes.data.malumot || profileRes.data
      }
      
      set({ user, isAuthenticated: true })
      toast.success(`Xush kelibsiz, ${user.ism || 'foydalanuvchi'}!`)
      
      // Admin yoki oddiy foydalanuvchi ekanligini qaytarish
      const adminRoles = ['admin', 'ADMIN', 'super_admin', 'SUPER_ADMIN']
      const isAdmin = adminRoles.includes(user?.rol)
      
      return { success: true, user, isAdmin }
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.xato || "Kirish muvaffaqiyatsiz"
      toast.error(message)
      return { success: false, error: message }
    }
  },
  
  // Ro'yxatdan o'tish
  register: async (userData) => {
    try {
      // Ro'yxatdan o'tish
      const response = await authAPI.register(userData)
      const data = response.data.malumot || response.data
      
      // Ro'yxatdan so'ng avtomatik kirish
      const loginRes = await authAPI.login({
        email_yoki_nom: userData.email,
        parol: userData.parol
      })
      const loginData = loginRes.data.malumot || loginRes.data
      
      localStorage.setItem('access_token', loginData.kirish_tokeni)
      localStorage.setItem('refresh_token', loginData.yangilash_tokeni)
      
      // Profil olish
      const profileRes = await userAPI.getProfile()
      const user = profileRes.data.malumot || profileRes.data
      
      set({ user, isAuthenticated: true })
      toast.success("Ro'yxatdan muvaffaqiyatli o'tdingiz!")
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.xato || "Ro'yxatdan o'tish muvaffaqiyatsiz"
      toast.error(message)
      return { success: false, error: message }
    }
  },
  
  // Chiqish
  logout: async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false })
      toast.success("Tizimdan chiqdingiz")
    }
  },
  
  // Profilni yangilash
  updateProfile: async (data) => {
    try {
      const baseKeys = ['ism', 'familiya', 'foydalanuvchi_nomi']
      const baseData = {}
      const extraData = {}

      Object.entries(data || {}).forEach(([key, value]) => {
        if (baseKeys.includes(key)) {
          baseData[key] = value
        } else {
          extraData[key] = value
        }
      })

      if (Object.keys(baseData).length > 0) {
        await userAPI.updateProfile(baseData)
      }
      if (Object.keys(extraData).length > 0) {
        await userAPI.updateProfileExtra(extraData)
      }

      const profileRes = await userAPI.getProfile()
      const userData = profileRes.data.malumot || profileRes.data
      set({ user: userData })
      toast.success("Profil yangilandi")
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.xato || "Profilni yangilashda xatolik"
      toast.error(message)
      return { success: false, error: message }
    }
  },
  
  // Avatarni yangilash
  updateAvatar: async (file) => {
    try {
      const response = await userAPI.updateAvatar(file)
      set((state) => ({ 
        user: { ...state.user, avatar_url: response.data.malumot.avatar_url }
      }))
      toast.success("Avatar yangilandi")
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.xato || "Avatarni yuklashda xatolik"
      toast.error(message)
      return { success: false, error: message }
    }
  },
}))
