import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // API proxy: src/app/api/v1/[...path]/route.ts → BACKEND_URL (server-side only)
  // Browser never touches the backend URL directly — no CORS, no port issues
};

export default nextConfig;
