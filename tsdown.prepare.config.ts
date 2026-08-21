import { defineConfig } from 'tsdown'

/** Build the Git-installed runtime directly from this repository's TypeScript source. */
export default defineConfig({
  entry: {
    index: 'src/index.ts',
    invariant: 'src/invariant.ts',
  },
  outDir: 'lib',
  format: ['esm'],
  platform: 'node',
  target: 'es2024',
  fixedExtension: false,
  dts: false,
  clean: true,
})
