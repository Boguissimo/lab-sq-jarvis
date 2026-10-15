// @@T017 [US1] [FR-005] Persistencia SQLite via better-sqlite3 (nativo + FTS5)

import Database from "better-sqlite3"
import { existsSync, mkdirSync } from "node:fs"
import { dirname } from "node:path"
import type { GraphNode, GraphEdge, IndexMetadata } from "./types.js"

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

const SCHEMA_SQL = `
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  nome TEXT NOT NULL,
  file_path TEXT,
  feature TEXT,
  data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS edges (
  source_id TEXT NOT NULL,
  target_id TEXT NOT NULL,
  tipo TEXT NOT NULL,
  confianca REAL NOT NULL DEFAULT 0.5,
  data TEXT,
  UNIQUE(source_id, tipo, target_id)
);

CREATE TABLE IF NOT EXISTS metadata (
  chave TEXT PRIMARY KEY,
  valor TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label);
CREATE INDEX IF NOT EXISTS idx_nodes_feature ON nodes(feature);
CREATE INDEX IF NOT EXISTS idx_nodes_file_path ON nodes(file_path);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_tipo ON edges(tipo);
`

const FTS_SCHEMA_SQL = `
CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
  node_id,
  nome,
  label,
  feature,
  descricao,
  tokenize='unicode61'
);
`

// ---------------------------------------------------------------------------
// Storage
// ---------------------------------------------------------------------------

export class KBStorage {
  private db: Database.Database
  private ftsDisponivel = false

  private constructor(db: Database.Database) {
    this.db = db
    this.db.pragma("journal_mode = WAL")
    this.db.exec(SCHEMA_SQL)
    try {
      this.db.exec(FTS_SCHEMA_SQL)
      this.ftsDisponivel = true
    } catch {
      this.ftsDisponivel = false
    }
  }

