import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

// Axios instance yaratish
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - token qo'shish
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - xatolarni ushlash va token yangilash
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 401 xato - token muddati tugagan
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/autentifikatsiya/token-yangilash`, {
            yangilash_tokeni: refreshToken
          })

          const { kirish_tokeni } = response.data
          localStorage.setItem('access_token', kirish_tokeni)

          originalRequest.headers.Authorization = `Bearer ${kirish_tokeni}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh token ham yaroqsiz
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/kirish'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API metodlari
export const authAPI = {
  login: (data) => api.post('/autentifikatsiya/kirish', data),
  register: (data) => api.post('/autentifikatsiya/royxatdan-otish', data),
  logout: () => api.post('/autentifikatsiya/chiqish'),
  refreshToken: (data) => api.post('/autentifikatsiya/token-yangilash', data),
  forgotPassword: (email) => api.post('/autentifikatsiya/parolni-tiklash', { email }),
  resetPassword: (data) => api.post('/autentifikatsiya/yangi-parol', data),
  me: () => api.get('/foydalanuvchi/men'),
}

export const userAPI = {
  getProfile: () => api.get('/foydalanuvchi/profil'),
  updateProfile: (data) => api.put('/foydalanuvchi/profil', data),
  updateProfileExtra: (data) => api.put('/foydalanuvchi/profil/qoshimcha', data),
  updateAvatar: (file, onUploadProgress) => {
    const formData = new FormData()
    formData.append('rasm', file)
    return api.post('/foydalanuvchi/profil/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress
    })
  },
  changePassword: (data) => api.post('/autentifikatsiya/parol-ozgartirish', data),
  deleteAccount: () => api.delete('/foydalanuvchi/profil'),
  getSessions: () => api.get('/foydalanuvchi/sessiyalar'),
  getNotificationSettings: () => api.get('/bildirishnoma/sozlamalar'),
  updateNotificationSettings: (data) => api.put('/bildirishnoma/sozlamalar', data),
}

export const categoryAPI = {
  getAll: (params) => api.get('/kategoriya/', { params }),
  getById: (id) => api.get(`/kategoriya/${id}`),
  getSubcategories: (id) => api.get(`/kategoriya/${id}/kichik-kategoriyalar`),
  getSubcategoryDetail: (id) => api.get(`/kategoriya/kichik/detail/${id}`),
  getSections: (subcategoryId) => api.get(`/kategoriya/bolim/${subcategoryId}`),
  getSectionDetail: (sectionId) => api.get(`/kategoriya/bolim/detail/${sectionId}`),
}

export const caseAPI = {
  getAll: (params) => api.get('/holat/', { params }),
  getById: (id) => api.get(`/holat/${id}`),
  getBySection: (bolimId, params) => api.get(`/holat/bolim/${bolimId}`, { params }),
  submitAnswer: (id, answer, sarflangan_vaqt = 0) => api.post(`/holat/${id}/javob?tanlangan_javob=${answer}&sarflangan_vaqt=${sarflangan_vaqt}`),
  getRandomCases: (params) => api.get('/holat/tasodifiy', { params }),
  getDailyChallenge: () => api.get('/holat/kunlik'),
  bookmark: (id) => api.post(`/holat/${id}/xatcho`),
  removeBookmark: (id) => api.delete(`/holat/${id}/xatcho`),
  flag: (id, reason) => api.post(`/holat/${id}/xabar`, { sabab: reason }),
  getBookmarks: (params) => api.get('/holat/xatcholar', { params }),
  getTags: () => api.get('/holat/teglar'),
}

export const progressAPI = {
  getOverview: () => api.get('/rivojlanish/'),
  getDashboard: () => api.get('/rivojlanish/dashboard'),
  getStats: (params) => api.get('/rivojlanish/statistika', { params }),
  getHistory: (params) => api.get('/rivojlanish/urinishlar', { params }),
  getDailyStats: (params) => api.get('/rivojlanish/kunlik', { params }),
  getCategoryStats: () => api.get('/rivojlanish/kategoriya-statistika'),
  getWeakAreas: () => api.get('/rivojlanish/zaif-tomonlar'),
  getStrongAreas: () => api.get('/rivojlanish/kuchli-tomonlar'),
}

