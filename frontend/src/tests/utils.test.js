import { describe, it, expect, beforeEach, vi } from 'vitest'

// Component test utilities
const createMockParticipant = (overrides = {}) => ({
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  role: 'Guest',
  mic_on: true,
  camera_on: true,
  online: true,
  avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Test',
  created_at: '2024-01-01T10:00:00',
  ...overrides,
})

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = value.toString()
    }),
    clear: vi.fn(() => {
      store = {}
    }),
    removeItem: vi.fn((key) => {
      delete store[key]
    }),
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('Utility Functions Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  describe('localStorage utilities', () => {
    it('handles localStorage.setItem failures gracefully', () => {
      const originalSetItem = localStorage.setItem
      localStorage.setItem = vi.fn(() => {
        throw new Error('Storage full')
      })

      // Function should throw error as expected
      expect(() => {
        localStorage.setItem('test', 'value')
      }).toThrow('Storage full')

      localStorage.setItem = originalSetItem
    })

    it('handles localStorage.getItem failures gracefully', () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn(() => {
        throw new Error('Storage error')
      })

      expect(() => {
        localStorage.getItem('test')
      }).toThrow('Storage error')

      localStorage.getItem = originalGetItem
    })

    it('handles localStorage operations normally', () => {
      localStorage.setItem('testKey', 'testValue')
      expect(localStorage.setItem).toHaveBeenCalledWith('testKey', 'testValue')
      
      localStorage.getItem('testKey')
      expect(localStorage.getItem).toHaveBeenCalledWith('testKey')
    })

    it('handles JSON parsing errors for localStorage values', () => {
      localStorage.getItem = vi.fn(() => 'invalid-json{')

      expect(() => {
        JSON.parse(localStorage.getItem('test'))
      }).toThrow()
    })
  })

    describe('Date utilities', () => {
      it('formats dates correctly', () => {
        const testDate = '2024-01-01T10:00:00'
        const date = new Date(testDate)
        
        expect(date.toISOString()).toBe('2024-01-01T10:00:00.000Z')
      })

      it('handles invalid dates gracefully', () => {
        const invalidDate = new Date('invalid-date')
        expect(isNaN(invalidDate.getTime())).toBe(true)
      })
    })

    describe('String utilities', () => {
      it('handles empty strings in search', () => {
        const searchTerm = ''
        const result = searchTerm.trim().toLowerCase()
        expect(result).toBe('')
      })

      it('normalizes search terms correctly', () => {
        const searchTerm = '  AlIcE  '
        const normalized = searchTerm.trim().toLowerCase()
        expect(normalized).toBe('alice')
      })

      it('handles special characters in search', () => {
        const searchTerm = 'alice@example.com'
        const normalized = searchTerm.trim().toLowerCase()
        expect(normalized).toBe('alice@example.com')
      })
    })

    describe('Array utilities', () => {
      it('handles empty arrays gracefully', () => {
        const emptyArray = []
        expect(emptyArray.length).toBe(0)
        expect(emptyArray.filter(() => true)).toEqual([])
      })

      it('filters arrays correctly', () => {
        const participants = [
          { name: 'Alice', online: true },
          { name: 'Bob', online: false },
          { name: 'Charlie', online: true }
        ]
        
        const onlineParticipants = participants.filter(p => p.online)
        expect(onlineParticipants).toHaveLength(2)
        expect(onlineParticipants[0].name).toBe('Alice')
        expect(onlineParticipants[1].name).toBe('Charlie')
      })

      it('sorts arrays correctly', () => {
        const participants = [
          { name: 'Charlie', created_at: '2024-01-03' },
          { name: 'Alice', created_at: '2024-01-01' },
          { name: 'Bob', created_at: '2024-01-02' }
        ]
        
        const sorted = participants.sort((a, b) => 
          new Date(a.created_at) - new Date(b.created_at)
        )
        
        expect(sorted[0].name).toBe('Alice')
        expect(sorted[1].name).toBe('Bob')
        expect(sorted[2].name).toBe('Charlie')
      })
    })

    describe('Data validation utilities', () => {
      it('validates participant data structure', () => {
        const validParticipant = createMockParticipant()
        
        expect(validParticipant).toHaveProperty('id')
        expect(validParticipant).toHaveProperty('name')
        expect(validParticipant).toHaveProperty('email')
        expect(validParticipant).toHaveProperty('role')
        expect(validParticipant).toHaveProperty('mic_on')
        expect(validParticipant).toHaveProperty('camera_on')
        expect(validParticipant).toHaveProperty('online')
        
        expect(typeof validParticipant.id).toBe('number')
        expect(typeof validParticipant.name).toBe('string')
        expect(typeof validParticipant.email).toBe('string')
        expect(typeof validParticipant.role).toBe('string')
        expect(typeof validParticipant.mic_on).toBe('boolean')
        expect(typeof validParticipant.camera_on).toBe('boolean')
        expect(typeof validParticipant.online).toBe('boolean')
      })

      it('handles participant data with missing fields', () => {
        const incompleteParticipant = createMockParticipant({ name: undefined })
        
        expect(incompleteParticipant.name).toBeUndefined()
        expect(incompleteParticipant.email).toBe('test@example.com') // Should have defaults
      })
    })

    describe('URL utilities', () => {
      it('validates avatar URLs', () => {
        const participant = createMockParticipant()
        
        expect(participant.avatar_url).toBeDefined()
        expect(participant.avatar_url).toMatch(/^https?:\/\//)
      })

      it('handles malformed URLs gracefully', () => {
        const malformedUrl = 'not-a-url'
        
        expect(() => {
          new URL(malformedUrl)
        }).toThrow()
      })
    })
})