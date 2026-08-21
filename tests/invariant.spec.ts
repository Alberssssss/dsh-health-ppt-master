import { Context } from '@deepseek-ai/cordis'
import { createUserMessage } from '@deepseek-ai/dsh-llm'
import SessionStore, { SessionId } from '@deepseek-ai/dsh-session'
import InvariantRegistry, { InvariantError } from '@deepseek-ai/dsh-invariants'
import { describe, expect, it } from 'vitest'
import * as HealthPptMasterInvariant from '../src/invariant.ts'
import { ROUTER_HINT, ROUTER_SOURCE } from '../src/router.ts'

function routerMessage(text = ROUTER_HINT, form: 'instructions' | 'catalog' = 'instructions') {
  return createUserMessage({
    content: [{ type: 'text', text }],
    source: { kind: 'plugin', plugin: ROUTER_SOURCE, form },
  })
}

describe('health-ppt-master invariant companion', () => {
  it('accepts exact router messages and validates seeded sessions on creation', async () => {
    const ctx = new Context()
    await ctx.plugin(SessionStore)
    await ctx.plugin(InvariantRegistry)
    await ctx.plugin(HealthPptMasterInvariant)
    const session = ctx.sessions.create(SessionId('health-ppt-router-valid'))
    expect(() => session.append('user/message', routerMessage(), { surfaceOp: 'append' })).not.toThrow()
    expect(() => ctx.sessions.create(SessionId('health-ppt-router-valid-seed'), {
      seed: [...session.events],
    })).not.toThrow()
    expect(() => session.append('user/message', createUserMessage({
      content: [{ type: 'text', text: 'unrelated' }],
      source: { kind: 'plugin', plugin: 'other' },
    }), { surfaceOp: 'append' })).not.toThrow()
  })

  it('rejects altered source metadata and altered router text', async () => {
    const ctx = new Context()
    await ctx.plugin(SessionStore)
    await ctx.plugin(InvariantRegistry)
    await ctx.plugin(HealthPptMasterInvariant)
    const session = ctx.sessions.create(SessionId('health-ppt-router-invalid'))
    expect(() => session.append('user/message', routerMessage(ROUTER_HINT, 'catalog'), {
      surfaceOp: 'append',
    })).toThrow(new InvariantError(
      '@deepseek-ai/dsh-experimental-health-ppt-master',
      'router messages must retain only the package instructions source',
    ))
    expect(() => session.append('user/message', routerMessage('altered'), {
      surfaceOp: 'append',
    })).toThrow(/exact packaged soft-route instructions/)
    expect(() => session.append('user/message', createUserMessage({
      content: [],
      source: { kind: 'plugin', plugin: ROUTER_SOURCE, form: 'instructions' },
    }), { surfaceOp: 'append' })).toThrow(/exact packaged soft-route instructions/)
  })

  it('rejects a malformed package-owned message already present at installation', async () => {
    const ctx = new Context()
    await ctx.plugin(SessionStore)
    await ctx.plugin(InvariantRegistry)
    const session = ctx.sessions.create(SessionId('health-ppt-router-preexisting'))
    session.append('user/message', routerMessage('altered'), { surfaceOp: 'append' })
    await expect(ctx.plugin(HealthPptMasterInvariant)).rejects.toThrow(
      /exact packaged soft-route instructions/,
    )
  })
})
