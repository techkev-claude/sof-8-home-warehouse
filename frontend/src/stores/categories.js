import { defineStore } from 'pinia'
import * as categoriesApi from '../api/categories'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    categories: [],
    loaded: false,
  }),
  getters: {
    byId: (state) => (id) => state.categories.find((cat) => cat.id === id),
  },
  actions: {
    async fetchCategories() {
      this.categories = await categoriesApi.listCategories()
      this.loaded = true
      return this.categories
    },
    async createCategory(data) {
      const category = await categoriesApi.createCategory(data)
      await this.fetchCategories()
      return category
    },
    async updateCategory(id, data) {
      const category = await categoriesApi.updateCategory(id, data)
      await this.fetchCategories()
      return category
    },
    async deleteCategory(id) {
      await categoriesApi.deleteCategory(id)
      await this.fetchCategories()
    },
  },
})
