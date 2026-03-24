import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/Matrix-Vector-Multiplier/", // Must match GitHub repo name for Pages
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});

