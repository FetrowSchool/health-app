// Evaluation-only static preview/proxy. Does not start the production entry.
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'

if (!process.argv[2] || !path.isAbsolute(process.argv[2])) throw Error('Pass the absolute harness build directory.')
const root = path.resolve(process.argv[2])
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8' }
http.createServer((req, res) => {
  if (req.url.startsWith('/api/')) {
    const upstream = http.request({ hostname: '127.0.0.1', port: 8190, path: req.url, method: req.method,
      headers: { ...req.headers, host: '127.0.0.1:8190' } }, response => {
      res.writeHead(response.statusCode, response.headers); response.pipe(res)
    })
    upstream.on('error', () => { res.writeHead(503, { 'Content-Type': 'application/json' }); res.end('{"detail":"Unavailable"}') })
    req.pipe(upstream); return
  }
  const target = path.resolve(root, '.' + (req.url === '/' ? '/index.html' : new URL(req.url, 'http://localhost').pathname))
  if (!target.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return }
  fs.readFile(target, (error, data) => {
    if (error) { res.writeHead(404); res.end(); return }
    res.writeHead(200, { 'Content-Type': types[path.extname(target)] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(data)
  })
}).listen(5290, '127.0.0.1', () => console.log('Simulated voice evaluation preview: http://127.0.0.1:5290'))
