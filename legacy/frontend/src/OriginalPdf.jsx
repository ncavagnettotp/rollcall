import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {Button, Card, Link} from '@heroui/react';

const constrainZoom = value => Math.max(1, Math.min(5, value));

export default function OriginalPdf({url, pages}) {
  const [pdf, setPdf] = useState(null);
  const [page, setPage] = useState(null);
  const [number, setNumber] = useState(1);
  const [direction, setDirection] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [fit, setFit] = useState(1);
  const [error, setError] = useState(false);
  const [rendered, setRendered] = useState(false);
  const [dragging, setDragging] = useState(false);
  const viewport = useRef(null);
  const paper = useRef(null);
  const canvas = useRef(null);
  const drag = useRef(null);
  const anchor = useRef(null);
  const liveZoom = useRef(1);
  const natural = page?.getViewport({scale: 1});
  const aspect = natural ? natural.width / natural.height : 612 / 792;
  const count = pdf?.numPages ?? pages;

  useEffect(() => {
    if (!globalThis.Worker) return;
    let active = true;
    let task;
    async function load() {
      try {
        const [library, worker] = await Promise.all([
          import('pdfjs-dist'),
          import('pdfjs-dist/build/pdf.worker.min.mjs?url'),
        ]);
        if (!active) return;
        library.GlobalWorkerOptions.workerSrc = worker.default;
        task = library.getDocument({url, isEvalSupported: false, maxImageSize: 16_000_000});
        const document = await task.promise;
        if (active) setPdf(document);
      } catch {
        if (active) setError(true);
      }
    }
    load();
    return () => {
      active = false;
      task?.destroy().catch(() => {});
    };
  }, [url]);

  useEffect(() => {
    if (!pdf) return;
    let active = true;
    setRendered(false);
    pdf.getPage(number).then(value => {if (active) setPage(value);})
      .catch(() => {if (active) setError(true);});
    return () => {active = false;};
  }, [pdf, number]);

  useEffect(() => {
    const element = viewport.current;
    const resize = () => {
      if (element.clientWidth && element.clientHeight) {
        setFit(Math.max(1, Math.min(element.clientWidth - 16, (element.clientHeight - 16) * aspect)));
      }
    };
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    resize();
    return () => observer.disconnect();
  }, [aspect]);

  useEffect(() => {
    if (!page || page.pageNumber !== number) return;
    const currentCanvas = canvas.current;
    const original = page.getViewport({scale: 1});
    const density = (currentCanvas.getBoundingClientRect().width / (fit * zoom)) || 1;
    const scale = Math.min(fit * zoom * density * devicePixelRatio / original.width,
      4096 / Math.max(original.width, original.height));
    // Render offscreen so rapid zoom or page changes can cancel safely.
    const image = document.createElement('canvas');
    const view = page.getViewport({scale});
    image.width = Math.max(1, Math.floor(view.width));
    image.height = Math.max(1, Math.floor(view.height));
    const task = page.render({canvas: image, viewport: view});
    let active = true;
    task.promise.then(() => {
      if (!active) return;
      currentCanvas.width = image.width;
      currentCanvas.height = image.height;
      currentCanvas.getContext('2d').drawImage(image, 0, 0);
      setRendered(true);
    }).catch(() => {if (active) setError(true);});
    return () => {active = false; task.cancel();};
  }, [page, number, fit, zoom]);

  useLayoutEffect(() => {
    liveZoom.current = zoom;
    if (!anchor.current) return;
    const element = viewport.current;
    const box = paper.current.getBoundingClientRect();
    const {u, v, x, y, density} = anchor.current;
    element.scrollLeft += (box.left + u * box.width - x) / density;
    element.scrollTop += (box.top + v * box.height - y) / density;
    anchor.current = null;
  }, [zoom]);

  useEffect(() => {
    const element = viewport.current;
    function wheel(event) {
      if (!event.deltaY || !rendered) return;
      event.preventDefault();
      if (drag.current) return;
      const pixels = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? element.clientHeight : 1);
      const next = constrainZoom(liveZoom.current * Math.exp(-pixels * .0015));
      if (next === liveZoom.current) return;
      const box = paper.current.getBoundingClientRect();
      anchor.current = {
        u: Math.max(0, Math.min(1, (event.clientX - box.left) / box.width)),
        v: Math.max(0, Math.min(1, (event.clientY - box.top) / box.height)),
        x: event.clientX, y: event.clientY,
        density: element.getBoundingClientRect().width / element.offsetWidth || 1,
      };
      liveZoom.current = next;
      setZoom(next);
    }
    element.addEventListener('wheel', wheel, {passive: false});
    return () => element.removeEventListener('wheel', wheel);
  }, [rendered]);

  function panStart(event) {
    if (event.button !== 0 || zoom <= 1) return;
    const element = event.currentTarget;
    element.setPointerCapture(event.pointerId);
    element.focus({preventScroll: true});
    drag.current = {
      id: event.pointerId, x: event.clientX, y: event.clientY,
      left: element.scrollLeft, top: element.scrollTop,
      density: element.getBoundingClientRect().width / element.offsetWidth || 1,
    };
    setDragging(true);
  }

  function panMove(event) {
    const start = drag.current;
    if (start?.id !== event.pointerId) return;
    event.currentTarget.scrollLeft = start.left + (start.x - event.clientX) / start.density;
    event.currentTarget.scrollTop = start.top + (start.y - event.clientY) / start.density;
  }

  function panEnd(event) {
    if (drag.current?.id !== event.pointerId) return;
    drag.current = null;
    setDragging(false);
  }

  function turn(by) {
    setDirection(by > 0 ? 'next' : 'previous');
    setRendered(false);
    setError(false);
    setNumber(value => Math.max(1, Math.min(count, value + by)));
    viewport.current.scrollTo(0, 0);
  }

  return <section className="correction-source" aria-label="Original source document">
    <Card className="correction-pane pdf-pane">
      <div className="correction-card-heading"><h3>Original PDF</h3>
        <div className="pdf-pager">
          <Button size="sm" variant="secondary" aria-label="Previous PDF page" isDisabled={!pdf || number <= 1} onPress={() => turn(-1)}>←</Button>
          <span role="status">Page {number} of {count}</span>
          <Button size="sm" variant="secondary" aria-label="Next PDF page" isDisabled={!pdf || number >= count} onPress={() => turn(1)}>→</Button>
        </div>
      </div>
      <div className="pdf-toolbar" aria-label="PDF zoom">
        <Button size="sm" variant="secondary" aria-label="Zoom out PDF" isDisabled={!rendered || zoom <= 1} onPress={() => setZoom(value => constrainZoom(value - .5))}>−</Button>
        <Button size="sm" variant="secondary" aria-label="Fit PDF page" isDisabled={!rendered} onPress={() => {setZoom(1); viewport.current.scrollTo(0, 0);}}>Fit</Button>
        <Button size="sm" variant="secondary" aria-label="Zoom in PDF" isDisabled={!rendered || zoom >= 5} onPress={() => setZoom(value => constrainZoom(value + .5))}>+</Button>
        <span>{Math.round(zoom * 100)}%</span>
      </div>
      <div className="pdf-viewport" ref={viewport} tabIndex={0} aria-label="PDF page preview"
        data-pannable={rendered && zoom > 1} data-dragging={dragging}
        onPointerDown={panStart} onPointerMove={panMove} onPointerUp={panEnd}
        onPointerCancel={panEnd} onLostPointerCapture={panEnd}>
        {!rendered && <p className="pdf-message">{error ? 'The inline preview is unavailable.' : 'Loading original PDF…'}</p>}
        <div className="pdf-paper" ref={paper} style={{width: fit * zoom, aspectRatio: aspect}}>
          <canvas key={number} ref={canvas} data-ready={rendered} data-direction={direction}
            role="img" aria-label={`PDF page ${number} of ${count}`}/>
        </div>
      </div>
      <div className="pdf-footer"><span>Scroll to zoom · Drag to pan</span>
        <Link href={url} target="_blank" rel="noopener noreferrer">View original PDF ↗</Link>
      </div>
    </Card>
  </section>;
}
