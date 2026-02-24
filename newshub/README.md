# newshub

MVP de hub de notícias personalizado em monorepo.

## Stack
- **Web:** Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Supabase Auth.
- **API:** FastAPI com validação JWT do Supabase.
- **Worker:** Python para ingestão RSS e envio de digest diário por e-mail.
- **Banco/Auth:** Supabase (Postgres + Auth).
- **Email:** Resend.
- **Automação:** GitHub Actions (ingestão a cada 15 min + digest diário).

## Estrutura
```txt
newshub/
  apps/
    web/
    api/
    worker/
  supabase/migrations/001_init.sql
  .github/workflows/
```

## Rodando localmente

### 1) Pré-requisitos
- Node.js 20+
- Python 3.11+
- Conta Supabase
- Conta Resend

### 2) Configuração de ambiente
Copie os exemplos de variáveis:

```bash
cp .env.example .env
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```

Preencha com suas credenciais de Supabase, Resend e tokens internos.

### 3) Banco
- Execute a migration `supabase/migrations/001_init.sql` no SQL Editor do Supabase.
- (Opcional) habilite RLS conforme sua política de acesso.

### 4) API
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 5) Worker (execução manual)
```bash
cd apps/worker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m worker.ingest
python -m worker.digest
```

### 6) Web
```bash
cd apps/web
npm install
npm run dev
```

Abra: `http://localhost:3000`.

## Deploy cloud

### Web (Vercel)
- Root Directory: `apps/web`
- Defina variáveis `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` e `NEXT_PUBLIC_API_URL`.

### API (Render)
- Serviço Python com Root Directory `apps/api`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Configure variáveis de ambiente de Supabase/Resend/Internal Token.

### Worker
- Pode rodar como job no Render ou via GitHub Actions chamando os endpoints internos da API.

### Supabase
- Use projeto com Postgres/Auth e aplique a migration SQL.

### GitHub Actions
Workflows prontos em `.github/workflows`:
- `ingest.yml`: chama `/internal/ingest` a cada 15 min.
- `digest.yml`: chama `/internal/send-digest` às 10:00 UTC (07:00 BRT).

## Segurança e conteúdo
- O sistema **não republica conteúdo integral**.
- Apenas metadados: título, resumo curto, imagem, data, fonte e link original.

## Próximos passos sugeridos
- Implementar RLS estrito por usuário em `user_sources` e `digests`.
- Adicionar observabilidade (Sentry/Logtail).
- Melhorar ranking para digest (relevância por categoria + frequência).
