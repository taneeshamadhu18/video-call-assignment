import { useEffect, useState, useRef } from "react";
import { 
  Search, 
  Grid3X3, 
  List, 
  Mic, 
  MicOff, 
  Video, 
  VideoOff, 
  Sun, 
  Moon, 
  ChevronLeft, 
  ChevronRight, 
  X, 
  ExternalLink,
  Loader2,
  AlertCircle,
  Info,
  Play,
  Pause
} from "lucide-react";
import { 
  api, 
  fetchParticipants, 
  fetchParticipantCount,
  fetchParticipant,
  updateParticipantMicrophone,
  updateParticipantCamera,
  updateParticipantStatus
} from "./api";
import "./App.css";

// Audio Level Visualizer Component
function AudioLevelVisualizer({ isActive, participantId }) {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const [audioLevel, setAudioLevel] = useState(0);

  useEffect(() => {
    if (!isActive) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      setAudioLevel(0);
      return;
    }

    const setupAudioAnalysis = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        
        const source = audioContextRef.current.createMediaStreamSource(stream);
        source.connect(analyserRef.current);
        
        analyserRef.current.fftSize = 256;
        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const updateAudioLevel = () => {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((acc, val) => acc + val, 0) / bufferLength;
          const normalizedLevel = Math.min(average / 128, 1);
          setAudioLevel(normalizedLevel);
          
          if (isActive) {
            animationRef.current = requestAnimationFrame(updateAudioLevel);
          }
        };

        updateAudioLevel();
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    };

    setupAudioAnalysis();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, [isActive, participantId]);

  return (
    <div className="audio-visualizer">
      <div className="audio-bars">
        {[...Array(5)].map((_, index) => (
          <div
            key={index}
            className={`audio-bar ${isActive && audioLevel > (index * 0.2) ? 'active' : ''}`}
            style={{
              height: isActive ? `${Math.max(20, audioLevel * 100)}%` : '20%',
              animationDelay: `${index * 0.1}s`
            }}
          />
        ))}
      </div>
    </div>
  );
}

