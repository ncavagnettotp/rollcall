import React, {useEffect, useRef, useState} from 'react';
import {Alert, Button, Card, Chip, Input} from '@heroui/react';
import DocumentReview, {request} from './DocumentReview';
import Inventory from './Inventory';
import brandImage from '../../docs/rollcall/references/dashboard-style-target.png';

const paths = {
  dashboard: 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
  inventory: 'M4 6c0-2 3.6-3 8-3s8 1 8 3-3.6 3-8 3-8-1-8-3Zm0 0v12c0 2 3.6 3 8 3s8-1 8-3V6M4 12c0 2 3.6 3 8 3s8-1 8-3',
  insights: 'M3 3v18h18M6 15l5-5 4 3 6-8m-5 0h5v5',
  corrections: 'm10.3 4.3-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-2.7l-8-14a2 2 0 0 0-3.4 0ZM12 9v5m0 3h.01',
  settings: 'M4 7h3m5 0h8M4 17h8m5 0h3M12 7a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Zm5 10a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z',
  calendar: 'M4 5h16v16H4zM8 3v4m8-4v4M4 10h16m-11 4h.01m5 0h.01',
  file: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8ZM14 2v6h6',
  menu: 'M4 6h16M4 12h16M4 18h16',
  close: 'M6 6l12 12M18 6 6 18',
};

const screens = {dashboard: 'Dashboard', inventory: 'Inventory', insights: 'Insights', corrections: 'Corrections', settings: 'Settings'};
const unavailable = {
  insights: 'Reports will be available when live storage records are connected.',
  settings: 'Shop-wide storage settings will be available with live inventory.',
};
const metrics = [
  {label: 'Total inventory', tone: 'blue', icon: 'inventory'},
  {label: 'Due soon', tone: 'amber', icon: 'calendar'},
  {label: 'Overdue', tone: 'red', icon: 'corrections'},
];

function Icon({name}) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={paths[name]}/>
    {name === 'file' && <path d="M12 18v-7m-3 3 3-3 3 3" stroke="#ff8900"/>}
  </svg>;
}

async function get(path) {
  const response = await fetch('/api/' + path, {signal: AbortSignal.timeout(6000)});
  if (!response.ok) throw new Error('Request failed');
  return response.json();
}

