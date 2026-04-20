import { i as loadBundledPluginPublicSurfaceModuleSync } from "./facade-loader-CGu7k8Om.js";
//#region src/plugin-sdk/openai-runtime.ts
function loadFacadeModule() {
	return loadBundledPluginPublicSurfaceModuleSync({
		dirName: "openai",
		artifactBasename: "runtime-api.js"
	});
}
const DEFAULT_OLLAMA_EMBEDDING_MODEL = "nomic-embed-text";
const createOllamaEmbeddingProvider = ((...args) => loadFacadeModule().createOllamaEmbeddingProvider(...args));
//#endregion
export { createOllamaEmbeddingProvider as n, DEFAULT_OLLAMA_EMBEDDING_MODEL as t };
