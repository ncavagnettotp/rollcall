// Bundle the installed HeroUI component into the standalone file:// design preview.
const path = require('node:path');
const vite = require.resolve('vite', {paths:[path.resolve('frontend')]});
const esbuild = require(require.resolve('esbuild', {paths:[vite]}));
esbuild.buildSync({
  entryPoints:['docs/rollcall/preview-tabs.jsx'],
  outfile:'docs/rollcall/assets/preview-tabs.js',
  bundle:true, format:'iife', platform:'browser', minify:true,
  define:{'process.env.NODE_ENV':'"production"'},
  nodePaths:[path.resolve('frontend/node_modules')],
  logLevel:'warning',
});
console.log('Bundled real HeroUI Tabs from installed project dependencies.');
