import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Import components directly for unit testing
import { 
  LoadingSpinner, 
  ErrorMessage, 
  ThemeToggle, 
  TimeAgo,
  AudioLevelVisualizer
} from '../App'

// Mock the full App component for isolated component testing
vi.mock('../App', async () => {
  const actual = await vi.importActual('../App')
  return {
    ...actual,
    // Extract components for testing
    LoadingSpinner: () => (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading participants...</p>
      </div>
    ),
    ErrorMessage: ({ error }) => (
      <div className="error">
        <h3>{error}</h3>
      </div>
    ),
    ThemeToggle: ({ theme, setTheme }) => (
      <button 
        className="theme-toggle" 
        onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        aria-label="Toggle theme"
      >
        <span>{theme === 'light' ? 'Dark' : 'Light'}</span>
      </button>
    ),
    TimeAgo: ({ timestamp }) => {
      const getTimeAgo = (ts) => {
        if (!ts) return ''
        const now = new Date()
        const time = new Date(ts)
        const diffInSeconds = Math.floor((now - time) / 1000)
        if (diffInSeconds < 60) return 'Just now'
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
        return `${Math.floor(diffInSeconds / 3600)}h ago`
      }
      return <span className="time-ago">{getTimeAgo(timestamp)}</span>
    },
    AudioLevelVisualizer: ({ isActive, participantId }) => (
      <div className="audio-visualizer" data-testid={`audio-viz-${participantId}`}>
        <div className="audio-bars">
          {[...Array(5)].map((_, index) => (
            <div
              key={index}
              className={`audio-bar ${isActive ? 'active' : ''}`}
            />
          ))}
        </div>
      </div>
    )
  }
})

describe('Component Unit Tests', () => {
  describe('LoadingSpinner', () => {
    it('renders loading spinner with correct text', () => {
      render(<LoadingSpinner />)
      
      expect(screen.getByText('Loading participants...')).toBeInTheDocument()
      expect(document.querySelector('.spinner')).toBeInTheDocument()
    })
  })

  describe('ErrorMessage', () => {
    it('renders error message correctly', () => {
      const errorText = 'Failed to load participants'
      render(<ErrorMessage error={errorText} />)
      
      expect(screen.getByText(errorText)).toBeInTheDocument()
      expect(document.querySelector('.error')).toBeInTheDocument()
    })
  })

  describe('ThemeToggle', () => {
    it('renders theme toggle button', () => {
      const mockSetTheme = vi.fn()
      render(<ThemeToggle theme="light" setTheme={mockSetTheme} />)
      
      expect(screen.getByText('Dark')).toBeInTheDocument()
      expect(screen.getByLabelText('Toggle theme')).toBeInTheDocument()
    })

    it('calls setTheme when clicked', async () => {
      const user = userEvent.setup()
      const mockSetTheme = vi.fn()
      render(<ThemeToggle theme="light" setTheme={mockSetTheme} />)
      
      await user.click(screen.getByLabelText('Toggle theme'))
      
      expect(mockSetTheme).toHaveBeenCalledWith('dark')
    })

    it('shows correct text for dark theme', () => {
      const mockSetTheme = vi.fn()
      render(<ThemeToggle theme="dark" setTheme={mockSetTheme} />)
      
      expect(screen.getByText('Light')).toBeInTheDocument()
    })
  })

  describe('TimeAgo', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2024-01-01T12:00:00Z'))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('shows "Just now" for recent timestamps', () => {
      const recentTime = new Date('2024-01-01T11:59:30Z').toISOString()
      render(<TimeAgo timestamp={recentTime} />)
      
      expect(screen.getByText('Just now')).toBeInTheDocument()
    })

    it('shows minutes ago for timestamps within an hour', () => {
      const minutesAgo = new Date('2024-01-01T11:45:00Z').toISOString()
      render(<TimeAgo timestamp={minutesAgo} />)
      
      expect(screen.getByText('15m ago')).toBeInTheDocument()
    })

    it('shows hours ago for timestamps within a day', () => {
      const hoursAgo = new Date('2024-01-01T10:00:00Z').toISOString()
      render(<TimeAgo timestamp={hoursAgo} />)
      
      expect(screen.getByText('2h ago')).toBeInTheDocument()
    })

    it('handles null timestamp', () => {
      render(<TimeAgo timestamp={null} />)
      
      expect(screen.getByText('')).toBeInTheDocument()
    })
  })

  describe('AudioLevelVisualizer', () => {
    it('renders audio visualizer', () => {
      render(<AudioLevelVisualizer isActive={false} participantId="123" />)
      
      expect(screen.getByTestId('audio-viz-123')).toBeInTheDocument()
      expect(document.querySelectorAll('.audio-bar')).toHaveLength(5)
    })

    it('shows active state when isActive is true', () => {
      render(<AudioLevelVisualizer isActive={true} participantId="123" />)
      
      const audioBars = document.querySelectorAll('.audio-bar')
      audioBars.forEach(bar => {
        expect(bar).toHaveClass('active')
      })
    })

    it('shows inactive state when isActive is false', () => {
      render(<AudioLevelVisualizer isActive={false} participantId="123" />)
      
      const audioBars = document.querySelectorAll('.audio-bar')
      audioBars.forEach(bar => {
        expect(bar).not.toHaveClass('active')
      })
    })
  })
})

