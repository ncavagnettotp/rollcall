import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {Alert, Button, Card, Disclosure, Input, Link, SearchField, Tabs, TextArea} from '@heroui/react';
import tireIcon from '../../docs/rollcall/assets/tire-user.png';
import wheelIcon from '../../docs/rollcall/assets/wheel-replacement.png';
import tireStackIcon from '../../docs/rollcall/assets/tire-stack-simple.svg?no-inline';
import './Inventory.css';
import BackButton from './BackButton';
import {request} from './DocumentReview';

const types = [['tire-wheel', 'Tires and wheels'], ['tires', 'Tires only'], ['wheels', 'Wheels only']];
const inStorage = set => set.status !== 'Removed';
const shortDate = new Intl.DateTimeFormat('en-US', {month:'2-digit', day:'2-digit', year:'numeric', timeZone:'UTC'});
const longDate = new Intl.DateTimeFormat('en-US', {month:'long', day:'numeric', year:'numeric', timeZone:'UTC'});
const historyDate = new Intl.DateTimeFormat('en-US', {month:'long', day:'numeric', timeZone:'UTC'});
const priorityDate = new Intl.DateTimeFormat('en-US', {month:'short', day:'numeric', timeZone:'UTC'});

function ProfileIcon({type}) {
  if (type === 'vehicles') return <span className="inventory-profile-icon inventory-car-icon" aria-hidden="true"/>;
  if (type === 'stored') return <span className="inventory-profile-icon inventory-stack-icon" style={{maskImage:`url(${tireStackIcon})`}} aria-hidden="true"/>;
  const paths = {
    phone:'M7 3H4a1 1 0 0 0-1 1c0 9.4 7.6 17 17 17a1 1 0 0 0 1-1v-3l-5-2-2 2a15 15 0 0 1-7-7l2-2-2-5Z',
    email:'M4 6h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1Zm0 2 8 6 8-6',
    unassigned:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1.2-1.5 2.5m0 3.5h.01',
  };
  return <svg className="inventory-profile-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[type]}/></svg>;
}

function CustomerContact({customer}) {
  const [feedback, setFeedback] = useState('');
  const digits = customer.phone?.replace(/\D/g, '');
  const phone = digits?.length === 10 ? `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}` : customer.phone;
  async function copyEmail() {
    try {await navigator.clipboard.writeText(customer.email); setFeedback('Email copied.');}
    catch {setFeedback('Could not copy email.');}
  }
  return <div className="inventory-contact">
    {phone && <Link href={`tel:${customer.phone}`}><ProfileIcon type="phone"/>{phone}</Link>}
    {customer.email && <Button variant="ghost" aria-label={`Copy email: ${customer.email}`} onPress={copyEmail}>
      <ProfileIcon type="email"/><span>{customer.email}</span>
    </Button>}
    <span className="inventory-contact-feedback" role="status">{feedback}</span>
  </div>;
}

function useInventoryRead(path, delay = 0) {
  const [result, setResult] = useState(null);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const response = await fetch(path, {signal: AbortSignal.any([controller.signal, AbortSignal.timeout(10000)])});
        if (!response.ok) throw new Error('Inventory request failed');
        const data = await response.json();
        if (!controller.signal.aborted) setResult({path, attempt, data});
      } catch {
        if (!controller.signal.aborted) setResult({path, attempt, error: true});
      }
    }, delay);
    return () => {clearTimeout(timer); controller.abort();};
  }, [path, delay, attempt]);
  const current = result?.path === path && result.attempt === attempt ? result : null;
  return {data:current?.data, error:current?.error, retry:() => setAttempt(value => value + 1)};
}

function SetIcons({kind}) {
  return <span className="inventory-set-icons" role="img" aria-label={types.find(([key]) => key === kind)?.[1]}>
    {kind !== 'wheels' && <img src={tireIcon} alt=""/>}
    {kind !== 'tires' && <img src={wheelIcon} alt="" className="inventory-wheel"/>}
  </span>;
}

