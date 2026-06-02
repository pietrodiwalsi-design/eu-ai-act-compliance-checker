import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // API proxy handled by src/app/api/v1/[...path]/route.ts
  // No rewrites needed — avoids Next.js proxy timeout on long LLM calls
};

export default nextConfig;
