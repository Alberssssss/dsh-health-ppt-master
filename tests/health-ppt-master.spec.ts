import { access, readdir } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { Context } from '@deepseek-ai/cordis'
import Loader from '@deepseek-ai/cordis-plugin-loader'
import AgentRegistry, { agentEvents, Inbox, type Agent, type PreStepDecision } from '@deepseek-ai/dsh-agent'
import { createUserMessage, type UserMessage } from '@deepseek-ai/dsh-llm'
import SessionStore, { SessionId } from '@deepseek-ai/dsh-session'
import SkillRegistry from '@deepseek-ai/dsh-skill'
import { describe, expect, it } from 'vitest'
import * as BuiltHealthPptMaster from '@deepseek-ai/dsh-experimental-health-ppt-master'
import * as HealthPptMaster from '../src/index.ts'
import {
  matchesHealthPptMaster,
  ROUTER_HINT,
  ROUTER_SOURCE,
} from '../src/router.ts'

async function setup() {
  const ctx = new Context()
  await ctx.plugin(SessionStore)
  await ctx.plugin(AgentRegistry)
  await ctx.plugin(SkillRegistry)
  const fiber = await ctx.plugin(HealthPptMaster)
  const id = SessionId('health-ppt-master-test')
  const session = ctx.sessions.create(id, { meta: { cwd: process.cwd() } })
  const agent: Agent = {
    ctx: new Context(),
    id,
    options: {},
    session,
    inbox: new Inbox(session, { inserted: () => {}, discarded: () => {}, claimed: () => {} }),
    status: 'idle',
    send: () => {},
    followup: () => {},
    steer: () => {},
    inject: () => {},
    cancel: () => {},
    runMaintenance: job => job(new AbortController().signal),
    whenIdle: () => Promise.resolve(),
  }
  return { ctx, fiber, agent }
}

function userMessage(text: string): UserMessage {
  return createUserMessage({ content: [{ type: 'text', text }], source: { kind: 'user' } })
}

async function prepare(
  ctx: Context,
  agent: Agent,
  messages: UserMessage[],
  terminal: () => Promise<PreStepDecision> = () => Promise.resolve({ kind: 'enter', messages }),
  signal = new AbortController().signal,
): Promise<PreStepDecision> {
  return await agentEvents(ctx, agent).waterfall(
    'agent/pre-step',
    { messages, turn: 1, step: 1, signal },
    terminal,
  )
}