function SetTypeBadge({kind}) {
  return <span className="inventory-set-type">
    <span aria-hidden="true"><SetIcons kind={kind}/></span>
    {types.find(([key]) => key === kind)?.[1]}
  </span>;
}

function LoadState({error, retry}) {
  return error ? <Alert status="danger" role="alert"><Alert.Indicator/><Alert.Content>
    <Alert.Description>Inventory could not be loaded.</Alert.Description>
    <Button variant="secondary" onPress={retry}>Try again</Button>
  </Alert.Content></Alert> : <p role="status">Loading inventory…</p>;
}

function ProfileSets({sets, open, mode}) {
  return sets.length ? <ul className="inventory-profile-sets" data-mode={mode}>{sets.map(set => <li key={set.id}>
    <div className="inventory-profile-set-line">
      {mode === 'unassigned' && <span className="inventory-unassigned-icon"><ProfileIcon type="unassigned"/></span>}
      <Button variant="ghost" aria-label={`Open ${set.name}${set.tire_size ? ', ' + set.tire_size : ''}`} onPress={() => open('sets', set.id)}>
        {set.name}{set.tire_size && ` · ${set.tire_size}`}
      </Button>
      <span className="inventory-profile-icon-box"><SetIcons kind={set.kind}/></span>
      <span className="inventory-profile-due">
        {set.due_on ? `Due ${longDate.format(new Date(set.due_on))}` : 'Due date unknown'}
      </span>
    </div>
    {mode !== 'vehicles' && <p className="inventory-muted">{set.vehicle || 'No vehicle information'}</p>}
  </li>)}</ul> : <p>No sets in this view.</p>;
}

function CustomerProfile({customer, open, view, updateView}) {
  const selectedTab = view.tab ?? 'vehicles';
  const card = useRef(null);
  const active = customer.sets.filter(inStorage);
  const unassigned = active.filter(set => !set.vehicle_id);
  useEffect(() => {
    const strip = card.current.querySelector('.tabs__list-container__scroller');
    if (!strip) return;
    function scrollTabs(event) {
      if (event.ctrlKey || Math.abs(event.deltaX) >= Math.abs(event.deltaY)) return;
      const limit = strip.scrollWidth - strip.clientWidth;
      if (limit <= 1 || (event.deltaY < 0 ? strip.scrollLeft <= 1 : strip.scrollLeft >= limit - 1)) return;
      event.preventDefault();
      const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? strip.clientWidth : 1;
      strip.scrollLeft += event.deltaY * unit;
    }
    strip.addEventListener('wheel', scrollTabs, {passive:false});
    return () => strip.removeEventListener('wheel', scrollTabs);
  }, []);
  return <>
    <Card ref={card} className="rollcall-card inventory-profile-card">
      <Tabs selectedKey={selectedTab} onSelectionChange={tab => updateView({tab})} className="inventory-tabs inventory-profile-tabs">
        <Tabs.ListContainer><Tabs.List aria-label="Customer profile views">
          {[['vehicles','Vehicles',customer.vehicles.length], ['unassigned','Unassigned',unassigned.length], ['stored','All Stored Sets',active.length]].map(([id,label,count]) =>
            <Tabs.Tab key={id} id={id}>
              <ProfileIcon type={id}/><span className="inventory-tab-label">{label}<span className="inventory-count">{count}</span></span>
              <Tabs.Indicator/>
            </Tabs.Tab>)}
        </Tabs.List></Tabs.ListContainer>
        <Tabs.Panel id="vehicles">
          {customer.vehicles.length ? customer.vehicles.map(vehicle => <Disclosure key={vehicle.id} className="inventory-vehicle"
            isExpanded={view.vehicle === vehicle.id} onExpandedChange={expanded => updateView({vehicle:expanded ? vehicle.id : null})}>
            <Disclosure.Heading><Disclosure.Trigger><span className="inventory-vehicle-tile"><ProfileIcon type="vehicles"/></span>{vehicle.description}<Disclosure.Indicator/></Disclosure.Trigger></Disclosure.Heading>
            <Disclosure.Content><Disclosure.Body>
              <ProfileSets sets={active.filter(set => set.vehicle_id === vehicle.id)} open={open} mode="vehicles"/>
            </Disclosure.Body></Disclosure.Content>
          </Disclosure>) : <p>No vehicles assigned.</p>}
        </Tabs.Panel>
        <Tabs.Panel id="unassigned"><ProfileSets sets={unassigned} open={open} mode="unassigned"/></Tabs.Panel>
        <Tabs.Panel id="stored"><ProfileSets sets={active} open={open} mode="stored"/></Tabs.Panel>
      </Tabs>
    </Card>
    {selectedTab === 'vehicles' && <Card className="rollcall-card inventory-history">
      <h2 id="inventory-history-title">Customer history</h2>
      <section className="inventory-history-content" aria-labelledby="inventory-history-title" tabIndex={0}>
        {customer.history.length ? <ol>{customer.history.map(event => <li key={event.occurred_on + event.description}>
          <time dateTime={event.occurred_on}>{historyDate.format(new Date(event.occurred_on))}</time><span>{event.description}</span>
        </li>)}</ol> : <p>No history recorded.</p>}
      </section>
    </Card>}
  </>;
}

