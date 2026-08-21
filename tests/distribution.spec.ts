import { readFile } from 'node:fs/promises'
import { describe, expect, it } from 'vitest'

interface PackageManifest {
  scripts: Record<string, string>
  files: string[]
  peerDependencies: Record<string, string>
  devDependencies: Record<string, string>
}

describe('standalone Git distribution', () => {
  it('owns a source build and contains no monorepo dependency specifiers', async () => {
    const raw = await readFile(new URL('../package.json', import.meta.url), 'utf8')
    const manifest = JSON.parse(raw) as PackageManifest
    expect(manifest.scripts.prepare).toBe('pnpm run build')
    expect(manifest.scripts.build).toContain('tsdown.prepare.config.ts')
    expect(manifest.scripts.build).toContain('tsconfig.build.json')
    expect(manifest.files).toContain('bin/doctor.js')
    expect(manifest.files).toContain('assets')
    expect(raw).not.toContain('workspace:')
    expect(Object.values(manifest.peerDependencies).every(value => value !== '*')).toBe(true)
    expect(manifest.devDependencies.tsdown).toMatch(/^\d+\.\d+\.\d+$/)
  })

  it('documents pnpm canonical GitHub build permission separately from the Git spec', async () => {
    const readme = await readFile(new URL('../README.md', import.meta.url), 'utf8')
    expect(readme).toContain(
      "--allow-build='@deepseek-ai/dsh-experimental-health-ppt-master@https://codeload.github.com/Alberssssss/dsh-health-ppt-master/tar.gz/<commit>'",
    )
    expect(readme).toContain(
      "'git+https://github.com/Alberssssss/dsh-health-ppt-master.git#<commit>'",
    )
    expect(readme).not.toContain(
      "--allow-build='@deepseek-ai/dsh-experimental-health-ppt-master@git+https://",
    )
  })
})