// Time Ago Component
function TimeAgo({ timestamp }) {
  const [timeAgo, setTimeAgo] = useState('');

  useEffect(() => {
    if (!timestamp) return;

    const updateTimeAgo = () => {
      const now = new Date();
      const time = new Date(timestamp);
      const diffInSeconds = Math.floor((now - time) / 1000);

      if (diffInSeconds < 60) {
        setTimeAgo('Just now');
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        setTimeAgo(`${minutes}m ago`);
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        setTimeAgo(`${hours}h ago`);
      } else {
        const days = Math.floor(diffInSeconds / 86400);
        setTimeAgo(`${days}d ago`);
      }
    };

    updateTimeAgo();
    const interval = setInterval(updateTimeAgo, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [timestamp]);

  return <span className="time-ago">{timeAgo}</span>;
}

// Theme Toggle Component
function ThemeToggle({ theme, setTheme }) {
  return (
    <button 
      className="theme-toggle" 
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      aria-label="Toggle theme"
    >
      {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
      <span>{theme === 'light' ? 'Dark' : 'Light'}</span>
    </button>
  );
}

// Loading Component
function LoadingSpinner() {
  return (
    <div className="loading">
      <div className="spinner">
        <Loader2 className="animate-spin" size={40} />
      </div>
      <p>Loading participants...</p>
    </div>
  );
}

// Error Component
function ErrorMessage({ error }) {
  return (
    <div className="error">
      <AlertCircle size={24} />
      <h3>{error}</h3>
    </div>
  );
}

// Participant Card Component
function ParticipantCard({ participant, view, onShowDetails, onToggleMedia, onToggleRealMedia, realMediaStates }) {
  const getInitials = (name) =>
    name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();

  const handleMediaToggle = (e, type) => {
    e.stopPropagation();
    // Toggle both database state and real media
    onToggleMedia(participant, type);
    onToggleRealMedia(participant, type);
  };

  const handleShowDetails = (e) => {
    e.stopPropagation();
    onShowDetails(participant);
  };

  const isRealMicActive = realMediaStates[participant.id]?.mic || false;
  const isRealCameraActive = realMediaStates[participant.id]?.camera || false;

  return (
    <div className={`participant-card ${view === 'list' ? 'list-view' : ''}`}>
      <div className="participant-header">
        <div className="avatar">
          {getInitials(participant.name)}
        </div>
        
        <div className="participant-basic-info">
          <h3 className="participant-name">
            <div className="participant-name-with-audio">
              <span>{participant.name}</span>
              {isRealMicActive && (
                <div className="name-audio-visualizer">
                  {[...Array(4)].map((_, index) => (
                    <div
                      key={index}
                      className={`name-audio-bar ${isRealMicActive ? 'active' : ''}`}
                      style={{
                        animationDelay: `${index * 0.1}s`,
                        height: isRealMicActive ? `${Math.random() * 12 + 4}px` : '4px'
                      }}
                    />
                  ))}
                </div>
              )}
            </div>
          </h3>
          <p className="participant-role">{participant.role}</p>
          
          <div className="participant-status">
            <div className={`status-indicator ${participant.online ? '' : 'offline'}`}></div>
            <span>{participant.online ? "Online" : "Offline"}</span>
          </div>
        </div>
        
        {view === 'list' && (
          <div className="participant-controls">
            <div className="control-with-visualizer">
              <button
                className={`control-button ${participant.mic_on ? 'active' : 'muted'}`}
                onClick={(e) => handleMediaToggle(e, 'mic')}
                aria-label={participant.mic_on ? 'Mute' : 'Unmute'}
                data-testid="mic-button"
              >
                {participant.mic_on ? <Mic size={16} /> : <MicOff size={16} />}
              </button>
              <AudioLevelVisualizer 
                isActive={isRealMicActive} 
                participantId={participant.id} 
              />
            </div>
            
            <button
              className={`control-button ${participant.camera_on ? 'active' : 'muted'}`}
              onClick={(e) => handleMediaToggle(e, 'camera')}
              aria-label={participant.camera_on ? 'Turn camera off' : 'Turn camera on'}
              data-testid="camera-button"
            >
              {participant.camera_on ? <Video size={16} /> : <VideoOff size={16} />}
            </button>
          </div>
        )}
        
        <button 
          className="details-button"
          onClick={handleShowDetails}
          aria-label="Show more details"
        >
          <Info size={18} />
        </button>
      </div>

      {view === "grid" && (
        <div className="video-preview" id={`video-${participant.id}`}>
          <Video size={20} />
          <span>Video Preview</span>
        </div>
      )}

      {view === "grid" && (
        <div className="participant-controls">
          <div className="control-with-visualizer">
            <button
              className={`control-button ${participant.mic_on ? 'active' : 'muted'}`}
              onClick={(e) => handleMediaToggle(e, 'mic')}
              aria-label={participant.mic_on ? 'Mute' : 'Unmute'}
              data-testid="mic-button"
            >
              {participant.mic_on ? <Mic size={16} /> : <MicOff size={16} />}
            </button>
            <AudioLevelVisualizer 
              isActive={isRealMicActive} 
              participantId={participant.id} 
            />
          </div>
          
          <button
            className={`control-button ${participant.camera_on ? 'active' : 'muted'}`}
            onClick={(e) => handleMediaToggle(e, 'camera')}
            aria-label={participant.camera_on ? 'Turn camera off' : 'Turn camera on'}
            data-testid="camera-button"
          >
            {participant.camera_on ? <Video size={16} /> : <VideoOff size={16} />}
          </button>
        </div>
      )}
    </div>
  );
}

// Modal Component
function ParticipantModal({ participant, onClose, onToggleMedia, onToggleRealMedia, realMediaStates }) {
  const videoRef = useRef(null);
  
  if (!participant) return null;

  const handleMediaToggle = (type) => {
    // Toggle both database state and real media
    onToggleMedia(participant, type);
    onToggleRealMedia(participant, type);
  };

  const isRealCameraActive = realMediaStates[participant.id]?.camera || false;
  const isRealMicActive = realMediaStates[participant.id]?.mic || false;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          <X size={16} />
        </button>

        <div className="modal-header">
          <div className="avatar large">
            {participant.name.split(" ").map(n => n[0]).join("").toUpperCase()}
          </div>
          <div className="modal-title-info">
            <h2>{participant.name}</h2>
            <p className="role-badge">{participant.role}</p>
          </div>
        </div>

        <div className="modal-video" id={`modal-video-${participant.id}`}>
          <video 
            ref={videoRef}
            autoPlay 
            muted
            style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '8px' }}
          />
          <div className="video-overlay">
            <Video size={32} />
            <span>{isRealCameraActive ? "Live Camera" : "Video Preview"}</span>
          </div>
        </div>

        <div className="modal-controls">
          <button
            className={`control-button ${participant.mic_on ? 'active' : 'muted'}`}
            onClick={() => handleMediaToggle('mic')}
          >
            {participant.mic_on ? <Mic size={16} /> : <MicOff size={16} />}
            <span>{participant.mic_on ? "Mute" : "Unmute"}</span>
          </button>
          
          <button
            className={`control-button ${participant.camera_on ? 'active' : 'muted'}`}
            onClick={() => handleMediaToggle('camera')}
          >
            {participant.camera_on ? <Video size={16} /> : <VideoOff size={16} />}
            <span>{participant.camera_on ? "Turn Off" : "Turn On"}</span>
          </button>
          
          <div className="audio-visualizer-container">
            <AudioLevelVisualizer 
              isActive={isRealMicActive} 
              participantId={participant.id} 
            />
          </div>
        </div>

        <div className="modal-info">
          <div className="info-grid">
            <div className="info-item">
              <strong>Email:</strong>
              <span>{participant.email}</span>
            </div>
            <div className="info-item">
              <strong>Status:</strong>
              <span className={participant.online ? "status-online" : "status-offline"}>
                {participant.online ? "🟢 Online" : "⚪ Offline"}
              </span>
            </div>
            <div className="info-item">
              <strong>Microphone:</strong>
              <span>{participant.mic_on ? "🎤 On" : "🔇 Muted"}</span>
            </div>
            <div className="info-item">
              <strong>Camera:</strong>
              <span>{participant.camera_on ? "📹 On" : "📵 Off"}</span>
            </div>
            <div className="info-item">
              <strong>Joined:</strong>
              <div className="timestamp-container">
                <span className="timestamp">
                  {participant.created_at ? new Date(participant.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  }) : 'Unknown'}
                </span>
                {participant.created_at && <TimeAgo timestamp={participant.created_at} />}
              </div>
            </div>
            <div className="info-item">
              <strong>Last Updated:</strong>
              <div className="timestamp-container">
                <span className="timestamp">
                  {participant.updated_at ? new Date(participant.updated_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  }) : 'Unknown'}
                </span>
                {participant.updated_at && <TimeAgo timestamp={participant.updated_at} />}
              </div>
            </div>
          </div>
          
          {participant.about_me && (
            <div className="about-section">
              <strong>About:</strong>
              <p>{participant.about_me}</p>
            </div>
          )}

          {participant.resume_url && (
            <a 
              href={participant.resume_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="resume-link"
            >
              <ExternalLink size={16} />
              View Resume
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function App() {
  const [participants, setParticipants] = useState([]);
  const [search, setSearch] = useState(localStorage.getItem('search') || "");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState(parseInt(localStorage.getItem('page')) || 0);
  const [view, setView] = useState(localStorage.getItem('view') || "grid");
  const [theme, setTheme] = useState(
    localStorage.getItem('theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  );
  
  // Real media states - persist in sessionStorage for page refresh
  const [realMediaStates, setRealMediaStates] = useState(() => {
    try {
      const saved = sessionStorage.getItem('realMediaStates');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  const [mediaStreams, setMediaStreams] = useState({});

  // UX states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const LIMIT = 6;

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Persist view mode
  useEffect(() => {
    localStorage.setItem('view', view);
  }, [view]);

  // Persist search query
  useEffect(() => {
    localStorage.setItem('search', search);
  }, [search]);

  // Persist page number
  useEffect(() => {
    localStorage.setItem('page', page.toString());
  }, [page]);

  // Persist real media states
  useEffect(() => {
    sessionStorage.setItem('realMediaStates', JSON.stringify(realMediaStates));
  }, [realMediaStates]);

  // Restore media streams on page refresh
  useEffect(() => {
    const restoreMediaStreams = async () => {
      for (const [participantId, states] of Object.entries(realMediaStates)) {
        if (states.camera || states.mic) {
          try {
            const stream = await navigator.mediaDevices.getUserMedia({
              video: states.camera,
              audio: states.mic
            });
            
            setMediaStreams(prev => ({ ...prev, [participantId]: stream }));
            
            if (states.camera) {
              // Restore video elements
              const videoElements = [
                document.getElementById(`video-${participantId}`),
                document.getElementById(`modal-video-${participantId}`)
              ];
              
              videoElements.forEach(element => {
                if (element) {
                  let video = element.querySelector('video');
                  if (!video) {
                    video = document.createElement('video');
                    video.style.cssText = 'width: 100%; height: 100%; object-fit: cover; border-radius: 8px; position: absolute; top: 0; left: 0;';
                    video.autoplay = true;
                    video.muted = true;
                    element.appendChild(video);
                  }
                  video.srcObject = stream;
                }
              });
            }
          } catch (error) {
            // Remove from realMediaStates if we can't access media
            setRealMediaStates(prev => {
              const newStates = { ...prev };
              delete newStates[participantId];
              return newStates;
            });
          }
        }
      }
    };

    if (Object.keys(realMediaStates).length > 0) {
      restoreMediaStreams();
    }
  }, []); // Run only on mount

  // Toggle database media (mic/camera)
  const toggleMedia = async (participant, type) => {
    try {
      let updatedParticipant;

      if (type === "mic") {
        updatedParticipant = await updateParticipantMicrophone(participant.id, !participant.mic_on);
      } else if (type === "camera") {
        updatedParticipant = await updateParticipantCamera(participant.id, !participant.camera_on);
      }

      setParticipants((prev) =>
        prev.map((p) => (p.id === participant.id ? updatedParticipant : p))
      );

      if (selected && selected.id === participant.id) {
        setSelected(updatedParticipant);
      }
    } catch (err) {
      console.error('Failed to update media state:', err);
      setError(err.message || "Failed to update media state");
      setTimeout(() => setError(null), 3000);
    }
  };
  
  // Toggle real media (webcam/microphone)
  const toggleRealMedia = async (participant, type) => {
    try {
      const participantId = participant.id;
      const currentStates = realMediaStates[participantId] || { mic: false, camera: false };
      
      if (type === 'camera') {
        if (currentStates.camera) {
          // Stop camera
          const stream = mediaStreams[participantId];
          if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setMediaStreams(prev => {
              const newStreams = { ...prev };
              delete newStreams[participantId];
              return newStreams;
            });
          }
          
          // Clear video elements
          const videoElements = [
            document.getElementById(`video-${participantId}`),
            document.getElementById(`modal-video-${participantId}`)
          ];
          
          videoElements.forEach(element => {
            if (element) {
              const video = element.querySelector('video');
              if (video) video.remove();
            }
          });
          
          setRealMediaStates(prev => ({
            ...prev,
            [participantId]: { ...currentStates, camera: false }
          }));
        } else {
          // Start camera
          const stream = await navigator.mediaDevices.getUserMedia({ 
            video: true, 
            audio: currentStates.mic 
          });
          
          setMediaStreams(prev => ({ ...prev, [participantId]: stream }));
          
          // Update video elements
          const videoElements = [
            document.getElementById(`video-${participantId}`),
            document.getElementById(`modal-video-${participantId}`)
          ];
          
          videoElements.forEach(element => {
            if (element) {
              let video = element.querySelector('video');
              if (!video) {
                video = document.createElement('video');
                video.style.cssText = 'width: 100%; height: 100%; object-fit: cover; border-radius: 8px; position: absolute; top: 0; left: 0;';
                video.autoplay = true;
                video.muted = true;
                element.appendChild(video);
              }
              video.srcObject = stream;
            }
          });
          
          setRealMediaStates(prev => ({
            ...prev,
            [participantId]: { ...currentStates, camera: true }
          }));
        }
      }
      
      if (type === 'mic') {
        if (currentStates.mic) {
          // Stop microphone
          const stream = mediaStreams[participantId];
          if (stream) {
            stream.getAudioTracks().forEach(track => track.stop());
          }
          
          setRealMediaStates(prev => ({
            ...prev,
            [participantId]: { ...currentStates, mic: false }
          }));
        } else {
          // Start microphone
          try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
              audio: true, 
              video: currentStates.camera 
            });
            
            setMediaStreams(prev => ({ ...prev, [participantId]: stream }));
            setRealMediaStates(prev => ({
              ...prev,
              [participantId]: { ...currentStates, mic: true }
            }));
          } catch (error) {
            setError("Failed to access microphone");
            setTimeout(() => setError(null), 3000);
          }
        }
      }
    } catch (error) {
      setError(`Failed to access ${type === 'camera' ? 'camera' : 'microphone'}`);
      setTimeout(() => setError(null), 3000);
    }
  };
  
  // Show participant details
  const showParticipantDetails = (participant) => {
    setSelected(participant);
  };

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(0);
    }, 400);

    return () => clearTimeout(timer);
  }, [search]);

  // Fetch participants
  useEffect(() => {
    const loadParticipants = async () => {
      setLoading(true);
      setError(null);

      try {
        const participantsData = await fetchParticipants(debouncedSearch, page + 1, LIMIT);
        setParticipants(participantsData);
      } catch (err) {
        console.error('Failed to fetch participants:', err);
        setError(err.message || "Failed to load participants");
      } finally {
        setLoading(false);
      }
    };

    loadParticipants();
  }, [debouncedSearch, page]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && selected) {
        setSelected(null);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selected]);

  return (
    <div className="app-container">
      <header className="header">
        <h1>AiRoHire Participants</h1>
        <ThemeToggle theme={theme} setTheme={setTheme} />
      </header>

      <div className="controls">
        {/* View Toggle */}
        <div className="view-toggle">
          <button
            className={view === "grid" ? "active" : ""}
            onClick={() => setView("grid")}
            aria-label="Grid view"
          >
            <Grid3X3 size={16} />
            <span>Grid</span>
          </button>
          <button
            className={view === "list" ? "active" : ""}
            onClick={() => setView("list")}
            aria-label="List view"
          >
            <List size={16} />
            <span>List</span>
          </button>
        </div>

        {/* Search */}
        <div className="search-container">
          <Search className="search-icon" size={18} />
          <input
            type="text"
            placeholder="Search participants..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
            aria-label="Search participants"
          />
        </div>
      </div>

      {/* Content */}
      {loading && <LoadingSpinner />}
      
      {error && <ErrorMessage error={error} />}

      {!loading && !error && participants.length === 0 && (
        <div className="error">
          <AlertCircle size={24} />
          <h3>No participants found</h3>
          <p>Try adjusting your search or check back later.</p>
        </div>
      )}

      {!loading && !error && participants.length > 0 && (
        <>
          <div className={view === "grid" ? "participants-grid" : "participants-list"}>
            {participants.map((participant) => (
              <ParticipantCard
                key={participant.id}
                participant={participant}
                view={view}
                onShowDetails={showParticipantDetails}
                onToggleMedia={toggleMedia}
                onToggleRealMedia={toggleRealMedia}
                realMediaStates={realMediaStates}
              />
            ))}
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button 
              disabled={page === 0} 
              onClick={() => setPage(page - 1)}
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
              Previous
            </button>
            <button 
              onClick={() => setPage(page + 1)}
              disabled={participants.length < LIMIT}
              aria-label="Next page"
            >
              Next
              <ChevronRight size={16} />
            </button>
          </div>
        </>
      )}

      {/* Modal */}
      <ParticipantModal
        participant={selected}
        onClose={() => setSelected(null)}
        onToggleMedia={toggleMedia}
        onToggleRealMedia={toggleRealMedia}
        realMediaStates={realMediaStates}
      />
    </div>
  );
}

export default App;