const detailPaths = {
  calendar:'M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2ZM7 2v6m10-6v6M3 11h18',
  pdf:'M14 2H5v20h14V7zM14 2v6h5M7 17c4-2 6-8 4-8-2 0 0 9 5 8 3-1-5-3-9 0Z',
  notes:'M5 3h14v14l-5 5H5zM14 22v-5h5M8 7h8m-8 4h8m-8 4h4',
};
const accessories = [['lug_nuts','Lug nuts'], ['center_caps','Center caps'], ['centering_rings','Centering rings']];

function DetailIcon({name}) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"
    strokeLinejoin="round" aria-hidden="true"><path d={detailPaths[name]}/></svg>;
}

function SetDetails({set}) {
  const date = set.removed_on || set.due_on;
  const [accessoryValues, setAccessoryValues] = useState({});
  const savingAccessories = useRef(new Set());
  const [accessoryError, setAccessoryError] = useState('');
  async function toggleAccessory(key, current) {
    if (savingAccessories.current.has(key)) return;
    const present = current !== true;
    savingAccessories.current.add(key);
    setAccessoryError('');
    setAccessoryValues(previous => ({...previous, [key]:present}));
    try {
      const result = await request(`/api/inventory/sets/${encodeURIComponent(set.id)}/accessories/${key}`, {
        method:'PATCH', headers:{'Content-Type':'application/json'}, body:JSON.stringify({present}),
      });
      setAccessoryValues(previous => ({...previous, [key]:result.present}));
    } catch {
      setAccessoryValues(previous => ({...previous, [key]:current}));
      setAccessoryError('Could not save the accessory. Try again.');
    } finally {
      savingAccessories.current.delete(key);
    }
  }
  return <>
    <Card className="rollcall-card inventory-set-header">
      <div className="inventory-set-identity"><h2>{set.name}</h2>{set.tire_size && <p>{set.tire_size}</p>}</div>
      <div className="inventory-set-meta">
        <span className="inventory-set-date"><DetailIcon name="calendar"/>{set.removed_on ? 'Removed' : 'Due'}
          {date ? <time dateTime={date}>{shortDate.format(new Date(date))}</time> : <strong>Unknown</strong>}
        </span>
        <span className="inventory-set-pill">{inStorage(set) ? 'In storage' : 'Removed'}</span>
      </div>
      <div className="inventory-set-tools">
        {set.document_id
          ? <Link className="inventory-set-pdf" aria-label="Open original PDF" href={`/api/documents/${set.document_id}/pdf`} target="_blank" rel="noreferrer"><DetailIcon name="pdf"/>PDF</Link>
          : <Button className="inventory-set-pdf" isDisabled title="No original PDF linked"><DetailIcon name="pdf"/>PDF</Button>}
        <Button variant="secondary" className="inventory-set-reassign" isDisabled>
          {set.vehicle_id ? 'Reassign vehicle' : 'Assign vehicle'}
        </Button>
      </div>
    </Card>
    <div className="inventory-detail-grid">
      <Card className="rollcall-card inventory-set-facts">
        <dl className="inventory-facts">
          <div className="inventory-fact-block"><dt><span className="inventory-fact-icon"><ProfileIcon type="vehicles"/></span>Vehicle</dt><dd>{set.vehicle || 'No vehicle assigned'}</dd></div>
          <div className="inventory-fact-block"><dt><span className="inventory-fact-icon"><img src={wheelIcon} alt=""/></span>Wheels</dt><dd>{set.wheels || 'Not provided'}</dd></div>
          <div className="inventory-fact-small"><dt>Accessories</dt><dd className="inventory-accessories">
            {accessories.map(([key,label]) => {
              const value = accessoryValues[key] ?? set[key];
              const state = value == null ? 'Unknown' : value ? 'Yes' : 'No';
              return <Button key={key} variant="ghost" isIconOnly className="inventory-accessory-toggle"
                aria-label={`${label}: ${state}`} title={`${label}: ${state}`} aria-pressed={value === true}
                isDisabled={!inStorage(set)} onPress={() => toggleAccessory(key, value)}>
                <span className="inventory-accessory" data-kind={key} data-state={state} aria-hidden="true"/>
              </Button>;
            })}
            {accessoryError && <span className="inventory-accessory-error" role="alert">{accessoryError}</span>}
          </dd></div>
          <div className="inventory-fact-small inventory-location"><dt>Location</dt><dd>
            <Input aria-label="Storage location" value={set.location || 'Not assigned'} readOnly/>
          </dd></div>
        </dl>
        <Button variant="secondary" className="inventory-set-remove inventory-set-outline" isDisabled>Remove</Button>
      </Card>
      <Card className="rollcall-card inventory-notes">
        <div className="inventory-note-heading"><h2>Notes</h2>
          <span className="inventory-note-icon" data-has-notes={!!set.notes?.trim()} role="img" aria-label={set.notes?.trim() ? 'Notes present' : 'No notes'}>
            <DetailIcon name="notes"/>
          </span>
        </div>
        <TextArea aria-label="Notes for this stored set" value={set.notes ?? ''} placeholder="No notes recorded." readOnly rows={5}/>
        <Button variant="secondary" className="inventory-set-outline" isDisabled>Save notes</Button>
      </Card>
    </div>
  </>;
}

