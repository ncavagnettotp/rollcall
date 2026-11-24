import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Button,Label,ListBox,SearchField,Select,Tabs} from '@heroui/react';

const otherSets = [
  {id:'brooks',customer:'Casey Brooks',vehicle:'2023 Ford Escape',name:'Nokian Hakkapeliitta',size:'225/60R18',type:'tires',status:'Current',section:'B',ro:'247812'},
  {id:'ellis',customer:'Jordan Ellis',vehicle:'2022 Mazda CX-5',name:'Michelin X-Ice Snow',size:'225/65R17',type:'tires',status:'Due soon',section:'C',ro:'247813'},
  {id:'morgan',customer:'Alex Morgan',vehicle:'2022 Subaru Outback',name:'Michelin X-Ice Snow',size:'225/60R18',type:'tire-wheel',status:'Current',section:'A',ro:'247814'},
  {id:'parker',customer:'Jamie Parker',vehicle:'2021 Toyota RAV4',name:'Bridgestone Blizzak',size:'225/65R17',type:'tires',status:'Due soon',section:'Not assigned',ro:'247815'},
  {id:'reed',customer:'Taylor Reed',vehicle:'2020 Honda CR-V',name:'Continental VikingContact',size:'235/60R18',type:'tire-wheel',status:'Overdue',section:'D',ro:'247816'},
  {id:'reed-previous',customer:'Taylor Reed',vehicle:'2020 Honda CR-V',name:'Continental VikingContact',size:'235/60R18',type:'tires',status:'Removed',section:'Not assigned',ro:'247801'},
];
const scopes = [['active','In storage'],['due','Due soon'],['overdue','Overdue'],['all','All sets']];
const types = [['all','All set types'],['tire-wheel','Tires and wheels'],['tires','Tires only'],['wheels','Wheels only']];
const compactSize = value=>value.replace(/[^a-z0-9]/gi,'').toLowerCase().replace(/r(?=\d+$)/,'');
const surnameFirst = name=>name.split(' ').reverse().join(', ');

function SetIcons({type}) {
  return <span className="shop-set-icons" role="img" aria-label={types.find(([id])=>id===type)?.[1]}>
    {type!=='wheels' && <img src="assets/tire-user.png" alt=""/>}
    {type!=='tires' && <img src="assets/wheel-replacement.png" alt=""/>}
  </span>;
}

