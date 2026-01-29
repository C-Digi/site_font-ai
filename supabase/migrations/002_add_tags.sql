-- Add a text array column for semantic tags
alter table public.fonts 
add column if not exists tags text[] default '{}';

-- Update the match_fonts function to return tags
create or replace function match_fonts (
  query_embedding vector(768),
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
