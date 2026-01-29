-- Add a source column to track where the font came from
alter table public.fonts 
add column if not exists source text default 'Google Fonts';

-- Update the match_fonts function to include the source column
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
    1 - (f.embedding <=> query_embedding) as similarity
  from fonts f
  where 1 - (f.embedding <=> query_embedding) > match_threshold
  order by f.embedding <=> query_embedding
  limit match_count;
end;
$$;
