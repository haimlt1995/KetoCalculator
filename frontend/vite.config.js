import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,                 // allow external access
    allowedHosts: ["all", "d2xlvapgg8htpu.cloudfront.net"],         // fixes CloudFront "Blocked request"
    proxy: {
      "/api": {
        target: "http://backend:8080", // backend service name on docker network
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
