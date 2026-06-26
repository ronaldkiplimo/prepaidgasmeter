# Deployment Troubleshooting

## Frontend still calls port 8000

If the browser Network tab shows requests like:

```text
http://102.212.245.79:8000/api/v1/auth/login/
http://localhost:8000/api/v1/auth/login/
```

the running Next.js bundle was built with the wrong API base. The browser should call the same origin instead:

```text
http://102.212.245.79/api/v1/auth/login/
```

Check the running container:

```bash
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml exec web sh -lc 'grep -R "localhost:8000\|102.212.245.79:8000" -n /app/.next /app/public /app/server.js 2>/dev/null || true'
```

Expected result: no output.

If there is output, rebuild and recreate the web container:

```bash
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml down
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml build --no-cache web
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml up -d
```

Then hard refresh the browser or clear site data.

## Nginx returns 502

A 502 means Nginx cannot reach the upstream service. Check that Docker has bound the upstream ports on localhost:

```bash
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml ps
ss -ltnp | grep -E ':80|:3000|:8000'
curl -I http://127.0.0.1:3000/login
curl -I http://127.0.0.1:8000/api/docs/
curl -I http://102.212.245.79/login
```

Check logs:

```bash
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml logs --tail=100 web
docker compose -f docker-compose.yml -f deploy/docker/docker-compose.localhost-ports.yml logs --tail=100 backend
tail -n 100 /var/log/nginx/prepaidgasmeter.error.log
```

If `127.0.0.1:3000` fails, restart the web container. If `127.0.0.1:8000` fails, restart the backend container.