function Dashboard({onUploaded}) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState({api: 'Checking…', db: 'Checking…'});
  const [error, setError] = useState(false);
  const [busy, setBusy] = useState(true);
  const [dragging, setDragging] = useState(false);
  const [file, selectFile] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef(null);
  const uploadLock = useRef(false);
  const mounted = useRef(false);
  useEffect(() => {
    mounted.current = true;
    return () => {mounted.current = false;};
  }, []);
  function chooseFile(next) {
    if (uploadLock.current || !next) return;
    setUploadError('');
    selectFile(next);
  }
  async function upload() {
    if (!file || uploadLock.current) return;
    setUploadError('');
    if (file.size > 10 * 1024 * 1024) {setUploadError('Choose a PDF no larger than 10 MiB.'); return;}
    if (!/\.pdf$/i.test(file.name)) {setUploadError('Choose a PDF file.'); return;}
    uploadLock.current = true;
    setUploading(true);
    try {
      const document = await request('/api/documents', {method: 'POST',
        headers: {'Content-Type': 'application/pdf', 'X-Filename': encodeURIComponent(file.name)}, body: file});
      if (mounted.current) onUploaded(document);
    } catch (failure) {
      setUploadError(failure.status === 413 ? 'Choose a PDF no larger than 10 MiB.'
        : [400, 415, 422].includes(failure.status) ? 'This PDF could not be read. Choose a valid, unencrypted PDF.'
        : 'Unable to upload this PDF. Check the connection and try again.');
    } finally {
      uploadLock.current = false;
      setUploading(false);
    }
  }
  async function refresh() {
    setBusy(true);
    const [dashboard, api, db] = await Promise.allSettled([get('dashboard'), get('health'), get('health/db')]);
    setData(dashboard.status === 'fulfilled' ? dashboard.value : null);
    setError(dashboard.status !== 'fulfilled');
    setStatus({api: api.status === 'fulfilled' ? 'Online' : 'Unavailable', db: db.status === 'fulfilled' ? 'Connected' : 'Unavailable'});
    setBusy(false);
  }
  useEffect(() => {refresh();}, []);

  const counts = Object.fromEntries((data?.categories ?? []).map(item => [item.label, item.count]));
  const ready = !data?.counts_are_placeholders && [counts.Stored, counts['Due Soon'], counts.Overdue].every(Number.isFinite);
  const values = ready ? [counts.Stored + counts['Due Soon'] + counts.Overdue, counts['Due Soon'], counts.Overdue] : [];
  return <>
    {error && <Alert status="danger" role="alert"><Alert.Indicator/><Alert.Content><Alert.Description>Dashboard unavailable. Check the server connection, then refresh.</Alert.Description></Alert.Content></Alert>}
    <section className="rollcall-metrics" aria-label="Inventory totals" aria-busy={busy}>
      {metrics.map(({label, tone, icon}, index) => <Card key={label} className="rollcall-card rollcall-metric">
        <h2>{label}</h2><div className={'rollcall-metric-value ' + tone}><span>{values[index] ?? '—'}</span><Icon name={icon}/></div>
      </Card>)}
    </section>
    <div className="rollcall-panels">
      <Card className="rollcall-card rollcall-upload">
        <h2>Upload invoices</h2>
        <div className="rollcall-drop" data-dragging={dragging}
          onDragOver={event => {event.preventDefault(); setDragging(true);}}
          onDragLeave={() => setDragging(false)}
          onDrop={event => {event.preventDefault(); setDragging(false); chooseFile(event.dataTransfer.files[0]);}}>
          <Icon name="file"/>
          <h3><span className="rollcall-wide-copy">Drag &amp; drop invoices here</span><span className="rollcall-compact-copy">Upload a document</span></h3>
          <p>PDF invoices, authorizations &amp; work orders</p>
          <Input ref={fileInput} hidden type="file" accept="application/pdf,.pdf" aria-label="Choose PDF" disabled={uploading}
            onChange={event => { chooseFile(event.target.files?.[0]); event.target.value = ''; }}/>
          <Button type="button" variant="ghost" className="rollcall-pdf-picker" isDisabled={uploading}
            onPress={() => fileInput.current?.click()}>Choose PDF</Button>
          {file && <><p className="rollcall-file-name">{file.name}</p><Button variant="primary" isDisabled={uploading} onPress={upload}>
            {uploading ? 'Uploading…' : 'Upload PDF'}
          </Button></>}
        </div>
        {uploadError && <Alert role="alert" status="danger"><Alert.Indicator/><Alert.Content><Alert.Description>{uploadError}</Alert.Description></Alert.Content></Alert>}
        <p><strong>Planned workflow</strong> · Clear submissions update inventory. Ambiguous details need attention.</p>
      </Card>
      <Card className="rollcall-card rollcall-status">
        <h2>Inventory status</h2>
        <div className="rollcall-ring" aria-hidden="true"><Icon name="inventory"/></div>
        {ready ? <dl>{['Stored', 'Due Soon', 'Overdue'].map(label => <div key={label}><dt>{label}</dt><dd>{counts[label]}</dd></div>)}</dl>
          : <p>Status will appear when live inventory is connected.</p>}
      </Card>
    </div>
    <footer className="rollcall-footer">
      <section aria-label="System status" aria-live="polite">
        <Chip size="sm" variant="soft">API: {status.api}</Chip>
        <Chip size="sm" variant="soft">PostgreSQL: {status.db}</Chip>
      </section>
      <Button type="button" size="sm" variant="ghost" isDisabled={busy} onPress={refresh}>Refresh status</Button>
    </footer>
  </>;
}

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [menu, setMenu] = useState(false);
  const [zoom, setZoom] = useState(readSidebarZoom);
  const [windowScale, setWindowScale] = useState(1);
  const effectiveZoom = Math.min(3, windowScale * zoom / 100);
  const sidebar = useRef(null);
  const toggle = useRef(null);

  useEffect(() => {
    const element = sidebar.current;
    function zoomOnWheel(event) {
      if (!event.ctrlKey || event.deltaY === 0) return;
      event.preventDefault();
      setZoom(value => Math.max(100, Math.min(300, value - Math.sign(event.deltaY) * 10)));
    }
    element.addEventListener('wheel', zoomOnWheel, {passive: false});
    return () => element.removeEventListener('wheel', zoomOnWheel);
  }, []);

  useEffect(() => {
    function resize() {
      setWindowScale(Math.max(1, Math.min(2, window.innerWidth / 1600, window.innerHeight / 900)));
    }
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(zoomStorageKey, String(zoom));
    } catch {
      // The current zoom still works when preferences cannot be written.
    }
  }, [zoom]);

  useEffect(() => {
    const previousZoom = document.body.style.zoom;
    document.body.style.zoom = String(effectiveZoom);
    return () => {document.body.style.zoom = previousZoom;};
  }, [effectiveZoom]);

  function navigate(next, document = null) {
    setPage(next);
    setUploadedDocument(document);
    setMenu(false);
  }
  const navItems = Object.entries(screens).map(([key, label]) =>
    <Button key={key} variant="ghost" className="rollcall-nav-item" aria-label={label}
      aria-current={key === page ? 'page' : undefined} onPress={() => navigate(key)}>
      <Icon name={key}/><span>{label}</span>
    </Button>);

  return <div className="rollcall-scale" style={{'--rollcall-zoom': effectiveZoom}}><div className="rollcall-shell">
    <aside className="rollcall-sidebar" ref={sidebar} data-expanded={menu}
      onKeyDown={event => {
        if (event.key === 'Escape' && menu) {
          setMenu(false);
          toggle.current?.focus();
        }
      }}>
      <Button ref={toggle} className="rollcall-menu" variant="ghost"
        aria-label={menu ? 'Collapse sidebar' : 'Expand sidebar'}
        aria-expanded={menu} aria-controls="rollcall-navigation"
        onPress={() => setMenu(open => !open)}><Icon name={menu ? 'close' : 'menu'}/></Button>
      <div className="rollcall-brand"><img src={brandImage} alt="Rollcall"/></div>
      <nav id="rollcall-navigation" className="rollcall-nav" aria-label="Rollcall navigation">{navItems}</nav>
    </aside>
    <main className="rollcall-main" data-screen={page} onPointerDown={() => {if (menu) setMenu(false);}}>
      {page === 'inventory' ? <Inventory/> : <>
      <header className="rollcall-header"><h1>{screens[page]}</h1></header>
      <div className="rollcall-workspace">
        {page === 'dashboard' && <Dashboard onUploaded={document => navigate('corrections', document)}/>}
        {page === 'corrections' && <DocumentReview key={uploadedDocument?.id ?? 'queue'} initialDocument={uploadedDocument}/>}
        {unavailable[page] && <Card className="rollcall-card"><Card.Content>{unavailable[page]}</Card.Content></Card>}
      </div>
      </>}
    </main>
  </div></div>;
}
const zoomStorageKey = 'rollcall.sidebarZoom';

function readSidebarZoom() {
  try {
    const value = Number(localStorage.getItem(zoomStorageKey));
    if (Number.isInteger(value) && value >= 100 && value <= 300) return value;
  } catch {
    // Keep zoom usable when browser storage is unavailable.
  }
  return 100;
}
