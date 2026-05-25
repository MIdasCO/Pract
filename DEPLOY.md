# Deployment and required secrets

Required repository secrets (Settings → Secrets and variables → Actions):

- `GHCR_USER` — GitHub username that owns the packages (used to login to ghcr.io).
- `GHCR_PAT` — Personal Access Token with `write:packages` permission for publishing to GHCR.
- `SERVER_HOST` — IP or hostname of the target VPS where the container will be deployed.
- `SERVER_USER` — SSH username on the target server.
- `SERVER_SSH_KEY` — Private SSH key for the `SERVER_USER` (paste the key contents as the secret).
- (Optional) `SERVER_SSH_PORT` — SSH port (default 22 if not set).

How the workflow uses these secrets:

- The workflow builds the image and tags it as `ghcr.io/<owner>/<repo>:<sha>` (owner/repo are lowercased).
- It logs in to GHCR using `GHCR_USER` and `GHCR_PAT`, pushes the image, then SSHes into the server to pull and run the image.

Local quick test (Docker Desktop):

```bash
# Build locally
docker build -f Dockerfile -t ghcr.io/your-org/your-repo:test .

# Login locally (use your PAT)
echo "YOUR_GHCR_PAT" | docker login ghcr.io -u "YOUR_GHCR_USER" --password-stdin

# Push to ghcr (requires GHCR permissions and correct image name)
docker push ghcr.io/your-org/your-repo:test

# On server (via SSH) pull and run
ssh -i ~/.ssh/id_rsa user@server_ip \
  "echo \"YOUR_GHCR_PAT\" | docker login ghcr.io -u \"YOUR_GHCR_USER\" --password-stdin && docker pull ghcr.io/your-org/your-repo:test && docker run -d --name fast_backend -p 8000:8000 ghcr.io/your-org/your-repo:test"
```

Notes:
- Keep `GHCR_PAT` secret; prefer using the built-in `GITHUB_TOKEN` only if you can publish with it from Actions (it often has enough permissions).
- `SERVER_SSH_KEY` should be the private key; the corresponding public key must be in `~/.ssh/authorized_keys` for `SERVER_USER` on the server.
