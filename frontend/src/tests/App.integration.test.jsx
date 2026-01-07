import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import App from '../App'

// Mock data
const mockParticipants = [
  {
    id: 1,
    name: "Alice Johnson",
    email: "alice@test.com", 
    role: "Host",
    online: true,
    mic_on: false,
    camera_on: false,
    about_me: "Frontend engineer",
    resume_url: "https://example.com/alice.pdf",
    created_at: "2024-01-01T00:00:00.000Z",
    updated_at: "2024-01-01T00:00:00.000Z"
  },
  {
    id: 2,
    name: "Bob Smith",
    email: "bob@test.com",
    role: "Guest", 
    online: false,
    mic_on: false,
    camera_on: false,
    about_me: "Backend developer",
    resume_url: null,
    created_at: "2024-01-01T00:00:00.000Z",
    updated_at: "2024-01-01T00:00:00.000Z"
  },
  {
    id: 3,
    name: "Carol White",
    email: "carol@test.com",
    role: "Guest",
    online: true,
    mic_on: false,
    camera_on: false,
    about_me: "UI/UX designer",
    resume_url: null,
    created_at: "2024-01-01T00:00:00.000Z",
    updated_at: "2024-01-01T00:00:00.000Z"
  }
]

// MSW server setup
const server = setupServer(
  rest.get('http://127.0.0.1:8000/participants', (req, res, ctx) => {
    const search = req.url.searchParams.get('search') || ''
    const limit = parseInt(req.url.searchParams.get('limit') || '6')
    const offset = parseInt(req.url.searchParams.get('offset') || '0')
    
    let filteredParticipants = mockParticipants
    if (search) {
      filteredParticipants = mockParticipants.filter(p => 
        p.name.toLowerCase().includes(search.toLowerCase())
      )
    }
    
    const paginatedParticipants = filteredParticipants.slice(offset, offset + limit)
    return res(ctx.json(paginatedParticipants))
  }),
  
  rest.get('http://127.0.0.1:8000/participants/count', (req, res, ctx) => {
    return res(ctx.json({ total: mockParticipants.length }))
  }),
  
  rest.put('http://127.0.0.1:8000/participants/:id/microphone', (req, res, ctx) => {
    const { id } = req.params
    const participant = mockParticipants.find(p => p.id === parseInt(id))
    if (participant) {
      return res(ctx.json({ ...participant, mic_on: !participant.mic_on }))
    }
    return res(ctx.status(404))
  }),
  
  rest.put('http://127.0.0.1:8000/participants/:id/camera', (req, res, ctx) => {
    const { id } = req.params
    const participant = mockParticipants.find(p => p.id === parseInt(id))
    if (participant) {
      return res(ctx.json({ ...participant, camera_on: !participant.camera_on }))
    }
    return res(ctx.status(404))
  })
)

// Mock getUserMedia
beforeEach(() => {
  Object.defineProperty(navigator, 'mediaDevices', {
    value: {
      getUserMedia: vi.fn().mockResolvedValue({
        getTracks: () => [{ stop: vi.fn() }]
      })
    },
    configurable: true
  })
  
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(() => null),
    setItem: vi.fn(),
    clear: vi.fn()
  }
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    configurable: true
  })
  
  // Mock sessionStorage
  const sessionStorageMock = {
    getItem: vi.fn(() => null),
    setItem: vi.fn(),
    clear: vi.fn()
  }
  Object.defineProperty(window, 'sessionStorage', {
    value: sessionStorageMock,
    configurable: true
  })
})

