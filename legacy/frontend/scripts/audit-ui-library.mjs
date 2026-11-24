// Source-level guard: inspect JSX syntax and import provenance, not emitted DOM.
import {parse} from '@babel/parser';
import {readFileSync, readdirSync} from 'node:fs';
import {dirname, join, relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const project=join(dirname(fileURLToPath(import.meta.url)),'..');
const nativeControls=new Set(['button','input','select','option','textarea','details','summary','a','form','fieldset','label','legend','dialog','table']);
const widgetNames=new Set(['Button','Input','TextField','TextArea','Select','ListBox','Disclosure','Link','Card','Alert','Form','Fieldset','SearchField','Checkbox','Modal','Table','Tabs','Popover','Switch']);
const widgetRoles=new Set(['button','checkbox','combobox','listbox','option','radio','switch','dialog','textbox','slider','tab','tablist','menu','menuitem']);
function walk(node,visit) {
 if (!node||typeof node!=='object') return;
 if (Array.isArray(node)) {node.forEach(item=>walk(item,visit));return;}
 if (node.type) visit(node);
 for (const [key,value] of Object.entries(node)) if (!['loc','start','end'].includes(key)) walk(value,visit);
}
function rootName(node) {return node.type==='JSXMemberExpression'?rootName(node.object):node.name;}
export function inspect(source) {
 const ast=parse(source,{sourceType:'module',plugins:['jsx','typescript']});
 const imports=new Map(),issues=[],used=new Set();
 walk(ast,node=>{
  if (node.type==='ImportDeclaration') for (const specifier of node.specifiers) {
   imports.set(specifier.local.name,node.source.value);
   if (!['react','react-dom/client','@heroui/react'].includes(node.source.value)&&!node.source.value.startsWith('.')&&specifier.local.name[0]===specifier.local.name[0].toUpperCase())
    issues.push(`Unapproved component import ${specifier.local.name} from ${node.source.value}`);
  }
 });
 walk(ast,node=>{
  if (node.type!=='JSXOpeningElement') return;
  const name=rootName(node.name);
  if (nativeControls.has(name)) issues.push(`Line ${node.loc.start.line}: native <${name}> must use HeroUI`);
  if (/^[a-z]/.test(name)) for (const attribute of node.attributes) {
   if (attribute.type==='JSXAttribute'&&attribute.name.name==='role'&&widgetRoles.has(attribute.value?.value)) issues.push(`Line ${node.loc.start.line}: custom role=${attribute.value.value} widget must use HeroUI`);
   if (attribute.type==='JSXAttribute'&&['onClick','onPress'].includes(attribute.name.name)&&!nativeControls.has(name)) issues.push(`Line ${node.loc.start.line}: interactive <${name}> must use HeroUI`);
  }
  if (widgetNames.has(name)&&imports.get(name)!=='@heroui/react') issues.push(`Line ${node.loc.start.line}: ${name} is not imported from HeroUI`);
  if (imports.get(name)==='@heroui/react') used.add(name);
 });
 return {issues,components:[...used].sort()};
}
if (process.argv.includes('--self-test')) {
 assert(inspect('export const A=()=> <button>Save</button>').issues.length);
 assert(inspect('const Button=()=>null;export const A=()=> <Button/>').issues.length);
 assert(inspect('import {Button} from "other-ui";export const A=()=> <Button/>').issues.length);
 assert(inspect('export const A=()=> <div role="button" onClick={()=>{}}>Save</div>').issues.length);
 assert.deepEqual(inspect('import {Button as Save,Card} from "@heroui/react";export const A=()=> <main><Card><Save>Save</Save></Card></main>').issues,[]);
 console.log('PASS: UI audit rejects raw controls, lookalike components and foreign UI imports; accepts HeroUI composition.');
} else {
 const pkg=JSON.parse(readFileSync(join(project,'package.json'),'utf8'));
 const errors=[];
 for (const name of ['@heroui/react','@heroui/styles']) if (!/^\d+\.\d+\.\d+$/.test(pkg.dependencies?.[name]||'')) errors.push(`${name} must be installed at an exact pinned version`);
 const styles=readFileSync(join(project,'src/styles.css'),'utf8');
 if (!(styles.indexOf('@import "tailwindcss";')>=0&&styles.indexOf('@import "@heroui/styles";')>styles.indexOf('@import "tailwindcss";'))) errors.push('HeroUI styles must follow Tailwind import');
 function files(directory) {return readdirSync(directory,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?files(join(directory,entry.name)):[join(directory,entry.name)]);}
 const report=[];
 for (const file of files(join(project,'src')).filter(file=>/\.[jt]sx?$/.test(file)&&!/[.](?:test|spec)[.]/.test(file))) {
  const result=inspect(readFileSync(file,'utf8'));
  report.push({file:relative(project,file),components:result.components});
  errors.push(...result.issues.map(issue=>`${relative(project,file)}: ${issue}`));
 }
 for (const row of report) console.log(`${row.file}: ${row.components.join(', ')||'application composition; no controls'}`);
 if (errors.length) {console.error(errors.join('\n'));process.exitCode=1;}
 else console.log('PASS: HeroUI source/import audit; no raw or lookalike library-covered controls. Semantic layout, domain icons, and theme CSS are retained.');
}
