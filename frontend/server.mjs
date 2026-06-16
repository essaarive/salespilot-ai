import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer, request as httpRequest } from "node:http";
import { extname, join, normalize } from "node:path";

const port = Number(process.env.PORT || 80);
const backendOrigin = process.env.BACKEND_ORIGIN || "http://backend:8000";
const distDir = join(process.cwd(), "dist");

const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
};

function proxyApi(req, res) {
  const target = new URL(req.url || "/", backendOrigin);
  const proxyReq = httpRequest(
    target,
    {
      method: req.method,
      headers: {
        ...req.headers,
        host: target.host,
      },
    },
    (proxyRes) => {
      res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
      proxyRes.pipe(res);
    },
  );

  proxyReq.on("error", () => {
    res.writeHead(502, { "content-type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ detail: "Backend service unavailable" }));
  });

  req.pipe(proxyReq);
}

async function serveStatic(req, res) {
  const pathname = decodeURIComponent(new URL(req.url || "/", "http://localhost").pathname);
  const safePath = normalize(pathname).replace(/^(\.\.[/\\])+/, "");
  const requestedPath = join(distDir, safePath === "/" ? "index.html" : safePath);

  let filePath = requestedPath;
  try {
    const fileStat = await stat(filePath);
    if (fileStat.isDirectory()) {
      filePath = join(filePath, "index.html");
    }
  } catch {
    filePath = join(distDir, "index.html");
  }

  const contentType = mimeTypes[extname(filePath)] || "application/octet-stream";
  res.writeHead(200, { "content-type": contentType });
  createReadStream(filePath).pipe(res);
}

createServer((req, res) => {
  if ((req.url || "").startsWith("/api/")) {
    proxyApi(req, res);
    return;
  }

  serveStatic(req, res).catch(() => {
    res.writeHead(500, { "content-type": "text/plain; charset=utf-8" });
    res.end("Internal server error");
  });
}).listen(port, "0.0.0.0", () => {
  console.log(`Frontend server listening on ${port}`);
});
