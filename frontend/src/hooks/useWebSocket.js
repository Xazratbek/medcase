import { useState, useEffect, useCallback, useRef } from 'react'
import toast from 'react-hot-toast'

const getDefaultWsUrl = () => {
  if (typeof window === 'undefined') return 'ws://localhost:8000/api/v1/ws'
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/api/v1/ws`
}

const WS_URL = import.meta.env.VITE_WS_URL || getDefaultWsUrl()

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    try {
      const ws = new WebSocket(`${WS_URL}?token=${token}`)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        reconnectAttempts.current = 0
        console.log('WebSocket ulandi')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          
          // Bildirishnoma turlariga qarab toast ko'rsatish
          if (data.turi === 'bildirishnoma') {
            toast(data.sarlavha || data.malumot?.matn, {
              icon: '🔔',
              duration: 5000,
            })
          } else if (data.turi === 'yangi_nishon') {
            toast.success(data.sarlavha, {
              icon: '🏆',
              duration: 6000,
            })
          } else if (data.turi === 'daraja_oshdi') {
            toast.success(data.sarlavha, {
              icon: '🎉',
              duration: 6000,
            })
          }
        } catch (e) {
          console.error('WebSocket xabar xatosi:', e)
        }
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        wsRef.current = null
        
        // Avtomatik qayta ulanish
        if (event.code !== 4001 && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          reconnectTimeoutRef.current = setTimeout(connect, delay)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket xatosi:', error)
      }
    } catch (e) {
      console.error('WebSocket ulanish xatosi:', e)
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
      return true
    }
    return false
  }, [])

  const subscribe = useCallback((channel) => {
    return sendMessage({ amal: 'obuna', kanal: channel })
  }, [sendMessage])

  const unsubscribe = useCallback((channel) => {
    return sendMessage({ amal: 'obunadan_chiqish', kanal: channel })
  }, [sendMessage])

  // Avtomatik ulanish
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  // Token o'zgarganda qayta ulanish
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'access_token') {
        if (e.newValue) {
          connect()
        } else {
          disconnect()
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    unsubscribe,
  }
}

export default useWebSocket
