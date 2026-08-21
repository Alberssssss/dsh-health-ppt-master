import { mkdtemp, mkdir, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const PREFLIGHT = fileURLToPath(new URL(
  '../assets/health-ppt-master/scripts/dsh_preflight.py',
  import.meta.url,
))
const VISUAL_REVIEW = fileURLToPath(new URL(
  '../assets/health-ppt-master/scripts/visual_review.py',
  import.meta.url,
))
const DOCTOR = fileURLToPath(new URL('../bin/doctor.js', import.meta.url))

function findPython(): string | undefined {
  for (const command of process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python']) {
    const result = spawnSync(command, ['-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' })
    if (result.status === 0) return result.stdout.trim()
  }
  return undefined
}

const python = findPython()

function runPreflight(args: string[], env: NodeJS.ProcessEnv = process.env) {
  if (!python) throw new Error('Python is unavailable')
  return spawnSync(python, [PREFLIGHT, ...args], { encoding: 'utf8', env })
}

describe.skipIf(!python)('DSH runtime preflight', () => {
  it('reports every capability without making optional groups fatal', () => {
    const result = runPreflight(['--json'])
    expect(result.status).toBe(0)
    const report = JSON.parse(result.stdout) as Record<string, unknown>
    expect(report.schema).toBe('health-ppt-master-preflight.v1')
    expect(report.required).toEqual([])
    expect(report.ok).toBe(true)
    expect(report.resources).toMatchObject({
      coreRequirements: expect.stringMatching(/requirements-core\.txt$/),
    })
    expect(Object.keys(report.groups as object).sort()).toEqual([
      'audio', 'core', 'document-parser', 'ingestion', 'office', 'preview', 'workspace',
    ])
  })

  it('fails a required unavailable capability and never emits credential values', () => {
    const sentinel = 'must-not-appear-in-preflight-output'
    const result = runPreflight(['--json', '--require', 'office'], {
      ...process.env,
      GEMINI_API_KEY: sentinel,
      PATH: '',
    })
    expect(result.status).toBe(2)
    expect(result.stdout).not.toContain(sentinel)
    const report = JSON.parse(result.stdout) as { ok: boolean }
    expect(report.ok).toBe(false)
  })

  it('validates explicit workspace and document-parser locations', async () => {
    const root = await mkdtemp(join(tmpdir(), 'health-ppt-preflight-'))
    const parser = join(root, 'document-parser')
    await mkdir(join(parser, 'scripts'), { recursive: true })
    await writeFile(join(parser, 'scripts', 'pdf_dispatcher.py'), '')
    const result = runPreflight([
      '--json',
      '--require', 'workspace',
      '--require', 'document-parser',
      '--workspace', root,
      '--document-parser-dir', parser,
    ])
    expect(result.status).toBe(0)
    const report = JSON.parse(result.stdout) as { ok: boolean }
    expect(report.ok).toBe(true)
  })

  it('exposes the same report through the installed package bin', () => {
    const result = spawnSync(process.execPath, [DOCTOR, '--json'], {
      encoding: 'utf8',
      env: { ...process.env, DSH_HEALTH_PPT_PYTHON: python },
    })
    expect(result.status).toBe(0)
    expect(JSON.parse(result.stdout)).toMatchObject({
      schema: 'health-ppt-master-preflight.v1',
      ok: true,
    })
  })

  it('percent-encodes non-ASCII slide names before the preview probe', () => {
    if (!python) throw new Error('Python is unavailable')
    const script = [
      'import importlib.util, sys',
      'spec = importlib.util.spec_from_file_location("visual_review", sys.argv[1])',
      'module = importlib.util.module_from_spec(spec)',
      'spec.loader.exec_module(module)',
      'class Response:',
      '    def __enter__(self): return self',
      '    def __exit__(self, *_args): return False',
      '    def read(self): return b\'{"content":"ok"}\'',
      'def open_url(request, timeout):',
      '    print(request.full_url)',
      '    return Response()',
      'module.urllib.request.urlopen = open_url',
      'print(module.fetch_slide_text("http://localhost:5050", "01_封面?#.svg"))',
    ].join('\n')
    const result = spawnSync(python, ['-c', script, VISUAL_REVIEW], {
      encoding: 'utf8',
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    })
    expect(result.status).toBe(0)
    expect(result.stdout).toContain('/api/slide/01_%E5%B0%81%E9%9D%A2%3F%23.svg')
    expect(result.stdout.trim().endsWith('\n2')).toBe(true)
  })
})