function CustomerPreview({sets, open, expanded, setExpanded}) {
  const panel = useRef(null);
  const groups = Map.groupBy(sets, set => set.vehicle_id ?? null);
  const customer = sets[0];
  useEffect(() => {
    panel.current?.scrollIntoView?.({block:'nearest'});
  }, []);
  return <Card ref={panel} className="rollcall-card inventory-customer-preview">
    <header>
      <div><h3>{customer.customer}</h3><p>{groups.size - Number(groups.has(null))} vehicles · {sets.length} stored {sets.length === 1 ? 'set' : 'sets'}</p></div>
      <Button variant="secondary" className="inventory-open-profile" onPress={() => open('customers', customer.customer_id)}>Open profile ↗</Button>
    </header>
    <section className="inventory-preview-scroll" aria-label={`${customer.customer} vehicles and stored sets`} tabIndex={0}>
      <h4>Vehicles</h4>
      {[...groups].sort(([a], [b]) => Number(a === null) - Number(b === null)).map(([id, vehicleSets]) => {
        const key = id ?? 'unassigned';
        return <Disclosure key={key} className="inventory-preview-vehicle" isExpanded={expanded === key}
          onExpandedChange={value => setExpanded(value ? key : null)}>
          <Disclosure.Heading><Disclosure.Trigger>
            <span className="inventory-vehicle-tile"><ProfileIcon type={id ? 'vehicles' : 'unassigned'}/></span>
            <span>{id ? vehicleSets[0].vehicle : 'Unassigned'}</span>
            <span className="inventory-count">{vehicleSets.length}</span><Disclosure.Indicator/>
          </Disclosure.Trigger></Disclosure.Heading>
          <Disclosure.Content><Disclosure.Body>
            {vehicleSets.map(set => <Button key={set.id} variant="ghost" className="inventory-preview-set"
              aria-label={`Open ${set.name}${set.tire_size ? ', ' + set.tire_size : ''}`} onPress={() => open('sets', set.id)}>
              <span className="inventory-preview-set-name"><strong>{set.name}</strong>{set.tire_size && <small>{set.tire_size}</small>}</span>
              <SetTypeBadge kind={set.kind}/>
              <span aria-hidden="true">›</span>
            </Button>)}
          </Disclosure.Body></Disclosure.Content>
        </Disclosure>;
      })}
    </section>
  </Card>;
}

