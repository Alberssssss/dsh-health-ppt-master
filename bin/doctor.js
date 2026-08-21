#!/usr/bin/env node

import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const script = fileURLToPath(new URL(
  '../assets/health-ppt-master/scripts/dsh_preflight.py',
  import.meta.url,
))
const configuredPython = process.env.DSH_HEALTH_PPT_PYTHON?.trim()
const candidates = configuredPython
  ? [[configuredPython, []]]
  : process.platform === 'win32'
    ? [['py', ['-3']], ['python', []]]
    : [['python3', []], ['python', []]]

for (const [command, prefix] of candidates) {
  const result = spawnSync(command, [...prefix, script, ...process.argv.slice(2)], {
    stdio: 'inherit',
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  })
  if (result.error && 'code' in result.error && result.error.code === 'ENOENT') continue
  if (result.error) {
    console.error(`health-ppt-master doctor failed to start ${command}: ${result.error.message}`)
    process.exitCode = 1
  } else {
    process.exitCode = result.status ?? 1
  }
  process.exit()
}

console.error(
  'health-ppt-master doctor requires Python 3; set DSH_HEALTH_PPT_PYTHON to its executable path.',
)
process.exitCode = 2
