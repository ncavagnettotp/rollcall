import './inventory-mobile.jsx';
import './corrections-preview.jsx';
import './insights-preview.jsx';
import './shop-inventory.jsx';
import tireStack from './assets/tire-stack-simple.js';
import carImage from './assets/vehicle-car-data.js';
import React, {useEffect, useState, useId} from 'react';
import {createRoot} from 'react-dom/client';
import {createPortal} from 'react-dom';
import {Tabs, Accordion} from '@heroui/react';

function CarIcon({className = 'customer-tab-icon customer-car-image'}) {
  const id = useId().replace(/:/g, '');
  return <svg className={className} viewBox="0 100 360 160" aria-hidden="true"><defs><filter id={id+'-invert'} colorInterpolationFilters="sRGB"><feColorMatrix type="matrix" values="-1 0 0 0 1 0 -1 0 0 1 0 0 -1 0 1 0 0 0 1 0" /></filter><mask id={id+'-mask'} maskUnits="userSpaceOnUse" x="0" y="0" width="360" height="360" style={{maskType:'luminance'}}><image width="360" height="360" href={carImage} filter={'url(#'+id+'-invert)'} /></mask></defs><rect width="360" height="360" fill="currentColor" mask={'url(#'+id+'-mask)'} /></svg>;
}
function TabIcon({type}) {
  if (type === 'vehicles') return <CarIcon />;
  if (type === 'unassigned') return <svg className="customer-tab-icon unassigned-question" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 4 2c-1 .7-1.5 1.2-1.5 2.5"/><circle cx="12" cy="17" r=".8" fill="currentColor" stroke="none"/></svg>;
  return <svg className="customer-tab-icon tire-stack-icon" viewBox="0 0 32 42" aria-hidden="true" dangerouslySetInnerHTML={{__html: tireStack}} />;
}

function CustomerTabs() {
  const [selected, setSelected] = useState('vehicles-tab');
  const [unassigned, setUnassigned] = useState(1);
  useEffect(() => {
    const strip=document.querySelector('#customer-tabs .tabs__list-container__scroller');
    if(!strip)return;
    const list=strip.querySelector('[role="tablist"]');
    let frame=0,target=strip.scrollLeft,position=strip.scrollLeft,lastTime=0;
    const clamp=value=>Math.max(0,Math.min(strip.scrollWidth-strip.clientWidth,value));
    const cancel=()=>{cancelAnimationFrame(frame);frame=0;target=position=strip.scrollLeft;};
    const update=()=>{
      strip.style.setProperty('--tab-fade-left',strip.scrollLeft>1?'22px':'0px');
      strip.style.setProperty('--tab-fade-right',strip.scrollWidth-strip.clientWidth-strip.scrollLeft>1?'22px':'0px');
      if(!frame)target=position=strip.scrollLeft;
    };
    const animate=time=>{
      const elapsed=Math.min(64,Math.max(1,time-lastTime));lastTime=time;
      target=clamp(target);
      const remaining=target-position;
      // Keep fractional progress separately from the browser's rounded scroll position.
      if(Math.abs(remaining)<.25){strip.scrollLeft=target;frame=0;update();return;}
      position+=remaining*(1-Math.exp(-elapsed/55));
      strip.scrollLeft=position;
      frame=requestAnimationFrame(animate);
    };
    const wheel=event=>{
      if(event.ctrlKey||strip.scrollWidth<=strip.clientWidth+1)return;
      const delta=Math.abs(event.deltaX)>Math.abs(event.deltaY)?event.deltaX:event.deltaY;
      if(!delta)return;
      event.preventDefault();
      if(!frame)target=position=strip.scrollLeft;
      target=clamp(target+delta*(event.deltaMode===1?16:event.deltaMode===2?strip.clientWidth:1));
      if(matchMedia('(prefers-reduced-motion: reduce)').matches){cancelAnimationFrame(frame);frame=0;strip.scrollLeft=target;update();return;}
      if(!frame){lastTime=performance.now();frame=requestAnimationFrame(animate);}
    };
    strip.addEventListener('wheel',wheel,{passive:false});
    strip.addEventListener('scroll',update,{passive:true});
    strip.addEventListener('pointerdown',cancel);
    strip.addEventListener('keydown',cancel);
    strip.addEventListener('touchstart',cancel,{passive:true});
    const observer=new ResizeObserver(update);observer.observe(strip);if(list)observer.observe(list);
    update();
    return()=>{cancelAnimationFrame(frame);observer.disconnect();strip.removeEventListener('wheel',wheel);strip.removeEventListener('scroll',update);strip.removeEventListener('pointerdown',cancel);strip.removeEventListener('keydown',cancel);strip.removeEventListener('touchstart',cancel);};
  },[]);
  useEffect(() => {
    const update = event => setUnassigned(event.detail.unassigned);
    window.addEventListener('rollcall:profile-counts', update);
    return () => window.removeEventListener('rollcall:profile-counts', update);
  }, []);
  useEffect(() => {
    const selectedTab = document.querySelector('[data-profile-key="' + selected + '"]');
    const panelId = { 'vehicles-tab': 'vehicles-panel', 'unassigned-tab': 'unassigned-panel', 'stored-tab': 'stored-panel' }[selected];
    if (selectedTab && panelId) {
      document.getElementById(panelId).setAttribute('aria-labelledby', selectedTab.id);
      selectedTab.setAttribute('aria-controls', panelId);
    }
  }, [selected, unassigned]);
  const change = key => {
    setSelected(key);
    for (const [tab, panel] of Object.entries({'vehicles-tab':'vehicles-panel','unassigned-tab':'unassigned-panel','stored-tab':'stored-panel'})) {
      document.getElementById(panel).hidden = key !== tab;
    }
  };
  return <Tabs variant="primary" selectedKey={selected} onSelectionChange={change} className="customer-heroui-tabs">
    <Tabs.ListContainer>
      <Tabs.List aria-label="Customer profile views">
        <Tabs.Tab id="vehicles-tab" data-profile-key="vehicles-tab" aria-label="Vehicles (2)">
          <span className="customer-tab-face"><TabIcon type="vehicles" />Vehicles<span className="tab-count">2</span></span><Tabs.Indicator><span className="tab-panel-join" aria-hidden="true" /></Tabs.Indicator>
        </Tabs.Tab>
        <Tabs.Tab id="unassigned-tab" data-profile-key="unassigned-tab" aria-label={`Unassigned (${unassigned})`}>
          <span className="customer-tab-face"><TabIcon type="unassigned" />Unassigned<span className="tab-count">{unassigned}</span></span><Tabs.Indicator><span className="tab-panel-join" aria-hidden="true" /></Tabs.Indicator>
        </Tabs.Tab>
        <Tabs.Tab id="stored-tab" data-profile-key="stored-tab" className="all-sets-tab" aria-label="All Stored Sets (4)">
          <span className="customer-tab-face"><TabIcon type="stored" />All Stored Sets<span className="tab-count">4</span></span><Tabs.Indicator><span className="tab-panel-join" aria-hidden="true" /></Tabs.Indicator>
        </Tabs.Tab>
      </Tabs.List>
    </Tabs.ListContainer>
  </Tabs>;
}

