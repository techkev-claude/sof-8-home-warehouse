import { defineStore } from 'pinia'
import * as usagePurposesApi from '../api/usagePurposes'

export const useUsagePurposesStore = defineStore('usagePurposes', {
  state: () => ({
    purposes: [],
    loaded: false,
  }),
  getters: {
    byId: (state) => (id) => state.purposes.find((p) => p.id === id),
  },
  actions: {
    async fetchPurposes() {
      this.purposes = await usagePurposesApi.listUsagePurposes()
      this.loaded = true
      return this.purposes
    },
    async createPurpose(data) {
      const purpose = await usagePurposesApi.createUsagePurpose(data)
      await this.fetchPurposes()
      return purpose
    },
    async updatePurpose(id, data) {
      const purpose = await usagePurposesApi.updateUsagePurpose(id, data)
      await this.fetchPurposes()
      return purpose
    },
    async deletePurpose(id) {
      await usagePurposesApi.deleteUsagePurpose(id)
      await this.fetchPurposes()
    },
  },
})
