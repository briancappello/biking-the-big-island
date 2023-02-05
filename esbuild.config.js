import esbuildServe from "esbuild-serve";

esbuildServe(
    // esbuild options
  {
    logLevel: "info",
    entryPoints: ["src/index.js"],
    bundle: true,
    outdir: "public",
    loader: {".png": "file"},
    assetNames: "images/[name]"
  },
  // serve options
  {
    port: 7000,
    root: 'public',
  },
);
