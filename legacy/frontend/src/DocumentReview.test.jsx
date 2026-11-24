import React from 'react';
import {render, screen, fireEvent, waitFor, cleanup} from '@testing-library/react';
import {afterEach, beforeEach, expect, test, vi} from 'vitest';
import App from './App';

beforeEach(() => {
  Object.defineProperty(Element.prototype, 'getAnimations', {configurable: true, value: () => []});
});
afterEach(() => {
  cleanup();
  delete Element.prototype.getAnimations;
  vi.unstubAllGlobals();
});
const original = {document_type:'invoice', invoice_number:'INV-42', work_order_number:'42', customer_name:'Sample Customer', contact:'', vehicle:'2020 Sample Vehicle', vin:'', start_date:'2026-11-10', date_source:'Invoice Date', storage_description:'Winter set', notes:'', action:'storage', centering_rings:'unknown', lug_nuts:'unknown', center_caps:'unknown'};
const document = {id:'doc-42', filename:'invoice.pdf', pages:1, extracted:{...original}, fields:{...original}, warnings:['Verify the vehicle VIN.'], status:'needs_review', version:1, duplicate:false, pdf_url:'/api/documents/doc-42/pdf', created_at:'2026-11-10T12:00:00Z'};
function respond(data, status=200) {return {ok:status<400,status,json:async()=>data};}
async function openPage(handler) {
  vi.stubGlobal('fetch', vi.fn(async (url, options)=>{
    if (url.startsWith('/api/documents')) return handler(url, options);
    return respond(url.endsWith('dashboard')?{categories:[]}:{status:'ok'});
  }));
  render(<App/>);
  return screen.findByLabelText('Choose PDF');
}
async function upload(input, file=new File(['%PDF-1.7 sample'], 'invoice.pdf', {type:'application/pdf'})) {
  fireEvent.change(input, {target:{files:[file]}});
  fireEvent.click(screen.getByRole('button', {name:'Upload PDF'}));
}
async function editDetails() {
  fireEvent.click(await screen.findByRole('button', {name: /Edit details/}));
  return screen.findByLabelText('Customer');
}
test('uploads raw PDF and saves corrections without changing extracted evidence', async()=>{
  const requests=[];
  const input=await openPage(async(url, options)=>{
    if (!options?.method) return respond({documents:[]});
    requests.push(options);
    if (options.method==='POST') return respond(document);
    return respond({...document, fields:JSON.parse(options.body).fields, status:'reviewed', version:2});
  });
  await upload(input);
  expect(await screen.findByRole('region', {name: 'Original source document'})).toBeInTheDocument();
  expect(await editDetails()).toHaveValue('Sample Customer');
  expect(requests[0].body).toBeInstanceOf(File);
  expect(requests[0].headers['X-Filename']).toBe('invoice.pdf');
  fireEvent.change(screen.getByLabelText('Customer'), {target:{value:'Corrected Customer'}});
  const action=screen.getByRole('button',{name:/Suggested action/});
  fireEvent.keyDown(action,{key:'ArrowDown',code:'ArrowDown'});
  fireEvent.keyUp(action,{key:'ArrowDown',code:'ArrowDown'});
  fireEvent.click(await screen.findByRole('option',{name:'Retrieval'}));
  fireEvent.click(screen.getByRole('button', {name:'Save review'}));
  expect(await screen.findByText('Review saved. Storage records are unchanged.')).toBeInTheDocument();
  expect(screen.getByText('Review saved. Storage records are unchanged.').closest('.review-panel')).toBeInTheDocument();
  expect(JSON.parse(requests[1].body)).toMatchObject({version:1,status:'reviewed',fields:{customer_name:'Corrected Customer',action:'retrieval',lug_nuts:'unknown'}});
  fireEvent.click(screen.getByText('Original extracted values'));
  expect(screen.getByText('Sample Customer', {exact:true})).toBeInTheDocument();
  expect(screen.getByRole('link', {name:/View original PDF/})).toHaveAttribute('href','/api/documents/doc-42/pdf');
  await editDetails();
  fireEvent.change(screen.getByLabelText('Vehicle'), {target:{value:'Unsaved vehicle correction'}});
  expect(screen.queryByText('Review saved. Storage records are unchanged.')).not.toBeInTheDocument();
});
test('keeps edits on version conflict until employee explicitly reloads', async()=>{
  const input=await openPage(async(url, options)=>{
    if (options?.method==='POST') return respond(document);
    if (options?.method==='PATCH') return respond({detail:'internal path should never be shown'},409);
    if (url.endsWith('doc-42')) return respond({...document,version:2,fields:{...original,customer_name:'Newest revision'}});
    return respond({documents:[]});
  });
  await upload(input);
  fireEvent.change(await editDetails(),{target:{value:'My unsaved edit'}});
  fireEvent.click(screen.getByRole('button',{name:'Save review'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('changed since you opened');
  expect(screen.getByRole('alert').closest('.review-panel')).toBeInTheDocument();
  expect(screen.getByLabelText('Customer')).toHaveValue('My unsaved edit');
  fireEvent.click(screen.getByRole('button',{name:'Reload latest review'}));
  await waitFor(()=>expect(screen.getByLabelText('Customer')).toHaveValue('Newest revision'));
});
test('rejects oversized PDFs before upload and displays sanitized request errors', async()=>{
  const input=await openPage(async(url,options)=>options?.method?respond({detail:'secret backend exception'},500):respond({documents:[]}));
  await upload(input, {name:'large.pdf',type:'application/pdf',size:10*1024*1024+1});
  expect(await screen.findByRole('alert')).toHaveTextContent('10 MiB');
  await upload(input);
  await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent('Unable to upload'));
  expect(screen.queryByText(/secret backend/)).not.toBeInTheDocument();
});
test('keeps reviewed PDFs accessible outside the pending queue', async()=>{
  const reviewed = {...document, status:'reviewed'};
  await openPage(async url => respond(url.endsWith('doc-42') ? reviewed : {documents:[reviewed]}));
  fireEvent.click(screen.getByRole('button',{name:'Corrections'}));
  expect(await screen.findByText('No submissions need review.')).toBeInTheDocument();
  expect(screen.queryByRole('button',{name:/Check VIN/})).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:/Reviewed documents/}));
  fireEvent.click(await screen.findByRole('button',{name:/Check VIN/}));
  expect(await screen.findByRole('heading',{name:'Sample Customer'})).toBeInTheDocument();
});

