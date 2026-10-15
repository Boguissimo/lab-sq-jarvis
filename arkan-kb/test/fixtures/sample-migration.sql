-- @@T010 [US1] [FR-003] Migration de teste para sql-parser

CREATE TABLE IF NOT EXISTS public.categorias (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nome text NOT NULL,
  descricao text,
  categoria_pai_id uuid REFERENCES categorias(id),
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.itens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  conteudo text NOT NULL,
  categoria_id uuid NOT NULL REFERENCES categorias(id),
  tipo text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX idx_item_categoria ON itens(categoria_id);

CREATE OR REPLACE FUNCTION public.buscar_itens_por_categoria(
  p_categoria_id uuid
)
RETURNS SETOF itens
LANGUAGE sql
STABLE
AS $$
  SELECT * FROM itens
  WHERE categoria_id = p_categoria_id;
$$;

CREATE POLICY "Users can view own items"
ON itens
FOR SELECT
USING (auth.uid() = user_id);

ALTER TABLE itens ENABLE ROW LEVEL SECURITY;
