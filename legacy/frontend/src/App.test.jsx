import React from 'react';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {afterEach, beforeEach, expect, test, vi} from 'vitest';
import App from './App';

beforeEach(() => {
  Object.defineProperty(Element.prototype, 'getAnimations', {configurable: true, value: () => []});
});
afterEach(() => {cleanup(); localStorage.removeItem('rollcall.sidebarZoom'); delete Element.prototype.getAnimations; vi.unstubAllGlobals();});

function online(url) {
  return {ok: true, json: async () => url === '/api/documents' ? {documents: []} :
    {status: 'ok', counts_are_placeholders: true, categories: []}};
}

test('opens the Rollcall dashboard with real connectivity and unpublished inventory counts', async () => {
  vi.stubGlobal('fetch', vi.fn(async url => online(url)));
  render(<App/>);
  expect(screen.getByRole('heading', {name: 'Dashboard'})).toBeInTheDocument();
  expect(screen.getByRole('navigation', {name: 'Rollcall navigation'})).toBeInTheDocument();
  expect(screen.queryByText('Tire & wheel storage')).not.toBeInTheDocument();
  expect(screen.getByRole('heading', {name: 'Inventory status'})).toBeInTheDocument();
  expect(screen.getAllByText('—')).toHaveLength(3);
  expect(await screen.findByText('PostgreSQL: Connected')).toBeInTheDocument();
});

test('reports failure and refresh recovers', async () => {
  const fetchMock = vi.fn().mockRejectedValue(new Error('offline'));
  vi.stubGlobal('fetch', fetchMock);
  render(<App/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('Dashboard unavailable');
  await waitFor(() => expect(screen.getByRole('button', {name: 'Refresh status'})).toBeEnabled());
  fetchMock.mockImplementation(async url => online(url));
  fireEvent.click(screen.getByRole('button', {name: 'Refresh status'}));
  await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
});

test('uploads from Dashboard and opens Corrections without an upload control', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url, options) => options?.method === 'POST'
    ? {ok: true, json: async () => ({id: 'sample', filename: 'rehearsal.pdf', pages: 1, fields: {}})}
    : online(url)));
  render(<App/>);
  const file = new File(['pdf'], 'rehearsal.pdf', {type: 'application/pdf'});
  const picker = screen.getByLabelText('Choose PDF');
  const openPicker = vi.spyOn(picker, 'click');
  fireEvent.click(screen.getByRole('button', {name: 'Choose PDF'}));
  expect(openPicker).toHaveBeenCalledOnce();
  fireEvent.change(picker, {target: {files: [file]}});
  expect(screen.getByText(file.name)).toBeInTheDocument();
  expect(screen.getByRole('heading', {name: 'Dashboard'})).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name: 'Upload PDF'}));
  expect(await screen.findByRole('heading', {name: 'Corrections', level: 1})).toBeInTheDocument();
  expect(screen.queryByLabelText('Choose PDF')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name: /Back to corrections/}));
  expect(screen.queryByRole('button', {name: 'Upload PDF'})).not.toBeInTheDocument();
  expect(screen.queryByRole('button', {name: /Back to dashboard/})).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name: 'Dashboard'}));
  expect(screen.getByRole('heading', {name: 'Dashboard'})).toBeInTheDocument();
});

test('inventory navigation loads an empty inventory from the server', async () => {
  vi.stubGlobal('fetch', vi.fn(async url => url === '/api/inventory'
    ? {ok: true, json: async () => ({sets: [], counts: {active: 0, due: 0, overdue: 0}})}
    : online(url)));
  render(<App/>);
  fireEvent.click(screen.getByRole('button', {name: 'Inventory'}));
  expect(screen.getByRole('heading', {name: 'Inventory', level: 1})).toBeInTheDocument();
  expect(await screen.findByText('No sets in this view.')).toBeInTheDocument();
});

