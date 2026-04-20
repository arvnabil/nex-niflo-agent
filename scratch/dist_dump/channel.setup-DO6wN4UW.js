import { t as createZalouserPluginBase } from "./shared-CDdPl2eP.js";
import { n as zalouserSetupAdapter } from "./setup-core-DP9WmyzP.js";
import { t as zalouserSetupWizard } from "./setup-surface-zAfIE-0m.js";
//#region extensions/zalouser/src/channel.setup.ts
const zalouserSetupPlugin = { ...createZalouserPluginBase({
	setupWizard: zalouserSetupWizard,
	setup: zalouserSetupAdapter
}) };
//#endregion
export { zalouserSetupPlugin as t };
