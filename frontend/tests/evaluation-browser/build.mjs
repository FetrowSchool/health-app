import {build} from 'vite'
import vue from '@vitejs/plugin-vue'
import {fileURLToPath} from 'node:url'
import path from 'node:path'
const root=fileURLToPath(new URL('.',import.meta.url))
const out=process.argv[2]
if(!out||!path.isAbsolute(out)||out.startsWith(path.resolve(root,'../..')))throw Error('Pass an absolute temporary output directory outside frontend.')
await build({configFile:false,root,plugins:[vue()],resolve:{alias:{vue:fileURLToPath(new URL('../../node_modules/vue/dist/vue.runtime.esm-bundler.js',import.meta.url))}},build:{outDir:out,emptyOutDir:true}})
