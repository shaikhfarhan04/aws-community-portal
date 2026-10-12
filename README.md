# AWS Community Registration Portal

Beginner learning project: Flask, Amazon RDS for MySQL, private S3, Docker on EC2, password hashing, login/logout, CSRF protection, multiple uploads and member-only presigned downloads.

## Architecture
Browser -> EC2 Docker/Gunicorn -> private RDS MySQL; application -> private S3 using the EC2 instance role. Never place AWS access keys in code or `.env` on EC2.

## AWS setup
1. Pick one region (examples use `ap-south-1`) and create a billing budget alert. Enable MFA.
2. Create an S3 bucket with Block Public Access ON and default encryption ON. Keep it private.
3. Create an EC2 IAM role with only `s3:PutObject`, `s3:GetObject`, and (for best-effort cleanup) `s3:DeleteObject` on `arn:aws:s3:::YOUR_BUCKET/members/*`. Attach it to EC2.
4. Create RDS MySQL in private subnets, Public access = No. Configure its security group to allow TCP 3306 only from the EC2 app security group.
5. EC2 security group: SSH from your IP only. For production, expose HTTPS via an ALB; don't expose container port 8000 directly.

## Create database
Connect to RDS from a network with access, then run `schema.sql`:
```bash
mysql -h YOUR_RDS_ENDPOINT -P 3306 -u DB_ADMIN -p < schema.sql
```
Create an application DB user using a strong generated password and least-privilege grants. The SQL host wildcard is not a network security boundary; security groups are. Prefer TLS for DB connections and store the password in Secrets Manager.

## Configure app
```bash
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```
Put the generated value in `SECRET_KEY`. Set `DATABASE_URL`, `S3_BUCKET_NAME`, and `AWS_REGION` in `.env`. URL-encode special characters in the DB password. Do not commit `.env`. For EC2, rely on its instance role for S3 access; for local tests use a local AWS profile rather than hard-coded keys.

## Test locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```
Tests use SQLite and don't need AWS. Build/run Docker:
```bash
docker build -t aws-community-portal:dev .
docker run --rm --env-file .env -p 127.0.0.1:8000:8000 aws-community-portal:dev
```
Open `http://127.0.0.1:8000`. Upload tests require valid S3 and RDS configuration.

## Deploy to EC2 with Docker
Install Docker Engine following the official instructions for your Amazon Linux version, then:
```bash
git clone YOUR_PRIVATE_GITHUB_REPOSITORY_URL
cd aws-community-portal
# Create .env securely on EC2; never commit it.
docker build -t aws-community-portal:release .
docker run -d --name community-portal --restart unless-stopped --env-file .env -p 127.0.0.1:8000:8000 aws-community-portal:release
docker logs --tail=100 community-portal
curl -f http://127.0.0.1:8000/health
```
Configure host Nginx as a reverse proxy and terminate HTTPS through an ALB/ACM or a correctly managed certificate. Do not open port 8000 to the internet. Set `SESSION_COOKIE_SECURE=true` once HTTPS is active.

## Features and limits
- Registration collects name, email, phone, city, skills, years of experience and password.
- Passwords are hashed; forms have CSRF protection; login sessions use HttpOnly cookies.
- Up to 10 files per request, max 10 MB each, extension allowlist. Files go to private S3; metadata and object keys go to MySQL.
- Download route verifies file ownership and returns a 5-minute presigned URL.
- Starter code automatically signs in a newly registered member. Add email verification, password reset, rate limiting, admin roles, content-based file validation and malware scanning before public production.
- S3 and MySQL aren't one transaction; cleanup is best effort. Production should track upload states and retry safely.
- `db.create_all()` is only for the starter lab. Add Flask-Migrate/Alembic for schema migrations.

## DevOps roadmap
1. GitHub pull requests, branch protection, secret scanning.
2. Jenkins CI: pytest, lint, dependency scan; fail builds on errors.
3. Add Ruff, pip-audit, SonarQube, Gitleaks and Trivy image scanning.
4. Push immutable Git-SHA-tagged images to Amazon ECR.
5. Deploy to staging, run health checks, manual production approval and rollback.
6. Terraform for VPC, subnets, security groups, EC2, S3, IAM, RDS and CloudWatch; protect remote state.
7. Ansible/cloud-init for Nginx, host configuration and CloudWatch agent.
8. CloudWatch logs, dashboards, alarms, RDS backups and tested recovery.
9. Production evolution: ALB, Auto Scaling, private RDS, multi-AZ as required, WAF if appropriate.
10. Consider presigned direct-to-S3 uploads for large files and add durable upload status tracking.