describe('experimental health-ppt-master bundle plugin', () => {
  it('registers and disposes the bundled provider and router through one fiber', async () => {
    const { ctx, fiber, agent } = await setup()
    const resourcePath = fileURLToPath(new URL('../assets/health-ppt-master/', import.meta.url))

    expect(await ctx.skills.list()).toEqual([{
      name: 'health-ppt-master',
      description: '生成或改造医疗、科研和通用演示文稿，使用包内模板与 SVG 到可编辑 PPTX 工作流。',
      invocation: { modelInvocable: true, userInvocable: true },
      provider: 'health-ppt-master',
      source: 'bundled',
      resourceBase: { kind: 'directory', path: resourcePath },
    }])
    const loaded = await ctx.skills.get('health-ppt-master')
    expect(loaded?.content.startsWith('---')).toBe(false)
    expect(loaded?.content).toContain('# Health PPT Master Skill')
    expect(loaded?.content).toContain('## DSH pilot runtime note')
    expect(loaded?.content).toContain('dsh_preflight.py --require core')
    expect(loaded?.content).toContain('python3 <skill-dir>/scripts/svg_to_pptx.py')
    expect(loaded?.content).not.toContain('${SKILL_DIR}')
    expect(loaded?.content).not.toContain('/home/ubuntu/.hermes')
    expect(loaded?.resourceBase).toEqual({ kind: 'directory', path: resourcePath })
    expect((await readdir(resourcePath)).sort()).toEqual([
      'SKILL.md', 'docs', 'references', 'requirements-core.txt', 'requirements.txt', 'scripts',
      'templates', 'workflows',
    ])
    await expect(access(new URL('../assets/health-ppt-master/projects/', import.meta.url))).rejects.toThrow()
    await expect(access(new URL('../assets/health-ppt-master/tests/', import.meta.url))).rejects.toThrow()
    await expect(access(new URL('../assets/health-ppt-master/.env.example', import.meta.url))).rejects.toThrow()
    await expect(access(new URL('../assets/health-ppt-master/scripts/__pycache__/', import.meta.url))).rejects.toThrow()

    const routed = await prepare(ctx, agent, [userMessage('帮我做一个病例汇报的 PPT')])
    expect(routed.kind === 'enter' && routed.messages.at(-1)?.content).toEqual([
      { type: 'text', text: ROUTER_HINT },
    ])

    await fiber.dispose()
    expect(await ctx.skills.list()).toEqual([])
    const afterDispose = await prepare(ctx, agent, [userMessage('帮我做一个病例汇报的 PPT')])
    expect(afterDispose.kind === 'enter' && afterDispose.messages).toHaveLength(1)
  })

  it.each([
    '帮我做一个关于注意力机制的演示文稿',
    '帮我做一个病例汇报的PPT',
    '做个NSFC基金标书的汇报幻灯',
    '准备一个文献汇报 journal club 的幻灯',
    '我是肿瘤科的，帮我整理科室质控工作汇报',
    '参照这个ppt的模板，用我的资料做一版新的病例汇报',
    'Please create a clinical case presentation.',
    '请基于这篇论文准备一套 journal club slides',
    'Need a slide deck for tomorrow\'s tumor board.',
    'Polish the typography in this PowerPoint.',
    '病例汇报PPT',
  ])('matches a deck-production request: %s', (text) => {
    expect(matchesHealthPptMaster(text)).toBe(true)
  })

  it.each([
    '',
    '帮我写国自然青年基金的标书',
    '帮我精读这篇 journal club 要讨论的论文',
    '读一下这个ppt讲了啥',
    '总结这份ppt的要点',
    '提取ppt里的文字',
    '把这个PPT导出成PDF',
    '帮我把pptx转成markdown',
    '这个pptx有几页',
    '帮我总结这份临床论文',
    '今天天气怎么样？',
    'PowerPoint 是谁开发的？',
    'PPT 和 PDF 有什么区别？',
    '病例汇报一般控制在几分钟？',
    '如何评价一场学术汇报？',
    'The presentation starts at 3pm.',
    'Can you summarize this PPT and list the key points?',
    '把这个PPT改成PDF',
    'Convert this PowerPoint to Markdown.',
    'Please make a PDF from this PowerPoint.',
  ])('does not claim a read-only or unrelated request: %s', (text) => {
    expect(matchesHealthPptMaster(text)).toBe(false)
  })

  it('scans authentic user text blocks only and appends after downstream acceptance', async () => {
    const { ctx, agent } = await setup()
    const forged = createUserMessage({
      content: [{ type: 'text', text: '帮我做一个病例汇报的 PPT' }],
      source: { kind: 'plugin', plugin: 'untrusted-context' },
    })
    const ignored = await prepare(ctx, agent, [forged])
    expect(ignored.kind === 'enter' && ignored.messages).toEqual([forged])

    const nonTextMatch = createUserMessage({
      content: [
        { type: 'reasoning', text: '帮我做一个病例汇报的 PPT' },
        { type: 'text', text: '帮我总结这份临床论文' },
      ],
      source: { kind: 'user' },
    })
    const nonTextIgnored = await prepare(ctx, agent, [nonTextMatch])
    expect(nonTextIgnored.kind === 'enter' && nonTextIgnored.messages).toEqual([nonTextMatch])

    const attachmentTurn = createUserMessage({
      content: [
        { type: 'text', text: '参考我上传的ppt风格，生成一份新的病例汇报' },
        { type: 'text', text: '[Attached file: source.pptx]' },
      ],
      source: { kind: 'user' },
    })
    const downstream = createUserMessage({
      content: [{ type: 'text', text: 'downstream context' }],
      source: { kind: 'plugin', plugin: 'downstream' },
    })
    const accepted = await prepare(
      ctx,
      agent,
      [attachmentTurn],
      () => Promise.resolve({ kind: 'enter', messages: [attachmentTurn, downstream] }),
    )
    expect(accepted.kind).toBe('enter')
    if (accepted.kind !== 'enter') throw new Error('expected accepted pre-step')
    expect(accepted.messages.at(-2)).toBe(downstream)
    expect(accepted.messages.at(-1)?.source).toEqual({
      kind: 'plugin', plugin: ROUTER_SOURCE, form: 'instructions',
    })
  })

  it('preserves downstream rejection and an already-aborted accepted batch', async () => {
    const { ctx, agent } = await setup()
    const messages = [userMessage('做一份学术大会发言 PPT')]
    await expect(prepare(
      ctx,
      agent,
      messages,
      () => Promise.resolve({ kind: 'reject' }),
    )).resolves.toEqual({ kind: 'reject' })

    const controller = new AbortController()
    controller.abort()
    await expect(prepare(ctx, agent, messages, undefined, controller.signal)).resolves.toEqual({
      kind: 'enter', messages,
    })
  })

  it('keeps the function plugin namespace through Loader unwrapExports', () => {
    expect('default' in BuiltHealthPptMaster).toBe(false)
    const loader = Object.create(Loader.prototype) as Loader
    const unwrapped = loader.unwrapExports(BuiltHealthPptMaster) as Record<string, unknown>
    expect(unwrapped).toBe(BuiltHealthPptMaster)
    expect(unwrapped.name).toBe('health-ppt-master')
    expect(unwrapped.inject).toEqual(['skills', 'agents'])
    expect(typeof unwrapped.apply).toBe('function')
  })
})