  // @@T017 [US1] criar
  static async criar(dbPath: string): Promise<KBStorage> {
    const dir = dirname(dbPath)
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true })
    const db = new Database(dbPath)
    return new KBStorage(db)
  }

  // --- Nos ---

  // @@T017 [US1] salvarNos
  salvarNos(nos: GraphNode[]): void {
    const stmt = this.db.prepare(
      "INSERT OR REPLACE INTO nodes (id, label, nome, file_path, feature, data) VALUES (?, ?, ?, ?, ?, ?)",
    )

    const inserirLote = this.db.transaction((lote: GraphNode[]) => {
      for (const no of lote) {
        stmt.run(
          no.id,
          no.label,
          no.nome,
          no.filePath ?? null,
          no.feature ?? null,
          JSON.stringify(no),
        )
      }
    })

    inserirLote(nos)

    if (this.ftsDisponivel && nos.length > 0) {
      this.popularFts(nos)
    }
  }

  // @@T017 [US1] popularFts
  private popularFts(_nos: GraphNode[]): void {
    // FTS5 content table — recriar com TODOS os nos do DB para manter sincronizado
    this.db.exec("DROP TABLE IF EXISTS nodes_fts")
    this.db.exec(FTS_SCHEMA_SQL)

    const rows = this.db
      .prepare("SELECT id, data FROM nodes")
      .all() as Array<{ id: string; data: string }>

    const stmt = this.db.prepare(
      "INSERT INTO nodes_fts (node_id, nome, label, feature, descricao) VALUES (?, ?, ?, ?, ?)",
    )

    const inserirLote = this.db.transaction((lote: typeof rows) => {
      for (const row of lote) {
        const no = JSON.parse(row.data)
        const descricao = no.descricao ?? no.conteudo ?? ""
        stmt.run(row.id, no.nome ?? "", no.label ?? "", no.feature ?? "", descricao)
      }
    })

    inserirLote(rows)
  }

  // @@T017 [US1] obterNo
  obterNo(id: string): GraphNode | undefined {
    const row = this.db
      .prepare("SELECT data FROM nodes WHERE id = ?")
      .get(id) as { data: string } | undefined
    return row ? (JSON.parse(row.data) as GraphNode) : undefined
  }

  // @@T017 [US1] buscarNosPorLabel
  buscarNosPorLabel(label: string): GraphNode[] {
    const rows = this.db
      .prepare("SELECT data FROM nodes WHERE label = ?")
      .all(label) as Array<{ data: string }>
    return rows.map((r) => JSON.parse(r.data) as GraphNode)
  }

  /**
   * Busca nós com nome EXATAMENTE igual (sem ranking FTS, sem corte top-N).
   * Usado pela resolução por nome para não perder a definição vigente quando
   * ela cai fora do top-N do FTS (nomes populares, RPCs versionadas).
   */
  buscarNosPorNome(nome: string): GraphNode[] {
    const rows = this.db
      .prepare("SELECT data FROM nodes WHERE nome = ?")
      .all(nome) as Array<{ data: string }>
    return rows.map((r) => JSON.parse(r.data) as GraphNode)
  }

  // --- Arestas ---

  // @@T017 [US1] salvarArestas
  salvarArestas(arestas: GraphEdge[]): void {
    const stmt = this.db.prepare(
      "INSERT OR REPLACE INTO edges (source_id, target_id, tipo, confianca, data) VALUES (?, ?, ?, ?, ?)",
    )

    const inserirLote = this.db.transaction((lote: GraphEdge[]) => {
      for (const aresta of lote) {
        if (aresta.targetId.startsWith("__")) continue
        stmt.run(
          aresta.sourceId,
          aresta.targetId,
          aresta.tipo,
          aresta.confianca,
          JSON.stringify(aresta.propriedades ?? {}),
        )
      }
    })

    inserirLote(arestas)
  }

  // @@T017 [US1] obterArestasDoNo
  obterArestasDoNo(
    nodeId: string,
    direcao: "in" | "out" | "all" = "all",
  ): GraphEdge[] {
    let rows: any[]

    if (direcao === "out") {
      rows = this.db
        .prepare("SELECT * FROM edges WHERE source_id = ?")
        .all(nodeId)
    } else if (direcao === "in") {
      rows = this.db
        .prepare("SELECT * FROM edges WHERE target_id = ?")
        .all(nodeId)
    } else {
      rows = this.db
        .prepare("SELECT * FROM edges WHERE source_id = ? OR target_id = ?")
        .all(nodeId, nodeId)
    }

    return rows.map((row: any) => ({
      sourceId: row.source_id as string,
      targetId: row.target_id as string,
      tipo: row.tipo as any,
      confianca: row.confianca as number,
      propriedades: row.data ? JSON.parse(row.data as string) : undefined,
    }))
  }

  // --- Busca texto (FTS5 BM25 com fallback LIKE) ---

  // @@T017 [US1] buscarTexto
  buscarTexto(termo: string, limite: number = 10): GraphNode[] {
    if (this.ftsDisponivel) {
      return this.buscarTextoFts(termo, limite)
    }
    return this.buscarTextoLike(termo, limite)
  }

  // @@T017 [US1] buscarTextoFts
  private buscarTextoFts(termo: string, limite: number): GraphNode[] {
    const tokens = termo
      .replace(/[*"(){}[\]^~\\:]/g, " ")
      .trim()
      .split(/\s+/)
      .filter((t) => t.length > 1)

    if (tokens.length === 0) return []

    const termoExato = `"${tokens.join(" ")}"`
    const termoOr = tokens.join(" OR ")

    try {
      // Match exato primeiro
      let rows = this.db
        .prepare(
          `SELECT node_id, rank FROM nodes_fts WHERE nodes_fts MATCH ? ORDER BY rank LIMIT ?`,
        )
        .all(termoExato, limite) as Array<{ node_id: string; rank: number }>

      // Complementar com OR se poucos resultados
      if (rows.length < limite && tokens.length > 1) {
        const idsExistentes = new Set(rows.map((r) => r.node_id))
        const rowsOr = this.db
          .prepare(
            `SELECT node_id, rank FROM nodes_fts WHERE nodes_fts MATCH ? ORDER BY rank LIMIT ?`,
          )
          .all(termoOr, limite) as Array<{ node_id: string; rank: number }>

        for (const r of rowsOr) {
          if (!idsExistentes.has(r.node_id)) {
            rows.push(r)
            if (rows.length >= limite) break
          }
        }
      }

      const resultados = rows
        .map((r) => this.obterNo(r.node_id))
        .filter(Boolean) as GraphNode[]

      // FTS5 nao entende camelCase — complementar com LIKE se poucos resultados
      if (resultados.length < limite) {
        const idsExistentes = new Set(resultados.map((r) => r.id))
        const likeResultados = this.buscarTextoLike(termo, limite - resultados.length)
        for (const r of likeResultados) {
          if (!idsExistentes.has(r.id)) {
            resultados.push(r)
            if (resultados.length >= limite) break
          }
        }
      }

      return resultados
    } catch {
      return this.buscarTextoLike(termo, limite)
    }
  }

  // @@T017 [US1] buscarTextoLike
  private buscarTextoLike(termo: string, limite: number): GraphNode[] {
    const termoLike = `%${termo}%`
    const rows = this.db
      .prepare(
        "SELECT data FROM nodes WHERE nome LIKE ? OR data LIKE ? LIMIT ?",
      )
      .all(termoLike, termoLike, limite) as Array<{ data: string }>
    return rows.map((r) => JSON.parse(r.data) as GraphNode)
  }

  // --- Exportar tudo ---

  // @@T017 [US1] todosOsNos
  todosOsNos(): GraphNode[] {
    const rows = this.db
      .prepare("SELECT data FROM nodes")
      .all() as Array<{ data: string }>
    return rows.map((r) => JSON.parse(r.data) as GraphNode)
  }

  // @@T017 [US1] todasAsArestas
  todasAsArestas(): GraphEdge[] {
    const rows = this.db.prepare("SELECT * FROM edges").all() as any[]
    return rows.map((row: any) => ({
      sourceId: row.source_id as string,
      targetId: row.target_id as string,
      tipo: row.tipo as any,
      confianca: row.confianca as number,
    }))
  }

  // --- Metadata ---

  // @@T017 [US1] salvarMetadata
  salvarMetadata(meta: IndexMetadata): void {
    this.db
      .prepare("INSERT OR REPLACE INTO metadata (chave, valor) VALUES (?, ?)")
      .run("index_metadata", JSON.stringify(meta))
  }

  // @@T017 [US1] obterMetadata
  obterMetadata(): IndexMetadata | undefined {
    const row = this.db
      .prepare("SELECT valor FROM metadata WHERE chave = ?")
      .get("index_metadata") as { valor: string } | undefined
    return row ? (JSON.parse(row.valor) as IndexMetadata) : undefined
  }

  // --- Estatisticas ---

  // @@T017 [US1] contarNos
  contarNos(): number {
    const row = this.db
      .prepare("SELECT COUNT(*) as total FROM nodes")
      .get() as { total: number }
    return row.total
  }

  // @@T017 [US1] contarArestas
  contarArestas(): number {
    const row = this.db
      .prepare("SELECT COUNT(*) as total FROM edges")
      .get() as { total: number }
    return row.total
  }

  // @@T017 [US1] contarNosPorLabel
  contarNosPorLabel(): Record<string, number> {
    const rows = this.db
      .prepare("SELECT label, COUNT(*) as total FROM nodes GROUP BY label")
      .all() as Array<{ label: string; total: number }>
    const mapa: Record<string, number> = {}
    for (const row of rows) {
      mapa[row.label] = row.total
    }
    return mapa
  }

  // --- Limpar e Fechar ---

  // @@T017 [US1] limpar
  limpar(): void {
    this.db.exec("DELETE FROM edges")
    this.db.exec("DELETE FROM nodes")
    this.db.exec("DELETE FROM metadata")
    if (this.ftsDisponivel) {
      // FTS5 contentless table nao aceita DELETE — recriar
      this.db.exec("DROP TABLE IF EXISTS nodes_fts")
      this.db.exec(FTS_SCHEMA_SQL)
    }
  }

  // @@T017 [US1] fechar
  fechar(): void {
    try {
      this.db.exec("VACUUM")
    } catch {
      // VACUUM pode falhar em edge cases
    }
    this.db.close()
  }
}