test('reopens duplicate uploads and archived reviews with unknown accessory values', async()=>{
  await openPage(async(url,options)=>{
    if (options?.method==='POST') return respond({...document, duplicate:true});
    if (url.endsWith('doc-42')) return respond(document);
    return respond({documents:[{...document, warnings:[
      'Preliminary suggestion only. Review source details and the proposed start date before later storage actions.',
      ...document.warnings,
    ]}]});
  });
  fireEvent.click(screen.getByRole('button',{name:'Corrections'}));
  const row = await screen.findByRole('button',{name:'Check VIN Sample Customer · RO 42'});
  expect(row).not.toHaveTextContent('Verify the vehicle VIN.');
  expect(row).not.toHaveTextContent('invoice.pdf');
  expect(screen.queryByRole('button',{name:/Open invoice.pdf/})).not.toBeInTheDocument();
  fireEvent.click(row);
  expect(await screen.findByRole('heading',{name:'Issue'})).toBeInTheDocument();
  expect(screen.getByText('Verify the vehicle VIN.')).toBeVisible();
  expect(screen.getByRole('textbox',{name:'VIN'})).toBeVisible();
  expect(screen.queryByText('Extracted details')).not.toBeInTheDocument();
  expect(screen.queryByLabelText('Customer')).not.toBeInTheDocument();
  expect(await editDetails()).toHaveValue('Sample Customer');
  fireEvent.click(screen.getByRole('button', {name: /Back to corrections/}));
  fireEvent.click(screen.getByRole('button', {name: 'Dashboard'}));
  await upload(await screen.findByLabelText('Choose PDF'));
  expect(await screen.findByText(/already archived/)).toBeInTheDocument();
  await editDetails();
  fireEvent.click(screen.getByText('Accessories'));
  expect(screen.getByRole('button', {name:/Centering rings/})).toHaveTextContent('Unknown');
  expect(screen.getByRole('button', {name:/Lug nuts/})).toHaveTextContent('Unknown');
  expect(screen.getByRole('button', {name:/Center caps/})).toHaveTextContent('Unknown');
  const trigger=screen.getByRole('button', {name:/Lug nuts/});
  fireEvent.keyDown(trigger,{key:'ArrowDown',code:'ArrowDown'});
  fireEvent.keyUp(trigger,{key:'ArrowDown',code:'ArrowDown'});
  fireEvent.click(await screen.findByRole('option',{name:'Yes'}));
  await waitFor(()=>expect(trigger).toHaveTextContent('Yes'));
});

test('keeps the edit draft while switching between Review details and Original PDF', async () => {
  const input = await openPage(async (url, options) => options?.method === 'POST'
    ? respond(document) : respond({documents: []}));
  await upload(input);
  fireEvent.change(await editDetails(), {target: {value: 'Draft name'}});
  fireEvent.click(screen.getByRole('tab', {name: 'Original PDF'}));
  expect(screen.getByRole('tab', {name: 'Original PDF'})).toHaveAttribute('aria-selected', 'true');
  fireEvent.click(screen.getByRole('tab', {name: 'Review details'}));
  expect(screen.getByLabelText('Customer')).toHaveValue('Draft name');
});
