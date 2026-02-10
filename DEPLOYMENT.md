# Deployment Guide: EC2 + GitHub Pages

This project uses two deployment targets:
- **Amazon EC2**: runs the Streamlit app and daily pipeline.
- **GitHub Pages**: serves a static landing page (`docs/`) linking to the EC2 app.

## 1) EC2 deploy (Ubuntu)

### Create instance
- AMI: Ubuntu 24.04 LTS (recommended). Ubuntu 22.04 also works with the bootstrap script.
- Size: `t3.medium` or larger
- Security group inbound:
  - `22` from your IP
  - `80` from `0.0.0.0/0`

### Clone and bootstrap
On your EC2 host:

```bash
sudo apt-get update -y
sudo apt-get install -y git

cd /home/ubuntu
git clone https://github.com/<YOUR_USER>/<YOUR_REPO>.git thedaily
cd thedaily
chmod +x deploy/ec2/bootstrap_ec2.sh
./deploy/ec2/bootstrap_ec2.sh https://github.com/<YOUR_USER>/<YOUR_REPO>.git
```

If you previously ran bootstrap on Python 3.10 and saw `requires a different Python: 3.10... not in '>=3.11'`, run:

```bash
cd /home/ubuntu/thedaily
git pull
rm -rf .venv
./deploy/ec2/bootstrap_ec2.sh https://github.com/<YOUR_USER>/<YOUR_REPO>.git
```

### Configure secrets

```bash
sudo nano /etc/thedaily.env
```

Set at least:

```bash
OPENAI_API_KEY=<your-key>
```

Then reload services:

```bash
sudo systemctl daemon-reload
sudo systemctl restart thedaily-streamlit.service
sudo systemctl start thedaily-pipeline.service
```

### Verify

```bash
systemctl status thedaily-streamlit.service --no-pager
systemctl status thedaily-pipeline.timer --no-pager
journalctl -u thedaily-streamlit.service -n 100 --no-pager
journalctl -u thedaily-pipeline.service -n 100 --no-pager
```

Open: `http://<EC2_PUBLIC_IP_OR_DNS>/`

## 2) GitHub Pages deploy

### Enable Pages in GitHub
- Repo Settings -> Pages -> Source: **GitHub Actions**.

The workflow file `.github/workflows/deploy-pages.yml` auto-deploys `docs/` on pushes to `main`.

### Update landing page link
Edit `docs/index.html` and replace:

- `https://YOUR_EC2_PUBLIC_DNS_OR_DOMAIN`

with your actual EC2 DNS or domain name.

Commit and push to `main`; Pages will publish automatically.

## 3) Optional domain + HTTPS

- Attach a domain to EC2 (Route53 or your DNS provider).
- Add TLS via Certbot + Nginx.
- Update `docs/index.html` link to `https://your-domain`.
