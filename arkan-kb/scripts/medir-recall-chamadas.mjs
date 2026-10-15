// Medição (Fase B, passo 1): classifica call-sites para estimar o ganho do TypeChecker
// vs. o name-matching atual. Não modifica nada. Uso: node scripts/medir-recall-chamadas.mjs
import ts from "typescript"
import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import Database from "better-sqlite3"

const raiz = resolve(process.cwd(), "..") // raiz do projeto indexado (script roda em arkan-kb/)
const db = new Database(resolve(raiz, ".arkan-kb/index.db"), { readonly: true })
const arquivos = db
  .prepare("SELECT DISTINCT file_path FROM nodes WHERE label='File' AND file_path LIKE '%.ts%'")
  .all()
  .map((r) => r.file_path)

const cat = {
  sameFileLocal: 0,   // foo() definido no mesmo arquivo (já resolvido hoje, conf 0.95)
  importado: 0,       // foo() onde foo é import → TypeChecker resolve exato; name-matching chuta
  membroRpcTask: 0,   // .rpc("x") / .task(...) dispatch dinâmico → TypeChecker NÃO resolve
  membroOutro: 0,     // a.b() genérico → TypeChecker resolve via tipo (difícil); hoje chuta
  globalBuiltin: 0,   // identifier não-local não-importado (setTimeout, etc.)
  totalCalls: 0,
  arquivos: 0,
}

for (const fp of arquivos) {
  let conteudo
  try { conteudo = readFileSync(resolve(raiz, fp), "utf8") } catch { continue }
  cat.arquivos++
  const sf = ts.createSourceFile(fp, conteudo, ts.ScriptTarget.Latest, true,
    fp.endsWith("x") ? ts.ScriptKind.TSX : ts.ScriptKind.TS)

  const importados = new Set()
  const locais = new Set()
  // coletar imports e declarações top-level
  sf.forEachChild((n) => {
    if (ts.isImportDeclaration(n) && n.importClause) {
      if (n.importClause.name) importados.add(n.importClause.name.text)
      const nb = n.importClause.namedBindings
      if (nb && ts.isNamedImports(nb)) nb.elements.forEach((e) => importados.add(e.name.text))
      if (nb && ts.isNamespaceImport(nb)) importados.add(nb.name.text)
    }
    if (ts.isFunctionDeclaration(n) && n.name) locais.add(n.name.text)
    if (ts.isVariableStatement(n)) {
      for (const d of n.declarationList.declarations)
        if (ts.isIdentifier(d.name)) locais.add(d.name.text)
    }
    if (ts.isClassDeclaration(n) && n.name) locais.add(n.name.text)
  })

  const visit = (node) => {
    if (ts.isCallExpression(node)) {
      cat.totalCalls++
      const e = node.expression
      if (ts.isIdentifier(e)) {
        if (locais.has(e.text)) cat.sameFileLocal++
        else if (importados.has(e.text)) cat.importado++
        else cat.globalBuiltin++
      } else if (ts.isPropertyAccessExpression(e)) {
        if (e.name.text === "rpc" || e.name.text === "task" || e.name.text === "trigger") {
          cat.membroRpcTask++
        } else {
          // se a raiz do acesso é um import (ns.foo()), TypeChecker resolve
          let raizAcesso = e.expression
          while (ts.isPropertyAccessExpression(raizAcesso)) raizAcesso = raizAcesso.expression
          if (ts.isIdentifier(raizAcesso) && importados.has(raizAcesso.text)) cat.importado++
          else cat.membroOutro++
        }
      }
    }
    ts.forEachChild(node, visit)
  }
  visit(sf)
}

const t = cat.totalCalls
const pct = (n) => `${n} (${Math.round(100 * n / t)}%)`
console.log(`Arquivos analisados: ${cat.arquivos}  |  call-sites: ${t}\n`)
console.log(`same-file local (já resolvido hoje):      ${pct(cat.sameFileLocal)}`)
console.log(`importado (TypeChecker resolve EXATO):    ${pct(cat.importado)}`)
console.log(`.rpc/.task/.trigger (dispatch dinâmico):  ${pct(cat.membroRpcTask)}  ← TypeChecker NÃO ajuda`)
console.log(`a.b() genérico (TypeChecker via tipo):    ${pct(cat.membroOutro)}`)
console.log(`global/builtin (setTimeout, etc.):        ${pct(cat.globalBuiltin)}`)
db.close()
