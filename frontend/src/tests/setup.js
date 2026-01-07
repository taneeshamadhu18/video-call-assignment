import '@testing-library/jest-dom'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock navigator.mediaDevices
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [{
        stop: vi.fn(),
        kind: 'audio',
        enabled: true
      }]
    }),
    enumerateDevices: vi.fn().mockResolvedValue([])
  }
})

// Mock AudioContext
window.AudioContext = vi.fn().mockImplementation(() => ({
  createAnalyser: vi.fn().mockReturnValue({
    fftSize: 256,
    frequencyBinCount: 128,
    getByteFrequencyData: vi.fn(),
    connect: vi.fn()
  }),
  createMediaStreamSource: vi.fn().mockReturnValue({
    connect: vi.fn()
  }),
  close: vi.fn(),
  state: 'running'
}))

window.webkitAudioContext = window.AudioContext