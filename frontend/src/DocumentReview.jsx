import React, {useEffect, useRef, useState} from 'react';
import {Alert, Button, Card, Chip, Disclosure, Fieldset, Form, Input, Label, ListBox, Select, Tabs, TextArea, TextField} from '@heroui/react';
import OriginalPdf from './OriginalPdf';
import BackButton from './BackButton';
import './DocumentReview.css';

const defaults = {document_type:'',invoice_number:'',work_order_number:'',customer_name:'',contact:'',vehicle:'',vin:'',start_date:'',date_source:'',storage_description:'',notes:'',action:'review_required',centering_rings:'unknown',lug_nuts:'unknown',center_caps:'unknown'};
const actions = [['review_required','Needs review'],['storage','Initial storage'],['swap','Swap'],['retrieval','Retrieval'],['renewal','Renewal'],['purchase_only','Purchase only']];
const preliminaryNotice = 'Preliminary suggestion only. Review source details and the proposed start date before later storage actions.';
const issueFields = [
  [/\bVIN\b/i, 'vin', 'VIN'],
  [/^Conflicting work order number\b/i, 'work_order_number', 'RO'],
  [/^Conflicting invoice number\b/i, 'invoice_number', 'Invoice number'],
  [/^(?:No reliable labeled source date|(?:Conflicting|Invalid) (?:Invoice|Authorization|Work Order) Date)/i, 'start_date', 'Source date', 'date'],
  [/^Conflicting lugs choices/i, 'lug_nuts', 'Lug nuts'],
  [/^Conflicting center caps choices/i, 'center_caps', 'Center caps'],
  [/^Conflicting center rings choices/i, 'centering_rings', 'Centering rings'],
];
const accessoryOptions = [['unknown','Unknown'],['yes','Yes'],['no','No']];
const documentIssues = document => (document?.warnings ?? []).filter(warning => warning !== preliminaryNotice);
const reviewLabel = document => document.status === 'reviewed' ? 'Reviewed document' : 'Review required';
const issueTitles = [
  [/\bVIN\b/i, 'Check VIN'],
  [/^Another source document shares/i, 'Shared RO'],
  [/^Historical seasons\/charges/i, 'Confirm renewal'],
  [/^Pre-invoice document/i, 'Final invoice needed'],
  [/^No readable embedded text/i, 'Review PDF manually'],
  [/^(?:No reliable labeled source date|(?:Conflicting|Invalid) (?:Invoice|Authorization|Work Order) Date)/i, 'Check source date'],
  [/^Conflicting work order number/i, 'Check RO'],
  [/^Conflicting invoice number/i, 'Check invoice number'],
  [/^Conflicting (?:lugs|center caps|center rings) choices/i, 'Check accessories'],
];
const issueTitle = document => {
  const titles = documentIssues(document).map(issue =>
    issueTitles.find(([pattern]) => pattern.test(issue))?.[1] ?? 'Review document');
  return [...new Set(titles)].join(' · ') || reviewLabel(document);
};
export async function request(url, options) {
  const response = await fetch(url, {...options,signal:AbortSignal.timeout(30000)});
  if (!response.ok) {const error=new Error('Request failed'); error.status=response.status; throw error;}
  return response.json();
}