test('customer profile keeps the selected mockup tab when returning from a set', async () => {
  const set = {id:'set-1', customer_id:'riley', customer:'Riley Bennett', sort_name:'Bennett, Riley',
    name:'Bridgestone Blizzak', tire_size:'225/65R17', kind:'tires', status:'Current', location:'A', due_on:'2027-05-12',
    notes:'Inspect tire wear before next installation.', lug_nuts:true};
  vi.stubGlobal('fetch', vi.fn(async (url, options) => {
    if (url === '/api/inventory/sets/set-1/accessories/lug_nuts' && options?.method === 'PATCH') {
      const {present} = JSON.parse(options.body);
      set.lug_nuts = present;
      return {ok:true, json:async () => ({present})};
    }
    const data = {
      '/api/inventory': {sets:[set], counts:{active:1, due:0, overdue:0}},
      '/api/inventory/customers/riley': {name:'Riley Bennett', phone:'312-555-0148',
        email:'riley.bennett@example.com', sets:[set], vehicles:[],
        history:[{occurred_on:'2026-11-01', description:'RO 247810 · New storage'}]},
      '/api/inventory/sets/set-1': set,
    }[url];
    return data ? {ok:true, json:async () => data} : online(url);
  }));
  render(<App/>);
  fireEvent.click(screen.getByRole('button', {name:'Inventory'}));
  fireEvent.click(await screen.findByRole('button', {name:'Bennett, Riley'}));
  const preview = screen.getByRole('region', {name:'Riley Bennett vehicles and stored sets'});
  fireEvent.click(screen.getByRole('button', {name:/Unassigned/}));
  expect(preview).toHaveTextContent('Tires only');
  fireEvent.click(screen.getByRole('button', {name:/Open Bridgestone/}));
  await screen.findByRole('heading', {name:'Bridgestone Blizzak'});
  expect(await screen.findByRole('link', {name:'(312) 555-0148'})).toHaveAttribute('href', 'tel:312-555-0148');
  expect(screen.getByRole('button', {name:'Copy email: riley.bennett@example.com'})).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name:'Back to Inventory'}));
  expect(await screen.findByRole('button', {name:/Unassigned/})).toHaveAttribute('aria-expanded', 'true');
  fireEvent.click(screen.getByRole('button', {name:/Open profile/}));
  fireEvent.click(await screen.findByRole('tab', {name:/Unassigned/}));
  expect(screen.getByText('Due May 12, 2027')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name:/Open Bridgestone/}));
  await screen.findByRole('heading', {name:'Bridgestone Blizzak'});
  expect(screen.getByText('In storage')).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', {name:'Lug nuts: Yes'}));
  expect(await screen.findByRole('button', {name:'Lug nuts: No'})).toHaveAttribute('aria-pressed','false');
  expect(screen.getByRole('textbox', {name:'Notes for this stored set'})).toHaveValue(set.notes);
  expect(screen.getByRole('button', {name:'Remove'})).toBeDisabled();
  fireEvent.click(screen.getByRole('button', {name:/Customer profile/}));
  expect(await screen.findByRole('tab', {name:/Unassigned/, selected:true})).toBeInTheDocument();
  expect(screen.queryByText('RO 247810 · New storage')).not.toBeInTheDocument();
  expect(screen.queryByRole('tab', {name:'Customer history'})).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('tab', {name:/Vehicles/}));
  expect(screen.getByRole('region', {name:'Customer history'})).toHaveTextContent('RO 247810 · New storage');
});

test('database HTTP error is shown as unavailable', async () => {
  vi.stubGlobal('fetch', vi.fn(async url => ({...online(url), ok: !url.endsWith('/db')})));
  render(<App/>);
  expect(await screen.findByText('PostgreSQL: Unavailable')).toBeInTheDocument();
});

test('folds out the existing sidebar and closes it after navigation or Escape', () => {
  vi.stubGlobal('fetch', vi.fn(async url => online(url)));
  render(<App/>);
  const toggle = screen.getByRole('button', {name: 'Expand sidebar'});
  const sidebar = screen.getByRole('complementary');
  fireEvent.click(toggle);
  expect(toggle).toHaveAttribute('aria-expanded', 'true');
  expect(sidebar).toHaveAttribute('data-expanded', 'true');
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  fireEvent.keyDown(toggle, {key: 'Escape'});
  expect(toggle).toHaveAttribute('aria-expanded', 'false');
  fireEvent.click(toggle);
  fireEvent.click(screen.getByRole('button', {name: 'Inventory'}));
  expect(toggle).toHaveAttribute('aria-expanded', 'false');
  expect(screen.getByRole('heading', {name: 'Inventory'})).toBeInTheDocument();
});

test('Ctrl-wheel over the sidebar scales the whole workspace and clamps at 100–300%', () => {
  vi.stubGlobal('fetch', vi.fn(async url => online(url)));
  const app = render(<App/>);
  let sidebar = screen.getByRole('complementary');
  const layout = document.body;
  fireEvent.wheel(screen.getByRole('main'), {ctrlKey: true, deltaY: -100});
  fireEvent.wheel(sidebar, {deltaY: -100});
  expect(layout.style.zoom).toBe('1');
  fireEvent.wheel(sidebar, {ctrlKey: true, deltaY: -100});
  expect(layout.style.zoom).toBe('1.1');
  app.unmount();
  render(<App/>);
  expect(layout.style.zoom).toBe('1.1');
  sidebar = screen.getByRole('complementary');
  for (let index = 0; index < 25; index++) fireEvent.wheel(sidebar, {ctrlKey: true, deltaY: -100});
  expect(layout.style.zoom).toBe('3');
  for (let index = 0; index < 25; index++) fireEvent.wheel(sidebar, {ctrlKey: true, deltaY: 100});
  expect(layout.style.zoom).toBe('1');
});
