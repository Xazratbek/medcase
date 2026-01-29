import { notificationAPI } from './api'

const urlBase64ToUint8Array = (base64String) => {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

export const ensurePushSubscription = async () => {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    throw new Error('Push qo‘llab-quvvatlanmaydi')
  }

  const permission = await Notification.requestPermission()
  if (permission !== 'granted') {
    throw new Error('Bildirishnoma ruxsati berilmadi')
  }

  const reg = await navigator.serviceWorker.register('/service-worker.js')
  const existing = await reg.pushManager.getSubscription()
  if (existing) {
    await notificationAPI.subscribePush(existing, navigator.userAgent)
    return existing
  }

  const { data } = await notificationAPI.getVapidKey()
  const publicKey = data?.public_key
  if (!publicKey) {
    throw new Error('VAPID public key topilmadi')
  }

  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(publicKey)
  })

  await notificationAPI.subscribePush(sub, navigator.userAgent)
  return sub
}

export const removePushSubscription = async () => {
  if (!('serviceWorker' in navigator)) return
  const reg = await navigator.serviceWorker.ready
  const sub = await reg.pushManager.getSubscription()
  if (sub) {
    await notificationAPI.unsubscribePush(sub, navigator.userAgent)
    await sub.unsubscribe()
  }
}