function Inventory() {
  const [query,setQuery]=useState(''),[scope,setScope]=useState('active'),[type,setType]=useState('all');
  const [filters,setFilters]=useState(false),[ascending,setAscending]=useState(true);
  const [view,setView]=useState(null),[locations,setLocations]=useState(()=>document.getElementById('locations').checked);
  const [,refresh]=useState(0);
  useEffect(()=>{
    const toggle=document.getElementById('locations');
    const update=()=>setLocations(toggle.checked);
    const navigate=event=>{
      if(event.detail.screen!=='inventory')return;
      if(event.detail.inventoryScope){
        setScope(event.detail.inventoryScope);
        setQuery('');
        setType('all');
      }
      setView(null);
      refresh(value=>value+1);
    };
    toggle.addEventListener('change',update);
    window.addEventListener('rollcall:screen',navigate);
    return ()=>{
      toggle.removeEventListener('change',update);
      window.removeEventListener('rollcall:screen',navigate);
    };
  },[]);
  const sets=[...window.rollcallCustomerSets(),...otherSets];
  const scopeSets=key=>sets.filter(set=>key==='all'||(key==='active'&&set.status!=='Removed')||
    (key==='due'&&set.status==='Due soon')||(key==='overdue'&&set.status==='Overdue'));
  const search=query.trim().toLowerCase();
  const matches=scopeSets(scope).filter(set=>(type==='all'||set.type===type)&&(
    !search||[set.customer,surnameFirst(set.customer),set.vehicle,set.vin,set.name,set.size,set.ro].some(value=>value?.toLowerCase().includes(search))||
    (/^\d[\d/ .rx-]*$/i.test(search)&&compactSize(set.size).includes(compactSize(search)))
  )).sort((a,b)=>(ascending?1:-1)*surnameFirst(a.customer).localeCompare(surnameFirst(b.customer)));

  const openCustomer=set=>set.customer==='Riley Bennett'?window.showScreen('profile'):setView({customer:set.customer});
  const openSet=set=>set.customer==='Riley Bennett'?window.openSet(set.id):setView({set,customer:set.customer});
  if(view){
    const {set,customer}=view;
    return <section key={set?.id ?? customer} className={`card shop-inventory-detail${set?'':' shop-customer-enter'}`}>
      <Button variant="ghost" onPress={()=>setView(null)}>← Back to Inventory</Button>
      <h2>{set?set.name:customer}</h2>
      {set?<dl>
        <div><dt>Customer</dt><dd><Button variant="ghost" onPress={()=>openCustomer(set)}>{customer}</Button></dd></div>
        <div><dt>Vehicle</dt><dd>{set.vehicle}</dd></div>
        <div><dt>Tire size</dt><dd>{set.size}</dd></div>
        <div><dt>Set</dt><dd><SetIcons type={set.type}/></dd></div>
        <div><dt>Status</dt><dd>{set.status}</dd></div>
        {locations&&<div><dt>Location</dt><dd>{set.section}</dd></div>}
        <div><dt>RO</dt><dd>{set.ro}</dd></div>
      </dl>:<ul>{sets.filter(item=>item.customer===customer).map(item=><li key={item.id}>
        <Button variant="ghost" onPress={()=>openSet(item)}>{item.name} · {item.size} · {item.status}</Button>
      </li>)}</ul>}
    </section>;
  }

  return <div className="shop-inventory">
    <div className="card shop-inventory-search">
      <SearchField aria-label="Search inventory" value={query} onChange={setQuery}>
        <SearchField.Group><SearchField.SearchIcon/><SearchField.Input placeholder="Search customer, VIN, tire size or model…"/><SearchField.ClearButton/></SearchField.Group>
      </SearchField>
      <Button variant="secondary" onPress={()=>setFilters(value=>!value)} aria-expanded={filters} aria-controls="shop-inventory-filters">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="M3 4h18l-7 8v6l-4 2v-8z"/></svg>Filters
      </Button>
      <div id="shop-inventory-filters" hidden={!filters}>
        <Select value={type} onChange={key=>{if(key)setType(key);}}>
          <Label>Set type</Label><Select.Trigger><Select.Value/><Select.Indicator/></Select.Trigger>
          <Select.Popover><ListBox>{types.map(([id,label])=><ListBox.Item key={id} id={id} textValue={label}>{label}<ListBox.ItemIndicator/></ListBox.Item>)}</ListBox></Select.Popover>
        </Select>
      </div>
    </div>
    <Tabs selectedKey={scope} onSelectionChange={setScope} className="shop-inventory-tabs">
      <Tabs.List aria-label="Inventory status">
        {scopes.map(([key,label])=><Tabs.Tab key={key} id={key}>{label}{key!=='all'&&<span className={key}>{scopeSets(key).length}</span>}<Tabs.Indicator/></Tabs.Tab>)}
      </Tabs.List>
      {scopes.map(([key,label])=><Tabs.Panel key={key} id={key}>
        {scope===key&&<section className="card shop-inventory-results" aria-label={label}>
          <header><h2>{key==='all'?'All sets':'Stored sets'}</h2><span className="sample-label">Sample records</span></header>
          <div className="shop-inventory-table"><table>
            <thead><tr>
              <th scope="col" aria-sort={ascending?'ascending':'descending'}><Button variant="ghost" onPress={()=>setAscending(value=>!value)}>Customer {ascending?'↑':'↓'}</Button></th>
              <th scope="col">Vehicle</th><th scope="col">Tire info</th><th scope="col">Set</th>
              {locations&&<th scope="col">Location</th>}<th scope="col">Status</th><th scope="col" aria-label="Set details"/>
            </tr></thead>
            <tbody>{matches.map(set=><tr key={set.id}>
              <td><Button variant="ghost" onPress={()=>openCustomer(set)}>{surnameFirst(set.customer)}</Button></td>
              <td>{set.vehicle==='No vehicle information'?'No vehicle assigned':set.vehicle}</td>
              <td><strong>{set.name}</strong><br/>{set.size}</td>
              <td><SetIcons type={set.type}/></td>
              {locations&&<td>{set.section}</td>}
              <td><span className="shop-inventory-status" data-status={set.status}>{set.status}</span></td>
              <td><Button variant="ghost" isIconOnly aria-label={`Open ${set.name}, ${set.size}, ${set.customer}`} onPress={()=>openSet(set)}>›</Button></td>
            </tr>)}</tbody>
          </table></div>
          {!matches.length&&<p>No sets match your search.</p>}
          <p className="shop-inventory-count" aria-live="polite">{matches.length} {matches.length===1?'set':'sets'}</p>
        </section>}
      </Tabs.Panel>)}
    </Tabs>
  </div>;
}

const host=document.getElementById('shop-inventory-root');
if(host)createRoot(host).render(<Inventory/>);
