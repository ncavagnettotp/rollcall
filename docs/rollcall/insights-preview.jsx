import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Label, ListBox, Select} from '@heroui/react';

const ranges = {
  '7': {label:'Last 7 days', start:'Nov 11', averageStored:126, averageOverdue:11, checkIns:8, pickups:5, renewals:4},
  '30': {label:'Last 30 days', start:'Oct 19', averageStored:124, averageOverdue:12, checkIns:24, pickups:19, renewals:16},
  '90': {label:'Last 90 days', start:'Aug 20', averageStored:117, averageOverdue:10, checkIns:61, pickups:40, renewals:39},
};

const icons = {
  stored:['M4 6c0-4 16-4 16 0s-16 4-16 0v12c0 4 16 4 16 0V6M4 10c0 4 16 4 16 0M4 14c0 4 16 4 16 0'],
  overdue:['','M10.9 3.6a1.3 1.3 0 0 1 2.2 0l8.3 14.9a1.2 1.2 0 0 1-1.1 1.8H3.7a1.2 1.2 0 0 1-1.1-1.8ZM12 9v5m0 3v.2'],
  in:['m7 10-5 2v7l10 4 10-4v-7l-5-2M2 12l10 4 10-4','M12 2v10M8 8l4 4 4-4'],
  out:['m7 10-5 2v7l10 4 10-4v-7l-5-2M2 12l10 4 10-4','M12 12V2M8 6l4-4 4 4'],
  renewal:['M3 12a9 9 0 0 1 16-6l2 2m0 4a9 9 0 0 1-16 6l-2-2','M21 3v5h-5M3 21v-5h5'],
};

function Icon({name}) {
  const [outline,accent] = icons[name];
  return <svg className="insights-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {outline && <path d={outline}/>}
    {accent && <path className="insights-icon-accent" d={accent}/>}
  </svg>;
}

function Insights() {
  const [selection,setSelection] = useState('30');
  const range = ranges[selection];
  const activity = [['Check-ins',range.checkIns,'in'],['Pickups',range.pickups,'out'],['Renewals',range.renewals,'renewal']];
  const averages = [
    ['Stored sets',range.averageStored,'stored'],
    ['Overdue sets',range.averageOverdue,'overdue'],
  ];

  return <div className="insights-layout">
    <div className="insights-toolbar">
      <div><span className="sample-label">Illustrative data</span><span className="insights-dates">{range.start} – Nov 17, 2026</span></div>
      <Select value={selection} onChange={key=>{if(ranges[key])setSelection(key);}} className="insights-range">
        <Label className="sr-only">Date range</Label>
        <Select.Trigger><Select.Value/><Select.Indicator/></Select.Trigger>
        <Select.Popover><ListBox>{Object.entries(ranges).map(([key,item])=>
          <ListBox.Item key={key} id={key} textValue={item.label}>{item.label}<ListBox.ItemIndicator/></ListBox.Item>
        )}</ListBox></Select.Popover>
      </Select>
    </div>
    <div className="insights-history" aria-live="polite">
      <section className="card insights-activity" aria-labelledby="insights-activity-title">
        <h2 id="insights-activity-title">Storage activity</h2>
        <table>
          <thead><tr><th scope="col">Activity</th><th scope="col">Sets</th></tr></thead>
          <tbody>{activity.map(([label,count,icon])=><tr key={label}>
            <th scope="row"><span><Icon name={icon}/>{label}</span></th><td>{count}</td>
          </tr>)}</tbody>
        </table>
      </section>
      <section className="card insights-averages" aria-labelledby="insights-averages-title">
        <h2 id="insights-averages-title">Daily averages</h2>
        <dl>{averages.map(([label,count,icon])=><div key={label}>
          <dt><Icon name={icon}/><span>{label}</span></dt>
          <dd>{count}</dd>
        </div>)}</dl>
      </section>
    </div>
    <section className="insights-today" aria-labelledby="insights-today-title">
      <h2 id="insights-today-title">Today</h2>
      <p><strong>18</strong> due in 30 days</p>
      <p><strong>10</strong> overdue</p>
    </section>
  </div>;
}

const host = document.getElementById('insights-root');
if (host) createRoot(host).render(<Insights/>);
