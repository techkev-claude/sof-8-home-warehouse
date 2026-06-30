import { defineStore } from 'pinia'
import * as locationsApi from '../api/locations'

export const useLocationsStore = defineStore('locations', {
  state: () => ({
    flat: [],
    tree: [],
    loaded: false,
  }),
  getters: {
    byId: (state) => (id) => state.flat.find((loc) => loc.id === id),
  },
  actions: {
    async fetchFlat() {
      this.flat = await locationsApi.listLocations()
      return this.flat
    },
    async fetchTree() {
      this.tree = await locationsApi.getLocationTree()
      return this.tree
    },
    async fetchAll() {
      await Promise.all([this.fetchFlat(), this.fetchTree()])
      this.loaded = true
    },
    async createLocation(data) {
      const location = await locationsApi.createLocation(data)
      await this.fetchAll()
      return location
    },
    async updateLocation(id, data) {
      const location = await locationsApi.updateLocation(id, data)
      await this.fetchAll()
      return location
    },
    async deleteLocation(id) {
      await locationsApi.deleteLocation(id)
      await this.fetchAll()
    },
  },
})
