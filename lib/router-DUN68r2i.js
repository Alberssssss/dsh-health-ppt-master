import { createUserMessage } from "@deepseek-ai/dsh-llm";
//#region lib/types/router.js
/** Deterministic soft routing for the packaged health-ppt-master skill. */
/** Source owner recorded on durable router instructions. */
const ROUTER_SOURCE = "health-ppt-master";
/** Stable model-visible reminder emitted for a matching user request. */
const ROUTER_HINT = [
	"<health-ppt-master-router>",
	"这是软路由提示，不表示 skill 已加载。本轮用户请求可能要求新建、修改、优化或参照模板生成一份 PPT/deck。采取任务动作前，先调用 `skill` 工具并使用精确名称 `health-ppt-master` 加载完整说明；只有加载后的说明才是执行依据。仅阅读、提取、总结、导出或转换现有 PPT/PPTX 且不产出 deck 时不要使用此 skill。该试点只绑定发现、路由与生命周期，不表示 Hermes 的 Python 依赖、document-parser、浏览器预览、图片提供方或交付治理已经迁移。",
	"</health-ppt-master-router>"
].join("\n");
const DECK_TERMS = [
	"ppt",
	"pptx",
	"powerpoint",
	"幻灯",
	"演示文稿",
	"课件",
	"slide",
	"slides",
	"deck",
	"presentation"
];
const PRODUCTION_TERMS = [
	"生成",
	"制作",
	"做成",
	"做个",
	"做一个",
	"做一份",
	"做份",
	"做一版",
	"写个",
	"帮我做",
	"创建",
	"新建",
	"重做",
	"重新做",
	"优化",
	"美化",
	"排版",
	"套用",
	"填充",
	"填进",
	"填到",
	"参照",
	"仿照",
	"出一版",
	"出个",
	"整理",
	"改成",
	"改一下",
	"按这版",
	"照这版",
	"照这个做"
];
const ENGLISH_PRODUCTION = /\b(?:create|make|build|generate|redesign|edit|optimize|polish)\b/i;
const READ_ONLY_TERMS = [
	"读取",
	"读一下",
	"打开",
	"看看",
	"总结",
	"提取",
	"导出",
	"转成",
	"转换",
	"有几页",
	"多少页",
	"讲了什么",
	"讲了啥",
	"内容是什么",
	"read ",
	"summarize",
	"extract",
	"export",
	"convert",
	"how many slides"
];
const PRESENTATION_DELIVERABLES = [
	"汇报材料",
	"路演",
	"做演示",
	"工作汇报",
	"科室汇报",
	"年度总结",
	"季度汇报",
	"述职",
	"进修汇报",
	"病例汇报",
	"病例讨论",
	"疑难病例",
	"病历汇报",
	"教学查房",
	"查房课件",
	"开题报告",
	"中期汇报",
	"结题汇报",
	"文献汇报",
	"读书报告会",
	"学术汇报",
	"大会发言",
	"学术幻灯",
	"答辩",
	"医学科普",
	"职称申报",
	"职称晋升材料",
	"科技奖申报",
	"等级评审",
	"学科评审",
	"药械申报",
	"注册申报",
	"case report ppt",
	"clinical case ppt",
	"journal club deck",
	"grant proposal slides"
];
const TEMPLATE_ACTIONS = [
	"套用模板",
	"套用这个",
	"按这个模板",
	"按模板",
	"用这个模板",
	"模板填充",
	"填进模板",
	"填到模板",
	"参照模板",
	"参照这个ppt",
	"参照这份ppt",
	"仿照这个ppt",
	"仿照这份ppt",
	"参考这个模板",
	"参考这份模板",
	"参考这个ppt",
	"参考这份ppt",
	"参考上传的ppt",
	"照着这个ppt",
	"照这个ppt",
	"按这个ppt",
	"按这份ppt",
	"医院模板",
	"科室模板",
	"本院模板",
	"院内模板"
];
const DOMAIN_MARKERS = [
	"科室",
	"医院",
	"临床",
	"病区",
	"门诊",
	"病房",
	"医师",
	"主任医师",
	"医学",
	"科研",
	"医生",
	"我科",
	"本科室",
	"院内",
	"学科"
];
const DOMAIN_DELIVERABLES = [
	"工作汇报",
	"科室汇报",
	"课件",
	"幻灯",
	"演示",
	"述职",
	"答辩",
	"病例汇报",
	"文献汇报",
	"大会发言",
	"开题报告",
	"中期汇报",
	"结题汇报"
];
function includesAny(text, terms) {
	return terms.some((term) => text.includes(term));
}
/**
* Decide whether one user-authored text matches the packaged skill's deck-production domain.
* @param value - user-authored text from the claimed pre-step batch.
* @returns whether the soft router should recommend loading the skill.
*/
function matchesHealthPptMaster(value) {
	const text = value.trim().toLowerCase();
	if (text.length === 0) return false;
	if (!(includesAny(text.replace(/\s+/g, ""), PRODUCTION_TERMS) || ENGLISH_PRODUCTION.test(text)) && includesAny(text, READ_ONLY_TERMS)) return false;
	const hasDeckTerm = includesAny(text, DECK_TERMS);
	const hasDeliverable = includesAny(text, PRESENTATION_DELIVERABLES);
	const hasTemplateAction = includesAny(text, TEMPLATE_ACTIONS);
	const hasDomainCombination = includesAny(text, DOMAIN_MARKERS) && includesAny(text, DOMAIN_DELIVERABLES);
	return hasDeckTerm || hasDeliverable || hasTemplateAction || hasDomainCombination;
}
function textOf(message) {
	return message.content.flatMap((block) => block.type === "text" ? [block.text] : []).join("\n");
}
/**
* Match only user-authored text messages from one claimed pre-step batch.
* @param messages - exclusive claimed messages offered to the waterfall.
* @returns whether any authentic user message matches the route.
*/
function matchesHealthPptMasterMessages(messages) {
	return messages.some((message) => message.source.kind === "user" && matchesHealthPptMaster(textOf(message)));
}
/**
* Register the waterfall listener that appends the soft route after downstream acceptance.
* @param ctx - plugin context carrying the agent event service.
*/
function registerHealthPptMasterRouter(ctx) {
	ctx.on("agent/pre-step", async ({ messages, signal }, next) => {
		const matched = matchesHealthPptMasterMessages(messages);
		const decision = await next();
		if (!matched || decision.kind === "reject" || signal.aborted) return decision;
		return {
			kind: "enter",
			messages: [...decision.messages, createUserMessage({
				content: [{
					type: "text",
					text: ROUTER_HINT
				}],
				source: {
					kind: "plugin",
					plugin: ROUTER_SOURCE,
					form: "instructions"
				}
			})]
		};
	});
}
//#endregion
export { ROUTER_SOURCE as n, registerHealthPptMasterRouter as r, ROUTER_HINT as t };
