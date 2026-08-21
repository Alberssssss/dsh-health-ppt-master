import { r as registerHealthPptMasterRouter } from "./router-DqFSdLOQ.js";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { BUNDLED_SKILL_RANK } from "@deepseek-ai/dsh-skill";
//#region src/index.ts
/**
* Bundled health-ppt-master provider and soft router.
*
* @module @deepseek-ai/dsh-experimental-health-ppt-master
*/
const PROVIDER_NAME = "health-ppt-master";
const SKILL_BODY_URL = new URL("../assets/health-ppt-master/SKILL.md", import.meta.url);
const RESOURCE_BASE = {
	kind: "directory",
	path: fileURLToPath(new URL("../assets/health-ppt-master/", import.meta.url))
};
const INVOCATION = {
	modelInvocable: true,
	userInvocable: true
};
const DESCRIPTION = "生成或改造医疗、科研和通用演示文稿，使用包内模板与 SVG 到可编辑 PPTX 工作流。";
const FRONTMATTER = /^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/;
const CANDIDATE = {
	name: "health-ppt-master",
	description: DESCRIPTION,
	invocation: INVOCATION,
	provider: PROVIDER_NAME,
	source: "bundled",
	resourceBase: RESOURCE_BASE,
	rank: BUNDLED_SKILL_RANK,
	locator: SKILL_BODY_URL
};
const provider = {
	name: PROVIDER_NAME,
	list: () => Promise.resolve([CANDIDATE]),
	async get(_candidate) {
		const content = (await readFile(SKILL_BODY_URL, "utf8")).replace(FRONTMATTER, "").trim();
		return {
			name: CANDIDATE.name,
			description: CANDIDATE.description,
			invocation: CANDIDATE.invocation,
			provider: CANDIDATE.provider,
			source: CANDIDATE.source,
			resourceBase: RESOURCE_BASE,
			content
		};
	}
};
/** Cordis plugin name and bundle row id. */
const name = "health-ppt-master";
/** Services required by the provider and pre-step router. */
const inject = ["skills", "agents"];
/**
* Register the immutable provider and soft router in one plugin fiber.
* @param ctx - Cordis context carrying the skill and agent services.
*/
function apply(ctx) {
	ctx.skills.registerProvider(() => provider);
	registerHealthPptMasterRouter(ctx);
}
//#endregion
export { apply, inject, name };
