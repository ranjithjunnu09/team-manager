import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

const savedToken = localStorage.getItem("token");
if (savedToken) {
  API.defaults.headers.common["Authorization"] = `Bearer ${savedToken}`;
}

export default API;