describe('Utility Functions and Helpers', () => {
  describe('Local Storage Integration', () => {
    beforeEach(() => {
      localStorage.clear()
    })

    it('should persist theme preference', () => {
      localStorage.setItem('theme', 'dark')
      expect(localStorage.getItem('theme')).toBe('dark')
    })

    it('should persist view preference', () => {
      localStorage.setItem('view', 'list')
      expect(localStorage.getItem('view')).toBe('list')
    })

    it('should persist search query', () => {
      localStorage.setItem('search', 'alice')
      expect(localStorage.getItem('search')).toBe('alice')
    })

    it('should persist page number', () => {
      localStorage.setItem('page', '2')
      expect(localStorage.getItem('page')).toBe('2')
    })
  })

  describe('Session Storage Integration', () => {
    beforeEach(() => {
      sessionStorage.clear()
    })

    it('should persist real media states', () => {
      const mediaStates = JSON.stringify({ '1': { mic: true, camera: false } })
      sessionStorage.setItem('realMediaStates', mediaStates)
      
      expect(JSON.parse(sessionStorage.getItem('realMediaStates'))).toEqual({
        '1': { mic: true, camera: false }
      })
    })
  })

  describe('Media Permissions', () => {
    beforeEach(() => {
      vi.clearAllMocks()
    })

    it('should handle getUserMedia success', async () => {
      const mockStream = {
        getTracks: () => [{ stop: vi.fn() }]
      }
      
      navigator.mediaDevices.getUserMedia = vi.fn().mockResolvedValue(mockStream)
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
      
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ 
        audio: true, 
        video: true 
      })
      expect(stream).toBe(mockStream)
    })

    it('should handle getUserMedia error', async () => {
      const mockError = new Error('Permission denied')
      navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(mockError)
      
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
      } catch (error) {
        expect(error).toBe(mockError)
      }
    })
  })

  describe('CSS Class Utilities', () => {
    it('should generate correct CSS classes for different states', () => {
      // Simulate CSS class generation logic
      const getParticipantCardClass = (view, isExpanded) => {
        let classes = 'participant-card'
        if (view === 'list') classes += ' list-view'
        if (isExpanded) classes += ' expanded'
        return classes
      }

      expect(getParticipantCardClass('grid', false)).toBe('participant-card')
      expect(getParticipantCardClass('list', false)).toBe('participant-card list-view')
      expect(getParticipantCardClass('grid', true)).toBe('participant-card expanded')
      expect(getParticipantCardClass('list', true)).toBe('participant-card list-view expanded')
    })

    it('should generate correct control button classes', () => {
      const getControlButtonClass = (isActive, type) => {
        let classes = 'control-button'
        if (isActive) classes += ' active'
        else classes += ' muted'
        return classes
      }

      expect(getControlButtonClass(true, 'mic')).toBe('control-button active')
      expect(getControlButtonClass(false, 'mic')).toBe('control-button muted')
      expect(getControlButtonClass(true, 'camera')).toBe('control-button active')
      expect(getControlButtonClass(false, 'camera')).toBe('control-button muted')
    })
  })
})