import esbuildServe from "esbuild-serve";

esbuildServe(
    // esbuild options
  {
    logLevel: "info",
    entryPoints: ["src/index.js"],
    bundle: true,
    outfile: "public/index.js",
    loader: {".png": "file"},
  },
  // serve options
  {
    port: 7000,
    root: 'public',
  },
);
