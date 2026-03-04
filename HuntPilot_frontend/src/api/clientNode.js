import axios from "axios";

const NODE_API_BASE_URL = (
  import.meta.env.VITE_NODE_API_URL ||
  "http://localhost:5000"
).replace(/\/+$/, "");

const nodeApi = axios.create({
  baseURL: NODE_API_BASE_URL,
  timeout: 15000,
});

nodeApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token && !config.headers?.Authorization) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

export default nodeApi;