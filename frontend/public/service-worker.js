self.addEventListener('push', (event) => {
  if (!event.data) return

  let data = {}
  try {
    data = event.data.json()
  } catch (e) {
    data = { title: 'Bildirishnoma', body: event.data.text() }
  }

  const title = data.title || 'Bildirishnoma'
  const options = {
    body: data.body || '',
    icon: '/medcase-icon.svg',
    badge: '/medcase-icon.svg',
    silent: data.silent === false ? false : false,
    data: {
      url: data.url || '/'
    }
  }

  event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification?.data?.url || '/'
  event.waitUntil(self.clients.openWindow(url))
})
