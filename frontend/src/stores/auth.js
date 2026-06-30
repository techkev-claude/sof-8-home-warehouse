import { defineStore } from 'pinia'
import * as authApi from '../api/auth'
import { getToken, setToken, setUnauthorizedHandler } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(),
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isViewer: (state) => state.user?.role === 'viewer',
    canEdit: (state) => state.user?.role === 'admin' || state.user?.role === 'member',
  },
  actions: {
    async login(username, password) {
      const { access_token } = await authApi.login(username, password)
      this.token = access_token
      setToken(access_token)
      await this.fetchMe()
    },
    async fetchMe() {
      this.user = await authApi.fetchMe()
      return this.user
    },
    logout() {
      this.token = null
      this.user = null
      setToken(null)
    },
  },
})

// Wired here (rather than in client.js) to avoid a circular import between
// the store and the axios client while still reacting to 401s globally.
export function registerAuthInterceptor() {
  const store = useAuthStore()
  setUnauthorizedHandler(() => {
    store.token = null
    store.user = null
  })
}
