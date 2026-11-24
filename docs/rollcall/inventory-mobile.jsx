import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Button,Modal} from '@heroui/react';

function InventoryNavigation(){
  const [screen,setScreen]=useState(()=>document.querySelector('.screen:not([hidden])')?.id||'profile'),[open,setOpen]=useState(false);
  const items=[...document.querySelectorAll('aside .nav button,aside .app-utilities button')].map(button=>({
    screen:button.dataset.screen,label:button.querySelector('span:not(.nav-badge)')?.textContent.trim(),disabled:button.disabled,icon:button.querySelector('svg')?.outerHTML||'',
  }));
  useEffect(()=>{
    const update=event=>{setScreen(event.detail.screen);setOpen(false);};
    const media=matchMedia('(max-width:1000px)');
    const resize=()=>{if(!media.matches)setOpen(false);};
    window.addEventListener('rollcall:screen',update);media.addEventListener('change',resize);
    if(document.documentElement.dataset.dashboardMobilePreview==='true')window.showScreen('dashboard');
    return()=>{window.removeEventListener('rollcall:screen',update);media.removeEventListener('change',resize);};
  },[]);
  const correctionConcept=(document.documentElement.dataset.correctionsMobile==='true'||document.documentElement.dataset.correctionsMobilePreview==='true')&&screen==='corrections';
  const {dashboardMobile,dashboardMobilePreview}=document.documentElement.dataset;
  const responsiveDashboard=(dashboardMobile==='true'||dashboardMobilePreview==='true')&&screen==='dashboard';
  if(!['inventory','profile','detail','insights'].includes(screen)&&!correctionConcept&&!responsiveDashboard)return null;
  return <Modal isOpen={open} onOpenChange={setOpen}>
    <Button className="inventory-menu-trigger" aria-label="Open full navigation" title="Open full navigation" onPress={()=>setOpen(true)}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
    </Button>
    <Modal.Backdrop className="inventory-menu-backdrop">
      <Modal.Container className="inventory-menu-container">
        <Modal.Dialog className="inventory-menu-dialog" aria-label="Full navigation">
          <Modal.Header className="inventory-menu-header">
            <div className="inventory-menu-brand"><img src="references/dashboard-style-target.png" alt="Rollcall"/></div>
            <Button className="inventory-menu-close" aria-label="Close navigation" onPress={()=>setOpen(false)}>×</Button>
          </Modal.Header>
          <Modal.Body className="inventory-menu-body">
            <nav className="inventory-menu-nav" aria-label="Full product navigation">{items.map(item=><Button key={item.label} isDisabled={item.disabled} className={(item.screen===screen||(['profile','detail'].includes(screen)&&item.screen==='inventory')||(screen==='detail'&&item.screen==='profile'))?'is-current':''} onPress={()=>{setOpen(false);if(item.screen)window.showScreen(item.screen);}}><span className="inventory-menu-icon" dangerouslySetInnerHTML={{__html:item.icon}}/><span>{item.label}</span></Button>)}</nav>
          </Modal.Body>
        </Modal.Dialog>
      </Modal.Container>
    </Modal.Backdrop>
  </Modal>;
}
const host=document.getElementById('inventory-menu-root');
if(host)createRoot(host).render(<InventoryNavigation/>);
