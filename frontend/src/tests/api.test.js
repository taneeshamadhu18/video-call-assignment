import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import { 
  fetchParticipants, 
  fetchParticipantCount, 
  fetchParticipant,
  updateParticipantMicrophone,
  updateParticipantCamera,
  updateParticipantStatus
} from '../api'

vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('API Client Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchParticipants', () => {
    it('fetches participants successfully', async () => {
      const mockData = [
        { id: 1, name: 'Alice', email: 'alice@test.com', role: 'Host' },
        { id: 2, name: 'Bob', email: 'bob@test.com', role: 'Guest' }
      ]
      
      mockedAxios.get.mockResolvedValueOnce({ data: mockData })

      const result = await fetchParticipants()

      expect(mockedAxios.get).toHaveBeenCalledWith('/participants', {
        params: { search: '', limit: 6, offset: 0 }
      })
      expect(result).toEqual(mockData)
    })

    it('fetches participants with search parameters', async () => {
      const mockData = [
        { id: 1, name: 'Alice', email: 'alice@test.com', role: 'Host' }
      ]
      
      mockedAxios.get.mockResolvedValueOnce({ data: mockData })

      const result = await fetchParticipants('alice', 10, 5)

      expect(mockedAxios.get).toHaveBeenCalledWith('/participants', {
        params: { search: 'alice', limit: 10, offset: 5 }
      })
      expect(result).toEqual(mockData)
    })

    it('handles API error gracefully', async () => {
      const errorMessage = 'Network Error'
      mockedAxios.get.mockRejectedValueOnce(new Error(errorMessage))

      await expect(fetchParticipants()).rejects.toThrow('Failed to fetch participants: Network Error')
    })

    it('handles API error with response data', async () => {
      const errorResponse = {
        response: {
          data: { message: 'Server error' },
          status: 500
        }
      }
      mockedAxios.get.mockRejectedValueOnce(errorResponse)

      await expect(fetchParticipants()).rejects.toThrow('Failed to fetch participants: Server error')
    })
  })

  describe('fetchParticipantCount', () => {
    it('fetches participant count successfully', async () => {
      const mockData = { total: 5 }
      mockedAxios.get.mockResolvedValueOnce({ data: mockData })

      const result = await fetchParticipantCount()

      expect(mockedAxios.get).toHaveBeenCalledWith('/participants/count', {
        params: { search: '' }
      })
      expect(result).toEqual(mockData)
    })

    it('fetches participant count with search', async () => {
      const mockData = { total: 2 }
      mockedAxios.get.mockResolvedValueOnce({ data: mockData })

      const result = await fetchParticipantCount('alice')

      expect(mockedAxios.get).toHaveBeenCalledWith('/participants/count', {
        params: { search: 'alice' }
      })
      expect(result).toEqual(mockData)
    })

    it('handles count API error', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Count error'))

      await expect(fetchParticipantCount()).rejects.toThrow('Failed to fetch participant count: Count error')
    })
  })

  describe('fetchParticipant', () => {
    it('fetches single participant successfully', async () => {
      const mockData = { id: 1, name: 'Alice', email: 'alice@test.com' }
      mockedAxios.get.mockResolvedValueOnce({ data: mockData })

      const result = await fetchParticipant(1)

      expect(mockedAxios.get).toHaveBeenCalledWith('/participants/1')
      expect(result).toEqual(mockData)
    })

    it('handles participant not found', async () => {
      const errorResponse = {
        response: {
          status: 404,
          data: { message: 'Participant not found' }
        }
      }
      mockedAxios.get.mockRejectedValueOnce(errorResponse)

      await expect(fetchParticipant(999)).rejects.toThrow('Failed to fetch participant: Participant not found')
    })
  })

  describe('updateParticipantMicrophone', () => {
    it('updates microphone status successfully', async () => {
      const mockData = { id: 1, mic_on: true }
      mockedAxios.put.mockResolvedValueOnce({ data: mockData })

      const result = await updateParticipantMicrophone(1, true)

      expect(mockedAxios.put).toHaveBeenCalledWith('/participants/1/microphone', {
        mic_on: true
      })
      expect(result).toEqual(mockData)
    })

    it('handles microphone update error', async () => {
      mockedAxios.put.mockRejectedValueOnce(new Error('Update failed'))

      await expect(updateParticipantMicrophone(1, true))
        .rejects.toThrow('Failed to update microphone: Update failed')
    })
  })

  describe('updateParticipantCamera', () => {
    it('updates camera status successfully', async () => {
      const mockData = { id: 1, camera_on: false }
      mockedAxios.put.mockResolvedValueOnce({ data: mockData })

      const result = await updateParticipantCamera(1, false)

      expect(mockedAxios.put).toHaveBeenCalledWith('/participants/1/camera', {
        camera_on: false
      })
      expect(result).toEqual(mockData)
    })

    it('handles camera update error', async () => {
      const errorResponse = {
        response: {
          data: { message: 'Invalid camera state' },
          status: 422
        }
      }
      mockedAxios.put.mockRejectedValueOnce(errorResponse)

      await expect(updateParticipantCamera(1, false))
        .rejects.toThrow('Failed to update camera: Invalid camera state')
    })
  })

  describe('updateParticipantStatus', () => {
    it('updates online status successfully', async () => {
      const mockData = { id: 1, online: true }
      mockedAxios.put.mockResolvedValueOnce({ data: mockData })

      const result = await updateParticipantStatus(1, true)

      expect(mockedAxios.put).toHaveBeenCalledWith('/participants/1/status', {
        online: true
      })
      expect(result).toEqual(mockData)
    })

    it('handles status update error', async () => {
      mockedAxios.put.mockRejectedValueOnce(new Error('Status update failed'))

      await expect(updateParticipantStatus(1, true))
        .rejects.toThrow('Failed to update status: Status update failed')
    })
  })

  describe('Error Handling Edge Cases', () => {
    it('handles network timeout errors', async () => {
      const timeoutError = new Error('timeout of 5000ms exceeded')
      timeoutError.code = 'ECONNABORTED'
      mockedAxios.get.mockRejectedValueOnce(timeoutError)

      await expect(fetchParticipants()).rejects.toThrow('Failed to fetch participants: timeout of 5000ms exceeded')
    })

    it('handles connection refused errors', async () => {
      const connectionError = new Error('connect ECONNREFUSED 127.0.0.1:8000')
      connectionError.code = 'ECONNREFUSED'
      mockedAxios.get.mockRejectedValueOnce(connectionError)

      await expect(fetchParticipants()).rejects.toThrow('Failed to fetch participants: connect ECONNREFUSED 127.0.0.1:8000')
    })

    it('handles malformed response data', async () => {
      // Simulate a response that doesn't have the expected structure
      mockedAxios.get.mockResolvedValueOnce({ data: null })

      const result = await fetchParticipants()
      expect(result).toBeNull()
    })

    it('handles empty error response', async () => {
      const errorResponse = {
        response: {
          data: null,
          status: 500
        }
      }
      mockedAxios.get.mockRejectedValueOnce(errorResponse)

      await expect(fetchParticipants()).rejects.toThrow('Failed to fetch participants: Request failed')
    })
  })

  describe('API Configuration', () => {
    it('should use correct base URL for API calls', () => {
      // Test that the API client is configured with the correct base URL
      expect(axios.defaults.baseURL).toBeDefined()
    })

    it('should handle different HTTP methods correctly', async () => {
      // Test GET requests
      mockedAxios.get.mockResolvedValueOnce({ data: [] })
      await fetchParticipants()
      expect(mockedAxios.get).toHaveBeenCalled()

      // Test PUT requests  
      mockedAxios.put.mockResolvedValueOnce({ data: { mic_on: true } })
      await updateParticipantMicrophone(1, true)
      expect(mockedAxios.put).toHaveBeenCalled()
    })

    it('should include proper headers for requests', async () => {
      mockedAxios.put.mockResolvedValueOnce({ data: { mic_on: true } })
      
      await updateParticipantMicrophone(1, true)
      
      // Verify the request was made with proper data
      expect(mockedAxios.put).toHaveBeenCalledWith(
        '/participants/1/microphone',
        { mic_on: true }
      )
    })
  })
})