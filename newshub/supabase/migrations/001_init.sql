create extension if not exists pgcrypto;

create table if not exists public.sources (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  category text not null,
  rss_url text not null,
  homepage_url text not null,
  is_active boolean not null default true,
  created_at timestamp not null default now()
);

create table if not exists public.articles (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references public.sources(id) on delete cascade,
  title text not null,
  url text not null unique,
  published_at timestamp not null,
  excerpt text not null,
  image_url text null,
  hash text not null unique,
  created_at timestamp not null default now()
);

create table if not exists public.user_sources (
  user_id uuid not null references auth.users(id) on delete cascade,
  source_id uuid not null references public.sources(id) on delete cascade,
  primary key (user_id, source_id)
);

create table if not exists public.digests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  digest_date date not null,
  sent_at timestamp null,
  status text not null,
  created_at timestamp not null default now()
);

create index if not exists idx_sources_category on public.sources(category);
create index if not exists idx_articles_published_at on public.articles(published_at desc);
create index if not exists idx_articles_source_id on public.articles(source_id);
create index if not exists idx_digests_user_date on public.digests(user_id, digest_date);