export const gamificationAPI = {
  getLeaderboard: (params) => api.get('/gamifikatsiya/reyting', { params }),
  getAchievements: () => api.get('/gamifikatsiya/nishonlar'),
  getMyAchievements: () => api.get('/gamifikatsiya/mening-nishonlarim'),
  getPoints: () => api.get('/gamifikatsiya/ballar'),
  getLevel: () => api.get('/gamifikatsiya/daraja'),
}

export const notificationAPI = {
  getAll: (params) => api.get('/bildirishnoma/', { params }),
  markAsRead: (id) => api.post(`/bildirishnoma/${id}/oqilgan`),
  markAllAsRead: () => api.post('/bildirishnoma/hammasi-oqilgan'),
  getUnreadCount: () => api.get('/bildirishnoma/oqilmagan-soni'),
  getVapidKey: () => api.get('/bildirishnoma/push/vapid'),
  subscribePush: (subscription, userAgent) => {
    const payload = subscription?.toJSON ? subscription.toJSON() : subscription
    return api.post('/bildirishnoma/push/subscribe', { ...payload, user_agent: userAgent })
  },
  unsubscribePush: (subscription, userAgent) => {
    const payload = subscription?.toJSON ? subscription.toJSON() : subscription
    return api.post('/bildirishnoma/push/unsubscribe', { ...payload, user_agent: userAgent })
  },
}

// Izoh (Forum/Comments) API
export const izohAPI = {
  create: (data) => api.post('/izoh/', data),
  getByCase: (holatId, params) => api.get(`/izoh/holat/${holatId}`, { params }),
  update: (id, data) => api.put(`/izoh/${id}`, data),
  delete: (id) => api.delete(`/izoh/${id}`),
  like: (id) => api.post(`/izoh/${id}/yoqtirish`),
  getMine: (params) => api.get('/izoh/mening', { params }),
}

// Takrorlash (Spaced Repetition) API
export const takrorlashAPI = {
  getToday: (params) => api.get('/takrorlash/bugungi', { params }),
  getStats: () => api.get('/takrorlash/statistika'),
  addCase: (holatId) => api.post(`/takrorlash/qoshish/${holatId}`),
  rate: (holatId, data) => api.post(`/takrorlash/baholash/${holatId}`, data),
  markRead: (holatId, oqilgan = true) => api.post(`/takrorlash/oqilgan/${holatId}?oqilgan=${oqilgan}`),
  getHistory: (holatId, params) => api.get(`/takrorlash/tarix/${holatId}`, { params }),
  getAllCards: (params) => api.get('/takrorlash/kartalar', { params }),
}

// Imtihon (Exam) API
export const imtihonAPI = {
  getTemplates: (params) => api.get('/imtihon/shablonlar', { params }),
  getTemplate: (id) => api.get(`/imtihon/shablon/${id}`),
  start: (data) => api.post('/imtihon/boshlash', data),
  get: (id) => api.get(`/imtihon/${id}`),
  getCurrentQuestion: (id) => api.get(`/imtihon/${id}/savol`),
  submitAnswer: (id, data) => api.post(`/imtihon/${id}/javob`, data),
  nextQuestion: (id) => api.post(`/imtihon/${id}/keyingi`),
  prevQuestion: (id) => api.post(`/imtihon/${id}/oldingi`),
  goToQuestion: (id, index) => api.post(`/imtihon/${id}/otish/${index}`),
  finish: (id) => api.post(`/imtihon/${id}/yakunlash`),
  getResult: (id) => api.get(`/imtihon/${id}/natija`),
  getMyExams: (params) => api.get('/imtihon/', { params }),
  getMyStats: () => api.get('/imtihon/statistika/mening'),
  cancel: (id) => api.delete(`/imtihon/${id}`),
}

export const umumiyAPI = {
  getLandingData: () => api.get('/umumiy/landing-data'),
}

export default api
