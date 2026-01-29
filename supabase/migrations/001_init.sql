-- Enable the pgvector extension to work with embeddings
create extension if not exists vector;

-- Create a table for fonts
create table if not exists public.fonts (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  category text,
  description text,
  license text default 'OFL',
  embedding vector(768), -- Dimensions for google/embedding-001 (or 1536 for OpenAI)
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create a table for semantic caching of search queries
create table if not exists public.searches (
  id uuid primary key default gen_random_uuid(),
  query_text text not null unique,
  embedding vector(768),
  response_json jsonb not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Function to search for fonts using vector similarity
create or replace function match_fonts (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  name text,
  category text,
  description text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    f.name,
    f.category,
    f.description,
    1 - (f.embedding <=> query_embedding) as similarity
  from fonts f
  where 1 - (f.embedding <=> query_embedding) > match_threshold
  order by f.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Function to check for cached search results
create or replace function match_searches (
  query_embedding vector(768),
  match_threshold float
)
returns table (
  response_json jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    s.response_json,
    1 - (s.embedding <=> query_embedding) as similarity
  from searches s
  where 1 - (s.embedding <=> query_embedding) > match_threshold
  order by s.embedding <=> query_embedding
  limit 1;
end;
$$;
