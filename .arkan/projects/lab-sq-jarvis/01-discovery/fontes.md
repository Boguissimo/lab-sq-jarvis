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
| JV-S014 | REW — ajuda da janela e dos filtros de EQ: https://www.roomeqwizard.com/help/help/html/eqwindow.html e https://www.roomeqwizard.com/help/help/html/eqfilters.html | 2 | não | “Match response to target”, faixa de ajuste, filtros travados, recomendação de limitar filtros a baixas frequências |
| JV-S015 | Audiotec Fischer — base de conhecimento, ATM: https://www.audiotec-fischer.de/en/knowledge-base/DSP-PC-Tool/atm/ | 2 | não | medição automática de atraso por canal |
| JV-S016 | Notas de lançamento do PC-Tool 5 (TuneEQ), republicadas: https://www.emmanet.info/audiotec-fischer-dsp-pc-tool-5-feat-tuneeq/ | 2 | não | média espacial, resolução ≥ 1/6 de oitava |
| JV-S017 | Audiotec Fischer — DSP Setup Guide Vol. 1: https://www.audiotec-fischer.de/media/pdf/d3/47/70/ATF_Sound_Tuning_Magazine-DSP_Setup_Guide_Vol1_web.pdf | 2 (versão antiga) | não | não encher vales; cuidado com reforços acima de ≈ 4 dB; processo iterativo |
| JV-S018 | Flat Liner Tuning — página principal: https://flatlinertuning.com/ | 2 (comercial) | não | fluxo guiado, sessão remota, preços |
| JV-S019 | Flat Liner Tuning — aplicativo e download: https://flatlinertuning.com/app.html e https://flatlinertuning.com/download.html | 2 (comercial) | não | API do REW, crossovers, EQ, TA por distância, verificação; divergência Windows/macOS |
| JV-S020 | Tuning Labs — página principal: https://tuninglabs.net/ | 2 (comercial) | não | edições, oficina, IA online, biblioteca |
| JV-S021 | Tuning Labs — blog “AI Auto-Tune Explained”: https://tuninglabs.net/blog/ai-auto-tune-explained.html | 2 (comercial) | não | 6 fases, verificações antes de aplicar |
| JV-S022 | Tuning Labs — guia para iniciantes: https://tuninglabs.net/guides/how-to-tune-car-audio-dsp.html | 2 (comercial) | não | arquivo RTA do REW ou do celular |
| JV-S023 | Audison — ACCORDO: https://audison.com/accordo/ | 2 | não | EQ, atrasos, níveis; meta de fase |
| JV-S024 | Audison — manual do bit Drive e FAQ do ACCORDO: https://audison.zendesk.com/hc/en-gb/articles/35741332904465-bit-Drive-User-manual e https://audison.zendesk.com/hc/en-gb/articles/26525819983377-ACCORDO-FAQ-FOR-BIT-DRIVE-2-0 | 2 | não | microfone USB, aparelhos compatíveis, “Nível Três” |
| JV-S025 | Audison — bit Drive 3.1: https://audison.com/bit-drive-3-1/ | 2 | não | ACCORDO 2.0: ruído de fundo, nível de teste por alto-falante |
| JV-S026 | Audiotec Fischer — AMI Tuning Kit: https://www.audiotec-fischer.de/en/accessories/ami-tuning-kit | 2 | não | AMI + microfone; compatibilidade com ATM |
| JV-S027 | Manual do MTK1 (cópia de terceiros): https://manuals.plus/m/f0028943c8e2671529609a76770e6902080d5d4aa893b0e951835aefc26bd31d | 2 (cópia) | não | curva “ATF Reference”; curva plana não recomendada para carro |

A comparação entre ferramentas que usa essas fontes está em [`comparacao-ferramentas.md`](comparacao-ferramentas.md).

Fontes técnicas de engenharia (literatura de filtros, crossovers, acústica de habitáculo) e fichas
técnicas dos equipamentos do Focus ainda **não** foram registradas: entram nas specs das features que
delas dependem.
