/** Deterministic soft routing for the packaged health-ppt-master skill. */
import type { Context } from '@deepseek-ai/cordis';
import { type UserMessage } from '@deepseek-ai/dsh-llm';
/** Source owner recorded on durable router instructions. */
export declare const ROUTER_SOURCE = "health-ppt-master";
/** Stable model-visible reminder emitted for a matching user request. */
export declare const ROUTER_HINT: string;
/**
 * Decide whether one user-authored text matches the packaged skill's deck-production domain.
 * @param value - user-authored text from the claimed pre-step batch.
 * @returns whether the soft router should recommend loading the skill.
 */
export declare function matchesHealthPptMaster(value: string): boolean;
/**
 * Match only user-authored text messages from one claimed pre-step batch.
 * @param messages - exclusive claimed messages offered to the waterfall.
 * @returns whether any authentic user message matches the route.
 */
export declare function matchesHealthPptMasterMessages(messages: readonly UserMessage[]): boolean;
/**
 * Register the waterfall listener that appends the soft route after downstream acceptance.
 * @param ctx - plugin context carrying the agent event service.
 */
export declare function registerHealthPptMasterRouter(ctx: Context): void;
