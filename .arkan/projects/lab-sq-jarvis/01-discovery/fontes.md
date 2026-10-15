# Inventário de Fontes — Lab SQ Jarvis

> **Fonte canônica** dos identificadores `JV-S###` (constituição, P11).
> **Níveis de confiança** (proposta, segue o modelo do Rygar): **1** medição própria com instrumento
> calibrado · **2** documentação do fabricante (manual, ficha técnica, página oficial) ·
> **3** literatura técnica e normas · **4** fóruns, relatos e páginas de revendedor ·
> **5** conhecimento prévio do agente ou memória. Fontes de nível 4–5 **só geram hipóteses**.
> **Limitação de 2026-10-15**: os sites dos fabricantes estavam bloqueados pela rede do ambiente;
> o conteúdo foi obtido por mecanismo de busca. “Lido diretamente” = não.

| ID | Fonte | Nível | Lido diretamente | O que sustenta |
| --- | --- | --- | --- | --- |
| JV-S001 | REW — ajuda da API: https://www.roomeqwizard.com/help/help_en-GB/html/api.html | 2 | não | API local, porta 4735, OpenAPI em `/doc.json`; GET sem licença |
| JV-S002 | REW — versões beta: https://www.roomeqwizard.com/beta.html | 2 | não | linha 5.40 e endpoints novos |
| JV-S003 | Fórum do autor do REW (API): https://www.avnirvana.com/threads/rew-api-beta-releases.12981/ | 4 (resposta do autor: 2) | não | varredura pela API exige Pro; resposta em frequência em Base64 |
| JV-S004 | Audiotec Fischer — DSP PC-Tool 6: https://www.audiotec-fischer.de/en/tools/dsp-pc-tool-6/ | 2 | não | funções do PC-Tool 6 |
| JV-S005 | Audiotec Fischer — TuneEQ: https://www.audiotec-fischer.de/en/knowledge-base/dsp-pc-tool/tuneeq/ | 2 | não | EQ automático por medição |
| JV-S006 | Audiotec Fischer — AMI: https://www.audiotec-fischer.de/en/accessories/ami | 2 | não | interface de medição com loopback |
| JV-S007 | Audiotec Fischer — downloads do PC-Tool: https://www.audiotec-fischer.de/en/tools/dsp-pc-tool/downloads/ | 2 | não | versões e modelos suportados |
| JV-S008 | EISA — DSP PC-Tool 6: https://eisa.eu/awards/dsp-pc-tool-6/ | 3 | não | AISA, Tune To Target, multibanda |
| JV-S009 | DIYMA — importação de filtros REW no PC-Tool: https://www.diymobileaudio.com/threads/how-to-import-rew-filter-sets-into-the-helix-v4-20-software.359418/page-2 | 4 | não | “REW Generic EQ .txt”; `.afpx` |
| JV-S010 | DIYMA — PC-Tool 6 lançado: https://www.diymobileaudio.com/threads/dsp-pc-tool-6-live-and-ready-for-download.476476/ | 4 | não | compatibilidade v5→v6 incerta |
| JV-S011 | Audison ACCORDO: https://audison.com/accordo/ | 2 | não | concorrente: calibração automática |
| JV-S012 | Tuning Labs: https://tuninglabs.net/ | 4 | não | concorrente com “IA” planejada |
| JV-S013 | Diagnóstico inicial do projeto: [`diagnostico-inicial.md`](diagnostico-inicial.md) | — | sim | registro histórico; não é fonte técnica |

Fontes técnicas de engenharia (literatura de filtros, crossovers, acústica de habitáculo) e fichas
técnicas dos equipamentos do Focus ainda **não** foram registradas: entram nas specs das features que
delas dependem.
