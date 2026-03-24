import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/Matrix-Vector-Analog/", // This matches the actual repo name
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});

