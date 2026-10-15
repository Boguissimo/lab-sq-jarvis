// @@T004 [US1] [FR-002] Arquivo de teste para code-parser

import { resolve } from "node:path"
import type { GraphNode } from "./types"

export interface ConfiguracaoParser {
  verbose: boolean
  maxArquivos: number
}

export function parsearArquivo(caminho: string): GraphNode[] {
  const absoluto = resolve(caminho)
  return processarConteudo(absoluto)
}

// @@[FR-011] processarConteudo
function processarConteudo(caminho: string): GraphNode[] {
  return validarFormato(caminho) ? [] : []
}

// @@[FR-005] validarFormato
function validarFormato(caminho: string): boolean {
  return caminho.endsWith(".ts")
}

export class GerenciadorIndice {
  private nos: GraphNode[] = []

  constructor(private config: ConfiguracaoParser) {}

  adicionar(no: GraphNode): void {
    this.nos.push(no)
  }

  buscar(nome: string): GraphNode | undefined {
    return this.nos.find((n) => n.nome === nome)
  }

  listar(): GraphNode[] {
    return [...this.nos]
  }
}

export const criarPadrao = (verbose: boolean): ConfiguracaoParser => ({
  verbose,
  maxArquivos: 1000,
})
