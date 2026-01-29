-- Add a JSONB column to store font file URLs (e.g., { "400": "url", "700": "url" })
alter table public.fonts 
add column if not exists files jsonb default '{}'::jsonb;

-- Update the match_fonts function to include the files column
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
  source text,
  files jsonb,
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
    f.source,
    f.files,
    1 - (f.embedding <=> query_embedding) as similarity
  from fonts f
  where 1 - (f.embedding <=> query_embedding) > match_threshold
  order by f.embedding <=> query_embedding
  limit match_count;
end;
$$;