const priorities = [
  ['Overdue', 'Overdue'],
  ['Due soon', 'Due in the next 30 days'],
  ['Date unknown', 'Due date unknown'],
  ['Current', 'Current'],
];

function CustomerResults({sets, selected, onSelect, open, expanded, setExpanded}) {
  const customers = [...Map.groupBy(sets, set => set.customer_id)].map(([id, matching]) => ({
    id, matching, name: matching[0].sort_name,
    status: priorities.find(([status]) => matching.some(set => set.status === status))?.[0] ?? 'Current',
  }));
  const active = customers.find(customer => customer.id === selected);
  const counts = Map.groupBy(sets, set => set.status);
  return <div className="inventory-customer-results" data-selected={!!active}>
    <section className="inventory-priority" aria-labelledby="inventory-stored-title">
      <header><h2 id="inventory-stored-title">Stored sets</h2><span>{counts.get('Overdue')?.length ?? 0} overdue · {counts.get('Due soon')?.length ?? 0} due soon</span></header>
      <div className="inventory-priority-list">
        {priorities.map(([status, title]) => {
          const group = customers.filter(customer => customer.status === status);
          if (!group.length) return null;
          return <div key={status} className="inventory-priority-group">
            <h4>{title}</h4>
            <ul>{group.map(customer => {
              const urgent = status === 'Overdue' || status === 'Due soon';
              const matchingStatus = customer.matching.filter(set => set.status === status);
              const firstDue = urgent ? matchingStatus.map(set => set.due_on).filter(Boolean).sort()[0] : null;
              const count = urgent || status === 'Date unknown' ? matchingStatus.length : customer.matching.length;
              const expanded = customer.id === active?.id;
              return <li key={customer.id}>
                <Button variant="ghost" className="inventory-priority-row" aria-label={customer.name} aria-expanded={expanded}
                  onPress={() => onSelect(expanded ? null : customer.id)}>
                  <span className="inventory-priority-dot" data-status={status} aria-hidden="true"/>
                  <strong>{customer.name}</strong>
                  <span className="inventory-status" data-status={status}>{count} {status === 'Current' ? 'stored' : status.toLowerCase()}</span>
                  {firstDue && <time dateTime={firstDue}>Due {priorityDate.format(new Date(firstDue))}</time>}
                  <span className="inventory-priority-chevron" aria-hidden="true">›</span>
                </Button>
              </li>;
            })}</ul>
          </div>;
        })}
      </div>
    </section>
    {active && <CustomerPreview key={active.id} sets={active.matching} open={open} expanded={expanded} setExpanded={setExpanded}/>}
  </div>;
}

