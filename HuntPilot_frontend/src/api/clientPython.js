import axios from "axios";

const PYTHON_API_BASE_URL = (
  import.meta.env.VITE_PYTHON_API_URL ||
  "http://localhost:8000"
).replace(/\/+$/, "");

const pythonApi = axios.create({
  baseURL: PYTHON_API_BASE_URL,
  timeout: 20000, // NLP may take slightly longer
});

export default pythonApi;