const host = document.getElementById('customer-tabs');
function UnassignedRowIcons() {
  const readHosts = () => [...document.querySelectorAll('#unassigned-panel .unassigned-row-icon-host')];
  const [hosts, setHosts] = useState(readHosts);
  useEffect(() => {
    const update = () => setHosts(readHosts());
    window.addEventListener('rollcall:profile-counts', update);
    return () => window.removeEventListener('rollcall:profile-counts', update);
  }, []);
  return hosts.map((node, index) => createPortal(<span className="row-unassigned-icon" role="img" aria-label="No assigned vehicle"><TabIcon type="unassigned" /></span>, node, String(index)));
}
createRoot(host).render(<><CustomerTabs /><UnassignedRowIcons /></>);

// The stored-set list remains the sample's source of truth. HeroUI owns disclosure
// state, measured panel height and the accessible expansion/collapse behavior.
function VehicleGroups() {
  const readGroups = () => ['2021 Audi Q5', '2024 Subaru Outback'].map(vehicle => ({
    vehicle,
    rows: [...document.querySelectorAll('#stored-panel .row')]
      .filter(row => row.querySelector('p.muted')?.textContent.trim() === vehicle)
      .map(row => row.outerHTML).join(''),
  }));
  const [groups, setGroups] = useState(readGroups);
  useEffect(() => {
    const update = () => setGroups(readGroups());
    window.addEventListener('rollcall:profile-counts', update);
    return () => window.removeEventListener('rollcall:profile-counts', update);
  }, []);
  return <Accordion allowsMultipleExpanded className="vehicle-accordion" onClick={event => {
    const link = event.target.closest('[data-set]');
    if (link) {event.preventDefault(); window.openSet(link.dataset.set);}
  }}>
    {groups.map(({vehicle, rows}) => <Accordion.Item key={vehicle} id={vehicle} className="vehicle-group">
      <Accordion.Heading>
        <Accordion.Trigger>
          <CarIcon className="vehicle-heading-icon vehicle-heading-car" />
          <span>{vehicle}</span><Accordion.Indicator />
        </Accordion.Trigger>
      </Accordion.Heading>
      <Accordion.Panel><Accordion.Body><div className="rows" dangerouslySetInnerHTML={{__html: rows || '<p class="muted">No stored sets assigned.</p>'}} /></Accordion.Body></Accordion.Panel>
    </Accordion.Item>)}
  </Accordion>;
}
createRoot(document.getElementById('vehicle-accordion')).render(<VehicleGroups />);

createRoot(document.getElementById('detail-car-icon')).render(<CarIcon className="fact-vehicle-icon" />);