export default function Inventory() {
  const [query, setQuery] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [expandedPreviewVehicle, setExpandedPreviewVehicle] = useState(null);
  const [views, setViews] = useState([]);
  const workspace = useRef(null);
  const view = views.at(-1);
  useLayoutEffect(() => {
    workspace.current.scrollTop = 0;
  }, [view?.kind, view?.id]);
  const search = query.trim();
  const list = useInventoryRead(search ? `/api/inventory?q=${encodeURIComponent(search)}` : '/api/inventory', search ? 150 : 0);
  const detail = useInventoryRead(view ? `/api/inventory/${view.kind}/${encodeURIComponent(view.id)}` : null);
  const heading = view?.kind === 'customers' ? detail.data?.name || 'Customer profile' : view ? 'Set details' : 'Inventory';
  const profile = view?.kind === 'customers';
  const selectedSet = view?.kind === 'sets' ? detail.data : null;
  const setCustomer = useInventoryRead(selectedSet
    ? `/api/inventory/customers/${encodeURIComponent(selectedSet.customer_id)}` : null).data;
  const contact = profile ? detail.data : setCustomer;
  const hasContact = !!(contact?.phone || contact?.email);
  const fromInventoryList = views.length === 1 && selectedCustomer === selectedSet?.customer_id;
  const goBack = () => setViews(items => items.slice(0, -1));
  const backLabel = views.length === 1 ? 'Back to Inventory' : views.at(-2)?.kind === 'customers' ? 'Customer profile' : 'Back to set details';
  const backButton = <BackButton className={profile ? 'inventory-profile-back' : undefined} onPress={goBack}>{backLabel}</BackButton>;
  const layout = content => <>
    <header className="rollcall-header" data-customer-profile={profile || undefined}
      data-set-contact={!!selectedSet && hasContact || undefined}>
      <div>{profile && backButton}
        {selectedSet && <div className="inventory-set-breadcrumb">
          <Button variant="ghost" onPress={() => open('customers', selectedSet.customer_id)}>{selectedSet.customer}’s profile</Button>
          <span> / Stored set</span>
        </div>}
        <h1>{heading}</h1>
      </div>
      {hasContact && <CustomerContact key={view.id} customer={contact}/>}
    </header>
    <div className="rollcall-workspace" data-customer-profile={profile || undefined} ref={workspace}>{content}</div>
  </>;
  function open(kind, id) {
    setViews(previous => {
      const index = previous.findIndex(item => item.kind === kind && item.id === id);
      return index < 0 ? [...previous, {kind, id}] : previous.slice(0, index + 1);
    });
  }

  if (view) return layout(<section key={`${view.kind}-${view.id}`} className={profile ? 'inventory-detail inventory-profile' : 'inventory-detail inventory-set-detail'}
    data-profile-tab={profile ? view.tab ?? 'vehicles' : undefined}>
    {!profile && (selectedSet && !fromInventoryList
      ? <BackButton onPress={() => open('customers', selectedSet.customer_id)}>Customer profile</BackButton>
      : backButton)}
    {!detail.data ? <LoadState {...detail}/> : view.kind === 'customers'
      ? <CustomerProfile key={view.id} customer={detail.data} open={open} view={view}
        updateView={changes => setViews(items => [...items.slice(0, -1), {...items.at(-1), ...changes}])}/>
      : <div className="inventory-set-enter"><SetDetails set={detail.data}/></div>}
  </section>);

  const sets = (list.data?.sets ?? []).filter(inStorage);

  return layout(<section className="inventory-page">
    <Card className="rollcall-card inventory-search">
      <SearchField aria-label="Search inventory" value={query} onChange={setQuery}>
        <SearchField.Group><SearchField.SearchIcon/><SearchField.Input maxLength={160} placeholder="Search customer, VIN, tire size or model…"/><SearchField.ClearButton/></SearchField.Group>
      </SearchField>
    </Card>
    <Card className="rollcall-card inventory-results">
        {!sets.length && <h2>Stored sets</h2>}
        {!list.data ? <LoadState {...list}/> : sets.length === 0 ? <p>{search ? 'No sets match your search.' : 'No sets in this view.'}</p> : <>
          <CustomerResults sets={sets} selected={selectedCustomer}
            onSelect={id => {setSelectedCustomer(id); setExpandedPreviewVehicle(null);}}
            open={open}
            expanded={expandedPreviewVehicle} setExpanded={setExpandedPreviewVehicle}/>
          <p className="inventory-total" aria-live="polite">{sets.length} {sets.length === 1 ? 'set' : 'sets'}</p>
        </>}
    </Card>
  </section>);
}
