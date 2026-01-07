import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import App from '../src/App'
import * as api from '../src/api'

// Mock the API module
vi.mock('../src/api')

describe('App Component', () => {
  const mockParticipants = [
    {
      id: 1,
      name: 'Alice Johnson',
      email: 'alice@test.com',
      role: 'Host',
      online: true,
      mic_on: true,
      camera_on: true,
      about_me: 'Frontend engineer',
      resume_url: 'https://example.com/alice.pdf',
      created_at: '2024-12-08T10:00:00Z',
      updated_at: '2024-12-08T12:00:00Z'
    },
    {
      id: 2,
      name: 'Bob Smith',
      email: 'bob@test.com',
      role: 'Guest',
      online: false,
      mic_on: false,
      camera_on: false,
      about_me: 'Backend developer',
      resume_url: null,
      created_at: '2024-12-08T11:00:00Z',
      updated_at: '2024-12-08T13:00:00Z'
    }
  ]

  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks()
    
    // Setup default mock implementations
    api.fetchParticipants.mockResolvedValue(mockParticipants)
    api.fetchParticipantCount.mockResolvedValue(2)
    api.updateParticipantMicrophone.mockImplementation((id, micOn) => {
      const participant = mockParticipants.find(p => p.id === id)
      return Promise.resolve({ ...participant, mic_on: micOn })
    })
    api.updateParticipantCamera.mockImplementation((id, cameraOn) => {
      const participant = mockParticipants.find(p => p.id === id)
      return Promise.resolve({ ...participant, camera_on: cameraOn })
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Participant List', () => {
    it('renders participant list correctly', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
        expect(screen.getByText('Bob Smith')).toBeInTheDocument()
      })
    })

    it('displays participant status correctly', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Host')).toBeInTheDocument()
        expect(screen.getByText('Guest')).toBeInTheDocument()
      })
    })

    it('shows online/offline status', async () => {
      render(<App />)
      
      await waitFor(() => {
        const onlineIndicators = document.querySelectorAll('.status.online')
        const offlineIndicators = document.querySelectorAll('.status.offline')
        
        expect(onlineIndicators).toHaveLength(1)
        expect(offlineIndicators).toHaveLength(1)
      })
    })
  })

  describe('Search Functionality', () => {
    it('calls fetchParticipants with search query', async () => {
      render(<App />)
      
      const searchInput = screen.getByPlaceholderText('Search participants...')
      fireEvent.change(searchInput, { target: { value: 'Alice' } })
      
      // Wait for debounced search
      await waitFor(() => {
        expect(api.fetchParticipants).toHaveBeenCalledWith('Alice', 1, 6)
      }, { timeout: 1000 })
    })

    it('updates participant list based on search', async () => {
      const filteredParticipants = [mockParticipants[0]]
      api.fetchParticipants.mockResolvedValue(filteredParticipants)
      
      render(<App />)
      
      const searchInput = screen.getByPlaceholderText('Search participants...')
      fireEvent.change(searchInput, { target: { value: 'Alice' } })
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
        expect(screen.queryByText('Bob Smith')).not.toBeInTheDocument()
      })
    })
  })

  describe('Media Controls', () => {
    it('toggles microphone state', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      })
      
      // Find microphone button for Alice (assuming it's the first participant)
      const micButtons = document.querySelectorAll('[data-testid="mic-button"]')
      fireEvent.click(micButtons[0])
      
      await waitFor(() => {
        expect(api.updateParticipantMicrophone).toHaveBeenCalledWith(1, false)
      })
    })

    it('toggles camera state', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      })
      
      // Find camera button for Alice
      const cameraButtons = document.querySelectorAll('[data-testid="camera-button"]')
      fireEvent.click(cameraButtons[0])
      
      await waitFor(() => {
        expect(api.updateParticipantCamera).toHaveBeenCalledWith(1, false)
      })
    })
  })

  describe('View Modes', () => {
    it('switches between grid and list view', async () => {
      render(<App />)
      
      // Check initial grid view
      expect(document.querySelector('.participant-grid')).toBeInTheDocument()
      
      // Switch to list view
      const listButton = screen.getByLabelText('List view')
      fireEvent.click(listButton)
      
      expect(document.querySelector('.participant-list')).toBeInTheDocument()
    })
  })

  describe('Theme Toggle', () => {
    it('toggles between light and dark theme', async () => {
      render(<App />)
      
      const themeButton = screen.getByLabelText('Toggle theme')
      fireEvent.click(themeButton)
      
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
      
      fireEvent.click(themeButton)
      
      expect(document.documentElement.getAttribute('data-theme')).toBe('light')
    })
  })

  describe('Participant Modal', () => {
    it('opens participant details modal', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      })
      
      // Click on details button
      const detailsButton = screen.getAllByText('More Details')[0]
      fireEvent.click(detailsButton)
      
      await waitFor(() => {
        expect(screen.getByText('Frontend engineer')).toBeInTheDocument()
      })
    })

    it('closes modal when clicking close button', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      })
      
      // Open modal
      const detailsButton = screen.getAllByText('More Details')[0]
      fireEvent.click(detailsButton)
      
      // Close modal
      const closeButton = screen.getByLabelText('Close modal')
      fireEvent.click(closeButton)
      
      await waitFor(() => {
        expect(screen.queryByText('Frontend engineer')).not.toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message when API fails', async () => {
      api.fetchParticipants.mockRejectedValue(new Error('Network error'))
      
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText(/Network error/)).toBeInTheDocument()
      })
    })

    it('clears error message after timeout', async () => {
      api.updateParticipantMicrophone.mockRejectedValue(new Error('Update failed'))
      
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      })
      
      // Try to update microphone to trigger error
      const micButtons = document.querySelectorAll('[data-testid="mic-button"]')
      fireEvent.click(micButtons[0])
      
      await waitFor(() => {
        expect(screen.getByText(/Update failed/)).toBeInTheDocument()
      })
      
      // Wait for error to clear (assuming 3 second timeout)
      await waitFor(() => {
        expect(screen.queryByText(/Update failed/)).not.toBeInTheDocument()
      }, { timeout: 4000 })
    })
  })

  describe('Loading States', () => {
    it('shows loading indicator while fetching participants', async () => {
      // Mock a delayed response
      api.fetchParticipants.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(mockParticipants), 100))
      )
      
      render(<App />)
      
      expect(screen.getByLabelText('Loading')).toBeInTheDocument()
      
      await waitFor(() => {
        expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
      })
    })
  })

  describe('Pagination', () => {
    it('handles pagination correctly', async () => {
      render(<App />)
      
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      })
      
      // Click next page button
      const nextButton = screen.getByLabelText('Next page')
      fireEvent.click(nextButton)
      
      await waitFor(() => {
        expect(api.fetchParticipants).toHaveBeenCalledWith('', 2, 6)
      })
    })
  })
})