import { describe, it, expect, beforeEach, vi } from 'vitest'
import { api } from './api'

global.fetch = vi.fn()

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('listTransactions', () => {
    it('should fetch transactions successfully', async () => {
      const mockTransactions = [
        { id: 1, date: '2024-01-01', description: 'Test', amount: 100 },
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTransactions,
      })

      const result = await api.listTransactions()

      expect(result).toEqual(mockTransactions)
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/transactions',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should throw error on failed request', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        text: async () => 'Error message',
      })

      await expect(api.listTransactions()).rejects.toThrow()
    })
  })

  describe('createCategory', () => {
    it('should create a category', async () => {
      const newCategory = { name: 'Test', type: 'expense' as const, color: '#000' }
      const mockResponse = { id: 1, ...newCategory }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await api.createCategory(newCategory)

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/categories',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(newCategory),
        })
      )
    })
  })

  describe('updateTransaction', () => {
    it('should update a transaction', async () => {
      const updates = { category_id: 5 }
      const mockResponse = { id: 1, ...updates }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await api.updateTransaction(1, updates)

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/transactions/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(updates),
        })
      )
    })
  })
})
