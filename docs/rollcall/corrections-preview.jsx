import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Button, TextField, Input, Label, TextArea, Select, ListBox, Tabs} from '@heroui/react';

const mobileLayout=document.documentElement.dataset.correctionsMobile==='true'||document.documentElement.dataset.correctionsMobilePreview==='true';

const initial = {customer:'Julian Ocampo',ro:'246408',vehicle:'2023 Chevrolet Tahoe',vin:'1GNSKNKT7PR330867',date:'2026-10-22',brand:'General',model:'G-Max',size:'305/35R24',wheels:'Black Asanti wheels',notes:'NEEDS TIRES REPLACED',action:'swap',outgoing:'',lug:'yes',caps:'yes',rings:'no'};
const actions=[['swap','Swap sets'],['renewal','Renew existing storage'],['storage','New storage'],['remove','Remove from storage'],['none','No storage activity']];
function PdfPages(){
  const [page,setPage]=useState(1),[previous,setPrevious]=useState(null),[direction,setDirection]=useState('next');
  const [zoom,setZoom]=useState(1),[fitWidth,setFitWidth]=useState(1);
  const [dragging,setDragging]=useState(false);
  const timer=useRef(),viewport=useRef(),currentZoom=useRef(1),wheelAnchor=useRef(null),drag=useRef(null);
  useEffect(()=>()=>clearTimeout(timer.current),[]);
  useLayoutEffect(()=>{
    currentZoom.current=zoom;
    const anchor=wheelAnchor.current,element=viewport.current;
    if(!anchor||!element)return;
    const bounds=element.getBoundingClientRect(),paper=element.querySelector('.pdf-page-track').getBoundingClientRect();
    element.scrollLeft+=paper.left+anchor.u*paper.width-(bounds.left+element.clientLeft+anchor.x);
    element.scrollTop+=paper.top+anchor.v*paper.height-(bounds.top+element.clientTop+anchor.y);
    wheelAnchor.current=null;
  },[zoom]);
  useEffect(()=>{
    const element=viewport.current;
    const onWheel=event=>{
      // Horizontal wheel input remains native; vertical wheel input zooms.
      if(!event.deltaY)return;
      event.preventDefault();
      if(drag.current)return;
      const pixels=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?element.clientHeight:1);
      const next=Math.max(1,Math.min(5,currentZoom.current*Math.exp(-pixels*.0015)));
      if(next===currentZoom.current)return;
      const bounds=element.getBoundingClientRect(),paper=element.querySelector('.pdf-page-track').getBoundingClientRect();
      wheelAnchor.current={u:Math.max(0,Math.min(1,(event.clientX-paper.left)/paper.width)),v:Math.max(0,Math.min(1,(event.clientY-paper.top)/paper.height)),x:event.clientX-bounds.left-element.clientLeft,y:event.clientY-bounds.top-element.clientTop};
      currentZoom.current=next;
      setZoom(next);
    };
    element.addEventListener('wheel',onWheel,{passive:false});
    return()=>element.removeEventListener('wheel',onWheel);
  },[]);
  useEffect(()=>{
    const element=viewport.current;
    const fit=()=>setFitWidth(Math.max(1,Math.min(element.clientWidth-16,(element.clientHeight-16)*612/792)));
    const observer=new ResizeObserver(fit);observer.observe(element);fit();
    return()=>observer.disconnect();
  },[]);
  const fitPage=()=>{setZoom(1);viewport.current.scrollTo(0,0);};
  const startDrag=event=>{
    if(event.button!==0||zoom<=1)return;
    const element=event.currentTarget;
    event.preventDefault();
    element.focus({preventScroll:true});
    element.setPointerCapture(event.pointerId);
    drag.current={id:event.pointerId,x:event.clientX,y:event.clientY,left:element.scrollLeft,top:element.scrollTop};
    setDragging(true);
  };
  const moveDrag=event=>{
    const start=drag.current;
    if(!start||start.id!==event.pointerId)return;
    event.currentTarget.scrollLeft=start.left+start.x-event.clientX;
    event.currentTarget.scrollTop=start.top+start.y-event.clientY;
  };
  const endDrag=event=>{
    if(!drag.current||drag.current.id!==event.pointerId)return;
    drag.current=null;setDragging(false);
    if(event.currentTarget.hasPointerCapture(event.pointerId))event.currentTarget.releasePointerCapture(event.pointerId);
  };
  const turn=delta=>{
    const next=page+delta;
    if(next<1||next>2||previous!==null)return;
    setDirection(delta>0?'next':'previous');
    if(!matchMedia('(prefers-reduced-motion: reduce)').matches){setPrevious(page);timer.current=setTimeout(()=>setPrevious(null),360);}
    setPage(next);
    viewport.current.scrollTo(0,0);
  };
  return <section className="card correction-source" aria-label="Original source document">
    <div className="correction-card-heading"><h3>Original PDF</h3><div className="pdf-pager"><Button size="sm" aria-label="Previous PDF page" isDisabled={page===1||previous!==null} onPress={()=>turn(-1)}>←</Button><small role="status" aria-live="polite">Page {page} of 2</small><Button size="sm" aria-label="Next PDF page" isDisabled={page===2||previous!==null} onPress={()=>turn(1)}>→</Button></div></div>
    <div className="pdf-zoom-toolbar" aria-label="PDF zoom"><Button size="sm" aria-label="Zoom out PDF" isDisabled={zoom<=1} onPress={()=>setZoom(value=>Math.max(1,value-.5))}>−</Button><Button size="sm" aria-label="Fit PDF page" onPress={fitPage}>Fit</Button><Button size="sm" aria-label="Zoom in PDF" isDisabled={zoom>=5} onPress={()=>setZoom(value=>Math.min(5,value+.5))}>+</Button><small>{Math.round(zoom*100)}%</small></div>
    <div className="pdf-page-viewport" ref={viewport} tabIndex={0} aria-label="PDF page, mouse wheel to zoom; click and drag to pan" data-pannable={zoom>1} data-dragging={dragging} onPointerDown={startDrag} onPointerMove={moveDrag} onPointerUp={endDrag} onPointerCancel={endDrag} onLostPointerCapture={endDrag}>
    <div className="pdf-page-track" style={{width:fitWidth*zoom}} data-direction={direction} data-turning={previous!==null}>
      {previous!==null&&<img className="pdf-page-outgoing" src={`assets/sample-pdf/swap-215798-${previous}.png`} alt="" aria-hidden="true"/>}
      <img key={page} className={previous!==null?'pdf-page-current pdf-page-incoming':'pdf-page-current'} src={`assets/sample-pdf/swap-215798-${page}.png`} alt={`Supplied invoice 215798, page ${page} of 2`} draggable="false"/>
    </div></div><p className="correction-hint">Scroll to zoom · Click and drag to pan · Fit resets</p>
  </section>;
}
function CorrectionPreview(){
  const [fields,setFields]=useState(initial),[draft,setDraft]=useState(initial),[editing,setEditing]=useState(false),[stage,setStage]=useState('queue'),[resolved,setResolved]=useState(false),[message,setMessage]=useState('');
  const [mobilePane,setMobilePane]=useState('review');
  useEffect(()=>{if(document.documentElement.dataset.correctionsMobilePreview==='true'){window.showScreen('corrections');setStage('review');}},[]);
  useEffect(()=>{
    const section=document.getElementById('corrections');
    document.querySelectorAll('aside button').forEach(button=>{
      const label=button.querySelector('span:not(.nav-badge)')?.textContent.trim();
      if(label){button.setAttribute('aria-label',label);button.title=label;}
    });
    const update=()=>{
      document.body.classList.toggle('correction-responsive-layout',!section.hidden);
      document.body.style.removeProperty('--correction-ui-scale');
      window.positionNavIndicator?.();
    };
    const observer=new MutationObserver(update);observer.observe(section,{attributes:true,attributeFilter:['hidden']});
    window.addEventListener('resize',update);update();
    return()=>{observer.disconnect();window.removeEventListener('resize',update);document.body.classList.remove('correction-responsive-layout');};
  },[]);
  const change=(key,value)=>setFields(old=>({...old,[key]:value}));
  const picker=(key,label,options,values=fields,onChange=change)=><Select className="correction-field" value={values[key]} onChange={value=>onChange(key,value)} fullWidth><Label>{label}</Label><Select.Trigger><Select.Value/><Select.Indicator/></Select.Trigger><Select.Popover><ListBox>{options.map(([id,text])=><ListBox.Item id={id} key={id} textValue={text}>{text}<ListBox.ItemIndicator/></ListBox.Item>)}</ListBox></Select.Popover></Select>;
  const field=(key,label,values=fields,onChange=change,type='text')=><TextField className="correction-field" value={values[key]} onChange={value=>onChange(key,value)}><Label>{label}</Label><Input type={type} fullWidth/></TextField>;
  const valid=fields.customer.trim()&&fields.ro.trim()&&/^\d{4}-\d{2}-\d{2}$/.test(fields.date)&&(['swap','renewal','remove'].includes(fields.action)?!!fields.outgoing:true);
  const summaries={swap:'Incoming set enters storage. Selected outgoing set leaves storage.',renewal:'Extend the selected storage period using its existing due date if early, or the printed document date if overdue.',storage:'Create an incoming storage listing without removing another set.',remove:'Remove the selected set from active storage and retain its history.',none:'Retain the document without creating a storage transaction.'};
  const draftChange=(key,value)=>setDraft(old=>({...old,[key]:value}));
  const startEdit=()=>{setDraft({...fields});setEditing(true);setMessage('');};
  return <div className={'correction-preview '+(stage==='review'?'is-review':'is-queue')} data-mobile-pane={mobilePane}>
    {stage==='queue'?<section className="card correction-queue"><h2>Corrections</h2><p className="muted">{resolved?'No unresolved sample issues.':'1 submission needs attention'}</p>{!resolved?<div className="correction-queue-row"><div><strong>{fields.customer}</strong><p>RO {fields.ro} · Review storage action</p><small>Demo correction workflow; this is not an actual issue flagged on the supplied invoice.</small></div><Button onPress={()=>{setStage('review');setMessage('');}}>Review →</Button></div>:<><p role="status">Sample correction resolved. No live inventory was changed.</p><Button onPress={()=>{setResolved(false);setFields({...initial});}}>Reset sample issue</Button></>}</section>:<>
      <Button className="correction-back" variant="ghost" onPress={()=>{setStage('queue');setEditing(false);}}>← Back to corrections</Button>
      <div className="correction-heading"><div><h2>Review correction</h2><strong>{fields.customer}</strong><p>RO {fields.ro} · {fields.vehicle||'No vehicle assigned'}</p></div><span className="sample-label">Sample preview</span></div>
      {mobileLayout&&<Tabs className="correction-mobile-view-tabs" selectedKey={mobilePane} onSelectionChange={setMobilePane}>
        <Tabs.ListContainer><Tabs.List aria-label="Correction workspace view">
          <Tabs.Tab id="review" aria-label="Review details">Review<Tabs.Indicator/></Tabs.Tab>
          <Tabs.Tab id="pdf" aria-label="Original PDF">PDF<Tabs.Indicator/></Tabs.Tab>
        </Tabs.List></Tabs.ListContainer>
      </Tabs>}
      <div className={'correction-columns'+(editing?' is-editing':'')}>
        <PdfPages/>
        <section className="card correction-review" aria-label="Correction details"><div className="correction-warning"><strong>⚠ Review storage action</strong><p>Demo correction workflow; this is not an actual issue flagged on the supplied invoice.</p></div><div className="correction-card-heading"><h3>Extracted details</h3><Button size="sm" variant="secondary" onPress={startEdit} isDisabled={editing}>Edit details →</Button></div><dl className="correction-summary">{[['Customer',fields.customer],['RO',fields.ro],['Source date',fields.date],['Tires',fields.brand+' '+fields.model],['Tire size',fields.size],['Wheels',fields.wheels]].map(([label,value])=><div key={label}><dt>{label}</dt><dd>{value||'Not provided'}</dd></div>)}</dl><h3>What should happen?</h3>{picker('action','Storage action',actions)}{['swap','renewal','remove'].includes(fields.action)&&picker('outgoing',fields.action==='swap'?'Coming out of storage':'Stored set',[['','Select a stored set…'],['pirelli','Example stored set A · Tahoe'],['nokian','Example stored set B · Tahoe']])}<div className="correction-proposal"><strong>Proposed change</strong><p>{summaries[fields.action]}</p></div><p className="correction-hint">{!valid?'Complete the customer, RO, source date and any required set selection.':'Review the proposed change before resolving.'}</p><Button className="correction-resolve" isDisabled={!valid||editing||resolved} onPress={()=>{setResolved(true);setMessage('Sample correction resolved. The proposed action would apply once; the original source and correction history would be retained. No live inventory was changed.');}}>Resolve correction</Button>{message&&<p role="status" className="correction-feedback">{message}</p>}</section>
        {editing&&<section className="card correction-editor" aria-label="Edit all details"><div className="correction-card-heading"><h3>Edit details</h3><Button size="sm" variant="ghost" onPress={()=>setEditing(false)}>Cancel</Button></div><p>Correct any field while keeping the original source in view.</p><div className="correction-editor-fields">{[['customer','Customer'],['ro','RO'],['vehicle','Vehicle'],['vin','VIN'],['date','Source date'],['brand','Tire brand'],['model','Tire model'],['size','Tire size'],['wheels','Wheel description']].map(([key,label])=><React.Fragment key={key}>{field(key,label,draft,draftChange,key==='date'?'date':'text')}</React.Fragment>)}{picker('action','Storage action',actions,draft,draftChange)}{['lug','caps','rings'].map((key,i)=><React.Fragment key={key}>{picker(key,['Lug nuts','Center caps','Centering rings'][i],[['unknown','Unknown'],['yes','Yes'],['no','No']],draft,draftChange)}</React.Fragment>)}<TextField className="correction-field" value={draft.notes} onChange={value=>draftChange('notes',value)}><Label>Notes</Label><TextArea rows={3}/></TextField></div><div className="correction-editor-actions"><Button onPress={()=>{setFields({...draft,outgoing:draft.action===fields.action?draft.outgoing:''});setEditing(false);setMessage('Details updated in this preview. Check the proposed change, then resolve.');}}>Apply corrections</Button><Button variant="secondary" onPress={()=>setEditing(false)}>Cancel</Button></div></section>}
      </div>
    </>}
    <p className="correction-hint">Supplied PDF · Demonstration review and stored-set choices · Edits reset on refresh · No live inventory connection</p>
  </div>;
}
const host=document.getElementById('corrections-root');
if(host)createRoot(host).render(<CorrectionPreview/>);
