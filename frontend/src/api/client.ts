import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  timeout: 20000
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("finflow_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  config.headers["x-device-id"] = localStorage.getItem("finflow_device") ?? crypto.randomUUID();
  localStorage.setItem("finflow_device", String(config.headers["x-device-id"]));
  return config;
});

