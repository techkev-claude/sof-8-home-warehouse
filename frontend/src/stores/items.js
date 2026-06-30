import { defineStore } from 'pinia'
import * as itemsApi from '../api/items'

const DEFAULT_LIMIT = 50

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
    hasMore: true,
    filters: {
      status: '',
      category_id: null,
      location_id: null,
      search: '',
    },
  }),
  actions: {
    async fetchItems({ reset = true } = {}) {
      this.loading = true
      this.error = null
      try {
        const skip = reset ? 0 : this.items.length
        const params = { skip, limit: DEFAULT_LIMIT }
        if (this.filters.status) params.status = this.filters.status
        if (this.filters.category_id) params.category_id = this.filters.category_id
        if (this.filters.location_id) params.location_id = this.filters.location_id
        if (this.filters.search) params.search = this.filters.search

        const result = await itemsApi.listItems(params)
        this.items = reset ? result : [...this.items, ...result]
        this.hasMore = result.length === DEFAULT_LIMIT
      } catch (err) {
        this.error = err
        throw err
      } finally {
        this.loading = false
      }
    },
    async loadMore() {
      if (!this.hasMore || this.loading) return
      await this.fetchItems({ reset: false })
    },
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },
    async removeItem(id) {
      await itemsApi.deleteItem(id)
      this.items = this.items.filter((item) => item.id !== id)
    },
  },
})
