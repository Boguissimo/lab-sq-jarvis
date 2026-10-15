// @@T034 [US7] [FR-015] Detectar entidades compartilhadas entre features

import { KBStorage } from "../graph/storage.js"
import type { GraphNode } from "../graph/types.js"

// ---------------------------------------------------------------------------
// Tipos
// ---------------------------------------------------------------------------

export interface EntidadeCompartilhada {
  entidade: GraphNode
  features: FeatureUso[]
}

export interface FeatureUso {
  feature: string
  tipo: "CREATES" | "MODIFIES" | "READS" | "REFERENCES"
  nos: GraphNode[]
}

export interface CrossFeatureResult {
  entidadesCompartilhadas: EntidadeCompartilhada[]
  totalEntidades: number
  totalFeatures: number
}

// ---------------------------------------------------------------------------
// Detectar entidades compartilhadas
// ---------------------------------------------------------------------------

export function detectarCrossFeature(
  storage: KBStorage,
): CrossFeatureResult {
  // Coletar tabelas e RPCs como entidades compartilhaveis
  const tabelas = storage.buscarNosPorLabel("Table")
  const rpcs = storage.buscarNosPorLabel("RPC")
  const entidades = [...tabelas, ...rpcs]

  const resultado: EntidadeCompartilhada[] = []

  for (const entidade of entidades) {
    // Buscar todos os nos que referenciam esta entidade por nome
    const nomeEntidade = entidade.nome.toLowerCase()

    // Buscar tasks que mencionam esta entidade no arquivoAlvo
    const tasks = storage.buscarNosPorLabel("Task")
    const featureMap = new Map<string, FeatureUso>()

    for (const task of tasks) {
      const arquivoAlvo = ((task as any).arquivoAlvo as string) ?? ""
      const descricao = ((task as any).descricao as string) ?? ""
      const feature = task.feature ?? "global"

      if (
        arquivoAlvo.toLowerCase().includes(nomeEntidade) ||
        descricao.toLowerCase().includes(nomeEntidade)
      ) {
        if (!featureMap.has(feature)) {
          featureMap.set(feature, {
            feature,
            tipo: "REFERENCES",
            nos: [],
          })
        }
        featureMap.get(feature)!.nos.push(task)
      }
    }

    // Buscar FRs que mencionam esta entidade
    const frs = storage.buscarNosPorLabel("FunctionalRequirement")
    for (const fr of frs) {
      const descricao = ((fr as any).descricao as string) ?? ""
      const feature = fr.feature ?? "global"

      if (descricao.toLowerCase().includes(nomeEntidade)) {
        if (!featureMap.has(feature)) {
          featureMap.set(feature, {
            feature,
            tipo: "REFERENCES",
            nos: [],
          })
        }
        featureMap.get(feature)!.nos.push(fr)
      }
    }

    // So considerar compartilhada se 2+ features referenciam
    if (featureMap.size >= 2) {
      resultado.push({
        entidade,
        features: [...featureMap.values()],
      })
    }
  }

  const todasFeatures = new Set<string>()
  for (const ec of resultado) {
    for (const f of ec.features) {
      todasFeatures.add(f.feature)
    }
  }

  return {
    entidadesCompartilhadas: resultado,
    totalEntidades: resultado.length,
    totalFeatures: todasFeatures.size,
  }
}
