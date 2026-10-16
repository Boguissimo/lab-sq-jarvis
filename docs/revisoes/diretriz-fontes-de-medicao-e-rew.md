# Lab SQ Jarvis | Diretriz de evolução: fontes de medição e integração REW

> **Origem**: complemento enviado pelo desenvolvedor em 2026-10-16, junto da revisão técnica do plano do JV-V02. Transcrito como recebido. **Não altera o escopo aprovado do JV-V02**; deve ser registrado no planejamento evolutivo (feature map / decisões) por decisão `JV-D` própria e implementado em incremento próprio.

## Objetivo

Preparar a arquitetura do Lab SQ Jarvis para trabalhar com curvas acústicas sintéticas e, futuramente, medições reais provenientes do Room EQ Wizard (REW), inclusive aquelas obtidas provisoriamente com o microfone de um celular.

Esta diretriz não altera automaticamente o escopo aprovado do JV-V02. Sua implementação deverá ocorrer em incremento próprio, respeitando o processo do Arkan Core.

## 1. Integração com a API HTTP do REW

O Room EQ Wizard disponibiliza uma API HTTP local.

- Documentação oficial: https://www.roomeqwizard.com/help/help/html/api.html
- Endereço padrão: `http://127.0.0.1:4735`
- Contrato OpenAPI: `http://127.0.0.1:4735/doc.json`

A API permite consultar medições e importar respostas em frequência. Consultar a documentação e o contrato OpenAPI da versão instalada antes de implementar endpoints e formatos de dados. A leitura das medições não exige licença Pro. A automação de sweeps pela API exige licença Pro.

## 2. Categorias de dados

O sistema deverá distinguir três categorias operacionais.

- **SYNTHETIC**: curvas geradas por modelos determinísticos, com parâmetros conhecidos, sementes reproduzíveis e defeitos intencionalmente introduzidos.
- **EXPERIMENTAL**: medições reais não calibradas, incluindo aquelas obtidas provisoriamente com o microfone de um celular e disponibilizadas ao REW.
- **CALIBRATED**: medições instrumentais com calibração documentada, respeitando as limitações específicas da aquisição.

A classificação não substitui os metadados técnicos. Registrar separadamente:

- Calibração da resposta em frequência.
- Calibração de SPL absoluto.
- Existência e compatibilidade da referência temporal.
- Equipamento utilizado.
- Posição e condições de aquisição.
- Origem e identificação dos dados.

## 3. Arquitetura

Separar claramente a origem dos dados, sua validação e o motor de diagnóstico.

Fontes previstas: gerador acústico sintético; arquivos importados; REW via API HTTP.

Todas deverão alimentar um modelo interno comum, preservando unidades, metadados, origem, disponibilidade de fase e referência temporal. O diagnóstico deverá considerar não apenas a curva apresentada, mas também quais inferências são tecnicamente admissíveis com os dados disponíveis.

## 4. Limitações de diagnóstico

- Medições sem referência temporal compatível não permitem conclusões confiáveis sobre fase relativa, alinhamento temporal ou soma complexa prevista.
- Medições sem calibração de SPL não permitem conclusões confiáveis sobre pressão sonora absoluta.
- O microfone de celular poderá servir para verificar o fluxo de aquisição, importação e análise, bem como observar alterações relativas sob condições controladas. Não deve ser considerado instrumento equivalente a um microfone de medição calibrado.
- Resultados sintéticos deverão ser identificados permanentemente como simulações.
- O programa não poderá converter artificialmente a qualidade de uma medição experimental em qualidade instrumental confirmada.

## 5. Gerador acústico

Priorizar curvas sintéticas fisicamente coerentes e reproduzíveis. O gerador deverá permitir simular:

1. Respostas em frequência irregulares.
2. Ressonâncias e reflexões.
3. Cancelamentos em crossovers.
4. Diferenças de nível entre vias.
5. Atrasos relativos.
6. Inversões de polaridade.
7. Alterações de filtros e equalização.
8. Ruído e limitações de aquisição.

Magnitude, fase e soma deverão resultar de um modelo matemático coerente, e não de perturbações aleatórias independentes. Cada cenário deverá registrar os defeitos introduzidos e os resultados esperados, permitindo verificar objetivamente os diagnósticos produzidos pelo Lab SQ.

## 6. Instrumentação prevista

- Microfone de medição Dayton EMM-6.
- Interface de áudio Behringer UMC202HD.
- Calibrador acústico de SPL em etapa posterior.

O desenvolvimento não ficará condicionado à aquisição desses equipamentos.

## 7. Restrições

- Não implementar escrita automática no DSP.
- Preservar a integração futura com o ecossistema HELIX e o PC-Tool.
- Manter os dados sintéticos separados dos dados reais, evitando que testes de software sejam interpretados como validação acústica do veículo.

## Encaminhamento

Registrar esta diretriz no planejamento evolutivo do Lab SQ Jarvis e identificar as interfaces que merecem preparação arquitetural. Não acrescentar automaticamente sua implementação ao JV-V02. A prioridade imediata permanece o desenvolvimento e a validação do motor de diagnóstico com curvas sintéticas. A integração HTTP com o REW e a aquisição experimental por celular deverão ser tratadas em incremento posterior, com requisitos e testes próprios.
