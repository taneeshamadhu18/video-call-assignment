# AiRoHire Participants Management System

A modern React web application for managing AiRoHire participants with real-time media controls, search functionality, and responsive design.

## 🚀 Features

- **Participant Management**: Search, filter, and paginate through participants
- **Real-time Media Controls**: Toggle microphone and camera states
- **Dual Media Support**: Both database-persisted and real webcam/microphone integration
- **Audio Visualization**: Real-time audio level visualization with Web Audio API
- **Theme Support**: Light/Dark mode toggle
- **Responsive Design**: Mobile, tablet, and desktop optimized
- **State Persistence**: Survives page refreshes
- **Modern UI**: Smooth animations, hover effects, and professional design

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend API running (see backend README)

### Installation

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   - Ensure backend API is running on `http://localhost:8000`
   - Frontend will automatically connect to backend API

4. **Start Development Server**
   ```bash
   npm run dev
   ```

5. **Access Application**
   - Frontend: http://localhost:5173 (or next available port)
   - The app will automatically open in your browser

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run test         # Run tests (Vitest)
npm run test:ui      # Run tests with UI
npm run test:coverage # Run tests with coverage
```

## 🏗️ Architecture Overview

### Component Architecture
```
App (Root Component)
├── ThemeToggle          # Theme switching functionality
├── LoadingSpinner       # Loading state component
├── ErrorMessage         # Error handling component
├── AudioLevelVisualizer # Real-time audio visualization
├── ParticipantCard      # Individual participant display
├── ParticipantModal     # Detailed participant view
└── TimeAgo             # Relative time display
```

### State Management
- **React Hooks**: useState, useEffect for local state
- **Custom Hooks**: useDebounce for search optimization
- **Persistence**: localStorage/sessionStorage for state persistence
- **Media State**: Separate state for real camera/microphone access

### Key Dependencies
- **React 19.2.0**: Core UI framework
- **Vite 7.2.4**: Fast build tool and dev server
- **Lucide React**: Modern icon library
- **Axios**: HTTP client with interceptors

### File Structure
```
src/
├── App.jsx              # Main application component
├── App.css              # Global styles and themes
├── api.js               # API client and helper functions
├── main.jsx             # Application entry point
├── index.css            # Base styles
└── tests/
    ├── App.test.jsx     # Component tests
    └── setup.js         # Test configuration
```

## 🔌 API Design Explanation

### API Client (`api.js`)
- **Axios Instance**: Configured with base URL and timeout
- **Error Handling**: Comprehensive error interceptors
- **Helper Functions**: Abstracted API calls with proper error handling

### API Integration Points

#### Participant Management
```javascript
fetchParticipants(search, page, limit)    // Get paginated participants
fetchParticipantCount(search)             // Get total count
fetchParticipant(id)                      // Get single participant
```

#### Media Controls
```javascript
updateParticipantMicrophone(id, micOn)    // Toggle microphone
updateParticipantCamera(id, cameraOn)     // Toggle camera
updateParticipantStatus(id, online)       // Update online status
```

### Error Handling Strategy
- **Request Interceptors**: Automatic timeout and retry logic
- **Response Interceptors**: Centralized error logging
- **UI Error States**: User-friendly error messages
- **Fallback Mechanisms**: Graceful degradation

### Data Flow
```
User Action → Component State → API Call → Backend → Database
     ↓              ↑              ↓          ↓         ↓
UI Update ← State Update ← Response ← API ← Database
```

## 🗄️ Database Design Rationale

### Frontend Data Modeling

#### Participant Object Structure
```javascript
{
  id: number,              // Unique identifier
  name: string,            // Full name
  email: string,           // Contact email
  role: "Host" | "Guest",  // Participant role
  online: boolean,         // Current status
  mic_on: boolean,         // Microphone state
  camera_on: boolean,      // Camera state
  about_me: string,        // Description
  resume_url: string,      // Optional resume link
  created_at: string,      // ISO timestamp
  updated_at: string       // ISO timestamp
}
```

#### State Management Rationale

**Local State Organization:**
- `participants`: Array of participant objects
- `search`: Search query string
- `page`: Current pagination page
- `view`: Display mode (grid/list)
- `theme`: UI theme preference
- `realMediaStates`: Hardware media access states

**Persistence Strategy:**
- **localStorage**: User preferences (theme, view, search, page)
- **sessionStorage**: Temporary states (real media access)
- **Component State**: UI-specific temporary states

### Data Synchronization
- **Optimistic Updates**: Immediate UI feedback
- **Error Recovery**: Revert on API failure
- **Timestamp Tracking**: Display relative time for updates
- **State Consistency**: Backend as source of truth

### Performance Optimizations
- **Debounced Search**: 300ms delay to reduce API calls
- **Pagination**: Limit data fetching to 6 items per page
- **Memoization**: Prevent unnecessary re-renders
- **Lazy Loading**: Progressive data loading

## 🎨 UI/UX Design Principles

### Responsive Design
- **Mobile First**: Progressive enhancement approach
- **Breakpoints**: 640px, 768px, 1024px
- **Flexible Grid**: CSS Grid with responsive columns
- **Touch Friendly**: Large tap targets for mobile

### Theme System
- **CSS Variables**: Consistent color system
- **Dark/Light Mode**: System preference detection
- **Smooth Transitions**: Theme switching animations
- **Accessibility**: Proper contrast ratios

### Component Design
- **Atomic Design**: Reusable component architecture
- **Props Interface**: Clear component APIs
- **Error Boundaries**: Graceful error handling
- **Loading States**: Progressive disclosure

## 🔧 Development Workflow

### Code Quality
- **ESLint**: Code linting and style enforcement
- **Prettier**: Code formatting (if configured)
- **Component Testing**: React Testing Library
- **Type Safety**: PropTypes validation

### Testing Strategy
- **Unit Tests**: Component behavior testing
- **Integration Tests**: API interaction testing
- **UI Tests**: User interaction testing
- **Error Scenarios**: Edge case handling

### Build Optimization
- **Vite Bundling**: Fast development and production builds
- **Code Splitting**: Automatic chunk splitting
- **Asset Optimization**: Image and resource optimization
- **Tree Shaking**: Dead code elimination

## 📱 Browser Compatibility

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Required APIs
- **getUserMedia**: Camera and microphone access
- **Web Audio API**: Audio visualization
- **CSS Grid**: Layout system
- **ES6 Modules**: Modern JavaScript features

## 🚀 Deployment

### Production Build
```bash
npm run build        # Creates dist/ directory
npm run preview      # Test production build locally
```

### Environment Variables
- No environment variables required for basic setup
- API URL can be configured in `api.js`

### Hosting Options
- **Vercel**: Automatic deployment from Git
- **Netlify**: Static site hosting
- **AWS S3**: Static website hosting
- **GitHub Pages**: Free hosting option

## 🔍 Troubleshooting

### Common Issues
1. **Media Access Denied**: Check browser permissions
2. **API Connection**: Verify backend is running
3. **Port Conflicts**: Vite will find next available port
4. **Build Errors**: Clear node_modules and reinstall

### Development Tips
- Use browser DevTools for debugging
- Check Network tab for API calls
- Enable React DevTools extension
- Monitor console for errors and warnings

---

This frontend provides a robust, scalable foundation for video call participant management with modern React patterns and comprehensive feature set.