export default function DocumentReview({initialDocument = null}) {
  const [documents,setDocuments]=useState([]);
  const [current,setCurrent]=useState(initialDocument);
  const [fields,setFields]=useState(() => ({...defaults, ...initialDocument?.fields}));
  const [busy,setBusy]=useState(false);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState('');
  const [listError,setListError]=useState('');
  const [message,setMessage]=useState(initialDocument ? (initialDocument.duplicate
    ? 'This PDF is already archived. Its existing review is open.' : 'PDF archived. Review the details below.') : '');
  const [conflict,setConflict]=useState(false);
  const [saveMessage,setSaveMessage]=useState('');
  const [saveError,setSaveError]=useState('');
  const [editing,setEditing]=useState(false);
  const [pane,setPane]=useState('review');
  const [focusRequest,setFocusRequest]=useState(initialDocument ? 1 : 0);
  const reviewHeading=useRef(null);
  const saveFeedback=useRef(null);

  async function loadList() {
    setLoading(true); setListError('');
    try {const result=await request('/api/documents'); setDocuments(result.documents);}
    catch {setListError('Unable to load archived documents. Try again.');}
    finally {setLoading(false);}
  }
  useEffect(()=>{loadList();},[]);
  useEffect(()=>{
    if (!focusRequest) return;
    reviewHeading.current?.focus({preventScroll:true});
    reviewHeading.current?.scrollIntoView?.({block:'start'});
  },[focusRequest]);
  useEffect(()=>{
    if (saveMessage||saveError) saveFeedback.current?.scrollIntoView?.({block:'nearest'});
  },[saveMessage,saveError]);
  function showDocument(value,bringIntoView=false) {
    setCurrent(value); setFields({...defaults,...value.fields}); setConflict(false); setError('');
    setSaveMessage(''); setSaveError('');
    if (bringIntoView) {
      setPane('review');
      setFocusRequest(previous=>previous+1);
    }
  }
  async function openDocument(id) {
    setBusy(true); setMessage(''); setError('');
    try {showDocument(await request(`/api/documents/${encodeURIComponent(id)}`),true);}
    catch {setError('Unable to open this document. Try again.');}
    finally {setBusy(false);}
  }
  async function save(event) {
    event.preventDefault(); setSaveError(''); setSaveMessage(''); setMessage(''); setBusy(true);
    try {
      const value=await request(`/api/documents/${encodeURIComponent(current.id)}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({version:current.version,fields,status:'reviewed'})});
      showDocument(value); setEditing(false); setSaveMessage('Review saved. Storage records are unchanged.'); await loadList();
    } catch (failure) {
      if (failure.status===409) {setConflict(true); setSaveError('This review changed since you opened it. Your edits are still here. Reload the latest review to replace them.');}
      else {setSaveError('Unable to save this review. Your edits are still here. Try again.');}
    } finally {setBusy(false);}
  }
  const change=(key,value)=>{setSaveMessage('');setFields(previous=>({...previous,[key]:value}));};
  const input=(key,label,type='text')=><TextField name={key} variant="secondary" value={fields[key]??''} onChange={value=>change(key,value)} isDisabled={busy} className="review-field"><Label>{label}</Label><Input type={type} fullWidth/></TextField>;
  const choice=(key,label,options)=><Select name={key} variant="secondary" value={fields[key]} onChange={value=>change(key,value)} isDisabled={busy} fullWidth className="review-field"><Label>{label}</Label><Select.Trigger><Select.Value/><Select.Indicator/></Select.Trigger><Select.Popover><ListBox>{options.map(([value,text])=><ListBox.Item id={value} key={value} textValue={text}>{text}<ListBox.ItemIndicator/></ListBox.Item>)}</ListBox></Select.Popover></Select>;

  const pdfUrl = current && `/api/documents/${encodeURIComponent(current.id)}/pdf`;
  const reviewFields = current && (current.fields ?? {});
  const issues = documentIssues(current);
  const correctionFields = issueFields.filter(([pattern]) => issues.some(issue => pattern.test(issue)));
  const showAction = !correctionFields.length || issues.some(issue => /confirm renewal|no readable embedded text/i.test(issue));
  const hasChanges = Object.keys(defaults).some(key => fields[key] !== (reviewFields?.[key] ?? defaults[key]));
  const pending = documents.filter(item => item.status !== 'reviewed');
  const reviewed = documents.filter(item => item.status === 'reviewed');
  const documentList = items => <ul className="archive-list">
    {items.map(item => {
      return <li key={item.id} className="correction-queue-row">
        <Button type="button" variant="ghost" className="correction-queue-trigger" isDisabled={busy} onPress={() => openDocument(item.id)}>
          <strong>{issueTitle(item)}</strong>
          <span className="correction-queue-meta">
            {item.fields?.customer_name || 'Customer not identified'}
            {item.fields?.work_order_number && ` · RO ${item.fields.work_order_number}`}
          </span>
        </Button>
      </li>;
    })}
  </ul>;

  function backToQueue() {
    setCurrent(null);
    setEditing(false);
    setMessage('');
    setError('');
    setSaveMessage('');
    setSaveError('');
  }

  return <section className="document-page" aria-label="Document review">
    {!current ? <>
      <Card className="correction-pane correction-queue" aria-labelledby="archive-title">
        <div className="correction-card-heading">
          <div><h2 id="archive-title">Review queue</h2>
            {!loading && !listError && pending.length > 0 && <p>{pending.length === 1 ? '1 submission needs review' : `${pending.length} submissions need review`}</p>}
          </div>
          <Button type="button" size="sm" variant="ghost" isDisabled={loading || busy} onPress={loadList}>Refresh documents</Button>
        </div>
        {loading ? <p>Loading documents…</p> : listError ? <Alert role="alert" status="danger"><Alert.Indicator/><Alert.Content><Alert.Description>{listError}</Alert.Description></Alert.Content></Alert>
          : pending.length > 0 ? documentList(pending) : <p>No submissions need review.</p>}
      </Card>
      {!loading && !listError && reviewed.length > 0 && <Disclosure className="correction-pane correction-archive">
        <Disclosure.Heading><Disclosure.Trigger>Reviewed documents ({reviewed.length})<Disclosure.Indicator/></Disclosure.Trigger></Disclosure.Heading>
        <Disclosure.Content><Disclosure.Body>{documentList(reviewed)}</Disclosure.Body></Disclosure.Content>
      </Disclosure>}
    </> : <div className="correction-workspace" data-mobile-pane={pane}>
      <BackButton onPress={backToQueue} isDisabled={busy} className="back-button">Back to corrections</BackButton>
      <header className="correction-heading">
        <div>
          <h2 id="review-title" ref={reviewHeading} tabIndex={-1}>{reviewFields.customer_name || 'Review correction'}</h2>
          {reviewFields.work_order_number && <p>RO {reviewFields.work_order_number}</p>}
        </div>
        <Chip size="sm" variant="soft" color={current.status === 'reviewed' ? 'success' : 'warning'}>{current.status === 'reviewed' ? 'Reviewed' : 'Needs review'}</Chip>
      </header>
      {message && <Alert role="status" status="success" className="document-feedback"><Alert.Indicator/><Alert.Content><Alert.Description>{message}</Alert.Description></Alert.Content></Alert>}
      <Tabs className="correction-tabs" selectedKey={pane} onSelectionChange={setPane}>
        <Tabs.ListContainer><Tabs.List aria-label="Correction workspace view">
          <Tabs.Tab id="review" aria-label="Review details">Review<Tabs.Indicator/></Tabs.Tab>
          <Tabs.Tab id="pdf" aria-label="Original PDF">PDF<Tabs.Indicator/></Tabs.Tab>
        </Tabs.List></Tabs.ListContainer>
      </Tabs>
      <div className="correction-columns">
        <OriginalPdf key={current.id} url={pdfUrl} pages={current.pages}/>
        <section className="review-panel" aria-label="Correction details">
          <Card className="correction-pane correction-details">
            <div className="correction-warning">
              <h3>{issues.length > 1 ? 'Issues' : 'Issue'}</h3>
              {issues.length > 1
                ? <ul>{issues.map((issue, index) => <li key={index}>{issue}</li>)}</ul>
                : <p>{issues[0] || reviewLabel(current)}</p>}
            </div>
            {!editing ? <>
              <Form className="correction-action" onSubmit={save}>
                {correctionFields.map(([,key,label,type]) => <React.Fragment key={key}>
                  {['lug_nuts','center_caps','centering_rings'].includes(key)
                    ? choice(key,label,accessoryOptions)
                    : input(key,label,type)}
                </React.Fragment>)}
                {showAction && choice('action','Suggested action',actions)}
                {saveError && <Alert ref={saveFeedback} role="alert" status="danger">
                  <Alert.Indicator/><Alert.Content><Alert.Description>{saveError}</Alert.Description>
                    {conflict && <Button type="button" variant="secondary" isDisabled={busy} onPress={() => openDocument(current.id)}>Reload latest review</Button>}
                  </Alert.Content>
                </Alert>}
                <div className="correction-actions">
                  <Button type="submit" variant="primary" isDisabled={busy || conflict || (current.status === 'reviewed' && !hasChanges)}>
                    {busy ? 'Working…' : 'Save review'}
                  </Button>
                  <Button type="button" variant="ghost" onPress={() => setEditing(true)} isDisabled={busy}>Edit details</Button>
                </div>
              </Form>
              {saveMessage && <Alert ref={saveFeedback} role="status" status="success"><Alert.Indicator/><Alert.Content><Alert.Description>{saveMessage}</Alert.Description></Alert.Content></Alert>}
            </> : <>
              <div className="correction-card-heading">
                <h3>Edit details</h3>
                <Button type="button" size="sm" variant="ghost" isDisabled={busy} onPress={() => {showDocument(current); setEditing(false);}}>Cancel</Button>
              </div>
              <Form onSubmit={save}>
                <Fieldset disabled={busy} className="review-fields">
                  <div className="review-grid">
                    {input('customer_name','Customer')}{input('work_order_number','RO')}
                    {input('vehicle','Vehicle')}{input('vin','VIN')}{input('start_date','Source date','date')}
                  </div>
                  <p className="date-provenance">Date source: {fields.date_source || 'Not identified'}.</p>
                  {choice('action','Suggested action',actions)}
                  <TextField name="storage_description" variant="secondary" value={fields.storage_description} onChange={value => change('storage_description', value)} isDisabled={busy} className="review-field"><Label>Storage description</Label><TextArea rows={3} fullWidth/></TextField>
                  <TextField name="notes" variant="secondary" value={fields.notes} onChange={value => change('notes', value)} isDisabled={busy} className="review-field"><Label>Notes / customer requests</Label><TextArea rows={3} fullWidth/></TextField>
                  <Disclosure className="review-details" isDisabled={busy}><Disclosure.Heading><Disclosure.Trigger>Accessories<Disclosure.Indicator/></Disclosure.Trigger></Disclosure.Heading><Disclosure.Content><Disclosure.Body><div className="accessory-grid">{[['centering_rings','Centering rings'],['lug_nuts','Lug nuts'],['center_caps','Center caps']].map(([key,label]) => <React.Fragment key={key}>{choice(key,label,accessoryOptions)}</React.Fragment>)}</div></Disclosure.Body></Disclosure.Content></Disclosure>
                  <Disclosure className="review-details" isDisabled={busy}><Disclosure.Heading><Disclosure.Trigger>Document details &amp; contact<Disclosure.Indicator/></Disclosure.Trigger></Disclosure.Heading><Disclosure.Content><Disclosure.Body><div className="review-grid">{input('document_type','Document type')}{input('invoice_number','Invoice number')}{input('contact','Contact')}{input('date_source','Date source')}</div></Disclosure.Body></Disclosure.Content></Disclosure>
                  <div className="save-row">
                    {saveError && <Alert ref={saveFeedback} role="alert" status="danger"><Alert.Indicator/><Alert.Content><Alert.Description>{saveError}</Alert.Description>{conflict && <Button type="button" variant="secondary" isDisabled={busy} onPress={() => openDocument(current.id)}>Reload latest review</Button>}</Alert.Content></Alert>}
                    <Button type="submit" variant="primary" isDisabled={busy || conflict}>{busy ? 'Working…' : 'Save review'}</Button>
                  </div>
                </Fieldset>
              </Form>
            </>}
            <Disclosure className="review-details"><Disclosure.Heading><Disclosure.Trigger>Original extracted values<Disclosure.Indicator/></Disclosure.Trigger></Disclosure.Heading><Disclosure.Content><Disclosure.Body><dl className="extracted-values">{Object.entries(current.extracted ?? {}).map(([key,value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{typeof value === 'string' ? value : JSON.stringify(value)}</dd></div>)}</dl></Disclosure.Body></Disclosure.Content></Disclosure>
          </Card>
        </section>
      </div>
    </div>}
    {error && <Alert role="alert" status="danger" className="document-feedback"><Alert.Indicator/><Alert.Content><Alert.Description>{error}</Alert.Description></Alert.Content></Alert>}
  </section>;
}
