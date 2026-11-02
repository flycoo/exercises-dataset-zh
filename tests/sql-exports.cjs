// 从页面提取实际使用的导出函数，供数据验证脚本执行。
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.join(__dirname, '..');
const result = {};
const exercises = JSON.parse(fs.readFileSync(path.join(root, 'data/exercises.zh-CN.json'), 'utf8'));
for (const page of ['index.html', 'setup.html']) {
  const html = fs.readFileSync(path.join(root, page), 'utf8');
  for (const [, script] of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
    new vm.Script(script, { filename: page });
  }
  const templates = html.match(/const DB_SQL = (\{[\s\S]*?\n {0,2}\});/)[1];
  const escape = html.match(/ {0,2}function escStr\([\s\S]*?\n {0,2}\}/)[0];
  const inserts = html.match(/ {0,2}function buildInserts\([\s\S]*?\n {0,2}\}(?=\s*(?:async )?function generateInsertSql)/)[0];
  const context = vm.createContext({ exercises });
  vm.runInContext(`const DB_SQL = ${templates}; ${escape}\n${inserts}\nthis.exports = Object.fromEntries(Object.entries(DB_SQL).map(([db, ddl]) => [db, {ddl, inserts: buildInserts(exercises, db)}]));`, context);
  result[page] = context.exports;
}
process.stdout.write(JSON.stringify(result));
