import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000, // 10 second timeout
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
    });
    return Promise.reject(error);
  }
);

// API helper functions with error handling
export const fetchParticipants = async (search = "", page = 1, limit = 6) => {
  try {
    const offset = (page - 1) * limit;
    const response = await api.get(`/participants`, {
      params: { search, limit, offset }
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch participants: ${error.response?.data?.detail || error.message}`);
  }
};

export const fetchParticipantCount = async (search = "") => {
  try {
    const response = await api.get(`/participants/count`, {
      params: { search }
    });
    return response.data.total;
  } catch (error) {
    throw new Error(`Failed to fetch participant count: ${error.response?.data?.detail || error.message}`);
  }
};

export const fetchParticipant = async (id) => {
  try {
    const response = await api.get(`/participants/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(`Failed to fetch participant: ${error.response?.data?.detail || error.message}`);
  }
};

export const updateParticipantMedia = async (id, micOn, cameraOn) => {
  try {
    const response = await api.patch(`/participants/${id}/media`, {
      mic_on: micOn,
      camera_on: cameraOn
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to update media: ${error.response?.data?.detail || error.message}`);
  }
};

export const updateParticipantMicrophone = async (id, micOn) => {
  try {
    const response = await api.patch(`/participants/${id}/microphone`, {
      mic_on: micOn
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to update microphone: ${error.response?.data?.detail || error.message}`);
  }
};

export const updateParticipantCamera = async (id, cameraOn) => {
  try {
    const response = await api.patch(`/participants/${id}/camera`, {
      camera_on: cameraOn
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to update camera: ${error.response?.data?.detail || error.message}`);
  }
};

export const updateParticipantStatus = async (id, online) => {
  try {
    const response = await api.patch(`/participants/${id}/status`, {
      online: online
    });
    return response.data;
  } catch (error) {
    throw new Error(`Failed to update status: ${error.response?.data?.detail || error.message}`);
  }
};
