const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

let googleScriptPromise = null
let googleInitialized = false

function loadGoogleScript() {
  if (googleScriptPromise) return googleScriptPromise
  if (window.google?.accounts?.id) {
    googleScriptPromise = Promise.resolve()
    return googleScriptPromise
  }

  googleScriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Google script yuklanmadi'))
    document.head.appendChild(script)
  })

  return googleScriptPromise
}

async function ensureGoogleInit(callback, uxMode = 'popup') {
  if (!GOOGLE_CLIENT_ID) {
    throw new Error('VITE_GOOGLE_CLIENT_ID sozlanmagan')
  }

  await loadGoogleScript()

  if (!window.google?.accounts?.id) {
    throw new Error('Google Identity yuklanmadi')
  }

  if (!googleInitialized) {
    window.google.accounts.id.initialize({
      client_id: GOOGLE_CLIENT_ID,
      callback,
      auto_select: false,
      cancel_on_tap_outside: true,
      ux_mode: uxMode
    })
    googleInitialized = true
  }
}

export async function getGoogleIdToken() {
  return new Promise(async (resolve, reject) => {
    try {
      await ensureGoogleInit((response) => {
        if (!response?.credential) {
          reject(new Error('Google token olinmadi'))
          return
        }
        resolve(response.credential)
      })

      window.google.accounts.id.prompt((notification) => {
        if (notification?.isNotDisplayed?.()) {
          reject(new Error('Google prompt korsatilmagan'))
        }
        if (notification?.isSkippedMoment?.()) {
          reject(new Error('Google prompt bekor qilindi'))
        }
      })
    } catch (err) {
      reject(err)
    }
  })
}

export async function initGoogleOneTap({ buttonElement, onToken, uxMode = 'popup' }) {
  await ensureGoogleInit((response) => {
    if (response?.credential) {
      onToken(response.credential)
    }
  }, uxMode)

  if (buttonElement) {
    window.google.accounts.id.renderButton(buttonElement, {
      theme: 'outline',
      size: 'large',
      shape: 'pill',
      text: 'continue_with',
      width: 320
    })
  }

  window.google.accounts.id.prompt()
}
