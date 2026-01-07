import { useEffect, useState } from "react";
import { api } from "./api";

function App() {
  const [participants, setParticipants] = useState([]);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState(0);

  // UX states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const LIMIT = 6;

  const getInitials = (name) =>
    name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();

  // 🎤📷 Toggle mic / camera
  const toggleMedia = async (participant, type) => {
    try {
      let endpoint = "";
      let payload = {};

      if (type === "mic") {
        endpoint = `/participants/${participant.id}/microphone`;
        payload = { mic_on: !participant.mic_on };
      }

      if (type === "camera") {
        endpoint = `/participants/${participant.id}/camera`;
        payload = { camera_on: !participant.camera_on };
      }

      const res = await api.patch(endpoint, payload);

      setParticipants((prev) =>
        prev.map((p) => (p.id === participant.id ? res.data : p))
      );

      if (selected && selected.id === participant.id) {
        setSelected(res.data);
      }
    } catch {
      setError("Failed to update media state");
    }
  };

  // ⏳ Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(0);
    }, 400);

    return () => clearTimeout(timer);
  }, [search]);

  // 🌐 Fetch participants
  useEffect(() => {
    const fetchParticipants = async () => {
      setLoading(true);
      setError(null);

      try {
        const res = await api.get("/participants", {
          params: {
            search: debouncedSearch,
            limit: LIMIT,
            offset: page * LIMIT,
          },
        });

        setParticipants(res.data);
      } catch {
        setError("Failed to load participants");
      } finally {
        setLoading(false);
      }
    };

    fetchParticipants();
  }, [debouncedSearch, page]);

  /* ================= UX STATES ================= */

  if (loading) {
    return <h2 style={{ padding: "20px" }}>Loading participants...</h2>;
  }

  if (error) {
    return (
      <div style={{ padding: "20px", color: "red" }}>
        <h3>{error}</h3>
      </div>
    );
  }

  if (!loading && participants.length === 0) {
    return (
      <div style={{ padding: "20px" }}>
        <h3>No participants found</h3>
        <p>Try adjusting your search.</p>
      </div>
    );
  }

  /* ================= MAIN UI ================= */

  return (
    <div style={{ padding: "20px" }}>
      <h1>Video Call Participants</h1>

      {/* 🔍 Search */}
      <input
        type="text"
        placeholder="Search participants..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ padding: "8px", marginBottom: "20px", width: "250px" }}
      />

      {/* 🧱 Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "15px",
        }}
      >
        {participants.map((p) => (
          <div
            key={p.id}
            onClick={() => setSelected(p)}
            style={{
              border: "1px solid #ccc",
              padding: "12px",
              cursor: "pointer",
            }}
          >
            {/* Avatar */}
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: "#555",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: "bold",
                marginBottom: "8px",
              }}
            >
              {getInitials(p.name)}
            </div>

            <strong>{p.name}</strong> ({p.role})

            {/* Online status */}
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "50%",
                  background: p.online ? "limegreen" : "gray",
                }}
              />
              <span style={{ fontSize: "12px" }}>
                {p.online ? "Online" : "Offline"}
              </span>
            </div>

            {/* Video preview */}
            <div
              style={{
                marginTop: "8px",
                height: "100px",
                background: "#000",
                color: "#aaa",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "12px",
              }}
            >
              Video Preview
            </div>

            {/* Controls */}
            <div style={{ marginTop: "10px" }}>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleMedia(p, "mic");
                }}
              >
                🎤 {p.mic_on ? "Mute" : "Unmute"}
              </button>

              <button
                style={{ marginLeft: "10px" }}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleMedia(p, "camera");
                }}
              >
                📷 {p.camera_on ? "Turn Off" : "Turn On"}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div style={{ marginTop: "20px" }}>
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>
          Prev
        </button>
        <button style={{ marginLeft: "10px" }} onClick={() => setPage(page + 1)}>
          Next
        </button>
      </div>

      {/* 🪟 Detail Modal */}
      {selected && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
          onClick={() => setSelected(null)}
        >
          <div
            style={{ background: "#222", padding: "20px", width: "320px" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                height: "180px",
                background: "#000",
                color: "#aaa",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "12px",
              }}
            >
              Large Video Preview
            </div>

            <div style={{ marginBottom: "12px" }}>
              <button onClick={() => toggleMedia(selected, "mic")}>
                🎤 {selected.mic_on ? "Mute" : "Unmute"}
              </button>
              <button
                style={{ marginLeft: "10px" }}
                onClick={() => toggleMedia(selected, "camera")}
              >
                📷 {selected.camera_on ? "Turn Off" : "Turn On"}
              </button>
            </div>

            <h3>{selected.name}</h3>
            <p>Email: {selected.email}</p>
            <p>Role: {selected.role}</p>

            <button onClick={() => setSelected(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
