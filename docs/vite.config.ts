import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/Matrix-Vector-Multiplier/", // Replace with your EXACT repository name
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});

