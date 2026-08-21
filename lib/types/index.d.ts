/**
 * Bundled health-ppt-master provider and soft router.
 *
 * @module @deepseek-ai/dsh-experimental-health-ppt-master
 */
import type { Context } from '@deepseek-ai/cordis';
/** Cordis plugin name and bundle row id. */
export declare const name = "health-ppt-master";
/** Services required by the provider and pre-step router. */
export declare const inject: string[];
/**
 * Register the immutable provider and soft router in one plugin fiber.
 * @param ctx - Cordis context carrying the skill and agent services.
 */
export declare function apply(ctx: Context): void;
