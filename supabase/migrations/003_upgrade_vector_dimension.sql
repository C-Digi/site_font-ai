-- Increase vector dimension to 4096 for qwen/qwen3-embedding-8b
alter table public.fonts alter column embedding type vector(4096);
alter table public.searches alter column embedding type vector(4096);

-- Note: We need to recreate or update the functions because the signature uses vector(768)
create or replace function match_fonts (
  query_embedding vector(4096),
  match_threshold float,
  match_count int
)
returns table (
  name text,
  category text,
  description text,
  tags text[],
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
    f.tags,
    1 - (f.embedding <=> query_embedding) as similarity
  from fonts f
  where 1 - (f.embedding <=> query_embedding) > match_threshold
  order by f.embedding <=> query_embedding
  limit match_count;
end;
$$;

create or replace function match_searches (
  query_embedding vector(4096),
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