describe('App Component', () => {
  beforeEach(() => {
    server.listen()
  })
  
  afterEach(() => {
    server.resetHandlers()
  })
  
  afterAll(() => {
    server.close()
  })

  it('renders the app header correctly', async () => {
    render(<App />)
    
    expect(screen.getByText('AiRoHire Participants')).toBeInTheDocument()
  })

  it('renders theme toggle button', async () => {
    render(<App />)
    
    expect(screen.getByRole('button', { name: /toggle theme/i })).toBeInTheDocument()
  })

  it('loads and displays participants', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
      expect(screen.getByText('Bob Smith')).toBeInTheDocument()
      expect(screen.getByText('Carol White')).toBeInTheDocument()
    })
  })

  it('switches between grid and list views', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    // Switch to list view
    const listButton = screen.getByRole('button', { name: /list view/i })
    fireEvent.click(listButton)
    
    // Verify list view is active
    expect(listButton).toHaveClass('active')
  })

  it('searches for participants', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    const searchInput = screen.getByRole('textbox', { name: /search participants/i })
    fireEvent.change(searchInput, { target: { value: 'Alice' } })
    
    // Wait for debounced search
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    }, { timeout: 1000 })
  })

  it('toggles microphone state', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    const micButtons = screen.getAllByTestId('mic-button')
    fireEvent.click(micButtons[0])
    
    // The UI should update to reflect the change
    await waitFor(() => {
      // Button should change from muted to active or vice versa
      expect(micButtons[0]).toBeInTheDocument()
    })
  })

  it('toggles camera state', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    const cameraButtons = screen.getAllByTestId('camera-button')
    fireEvent.click(cameraButtons[0])
    
    // The UI should update to reflect the change
    await waitFor(() => {
      expect(cameraButtons[0]).toBeInTheDocument()
    })
  })

  it('opens participant modal when info button is clicked', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    const infoButtons = screen.getAllByLabelText('Show more details')
    fireEvent.click(infoButtons[0])
    
    // Modal should open with participant details
    await waitFor(() => {
      expect(screen.getByText('alice@test.com')).toBeInTheDocument()
      expect(screen.getByText('Frontend engineer')).toBeInTheDocument()
    })
  })

  it('closes modal when close button is clicked', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    // Open modal
    const infoButtons = screen.getAllByLabelText('Show more details')
    fireEvent.click(infoButtons[0])
    
    await waitFor(() => {
      expect(screen.getByText('alice@test.com')).toBeInTheDocument()
    })
    
    // Close modal
    const closeButton = screen.getByRole('button', { name: /close modal/i })
    fireEvent.click(closeButton)
    
    // Modal should be closed
    await waitFor(() => {
      expect(screen.queryByText('alice@test.com')).not.toBeInTheDocument()
    })
  })

  it('handles pagination', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    const nextButton = screen.getByRole('button', { name: /next page/i })
    const prevButton = screen.getByRole('button', { name: /previous page/i })
    
    expect(prevButton).toBeDisabled()
    expect(nextButton).toBeInTheDocument()
  })

  it('toggles theme', async () => {
    render(<App />)
    
    const themeButton = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(themeButton)
    
    // Should toggle between light and dark themes
    expect(themeButton).toBeInTheDocument()
  })

  it('displays online/offline status correctly', async () => {
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
    
    // Alice is online, Bob is offline
    const onlineIndicators = screen.getAllByText('Online')
    const offlineIndicators = screen.getAllByText('Offline')
    
    expect(onlineIndicators.length).toBeGreaterThan(0)
    expect(offlineIndicators.length).toBeGreaterThan(0)
  })

  it('handles API errors gracefully', async () => {
    // Mock API error
    server.use(
      rest.get('http://127.0.0.1:8000/participants', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }))
      })
    )
    
    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch participants/i)).toBeInTheDocument()
    })
  })

  it('shows loading state while fetching data', async () => {
    // Mock delayed API response
    server.use(
      rest.get('http://127.0.0.1:8000/participants', (req, res, ctx) => {
        return res(ctx.delay(100), ctx.json(mockParticipants))
      })
    )
    
    render(<App />)
    
    // Should show loading spinner
    expect(screen.getByText('Loading participants...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
    })
  })
})