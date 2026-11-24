// Fade only the overflowing edges of the independent sidebar scroll area.
(() => {
  const sidebar=document.querySelector('.shell>aside');
  const scroll=document.createElement('div');
  scroll.className='sidebar-scroll';
  scroll.setAttribute('role','region');
  scroll.setAttribute('aria-label','Sidebar navigation');
  scroll.tabIndex=0;
  while(sidebar.firstChild)scroll.append(sidebar.firstChild);
  sidebar.append(scroll);
  scroll.querySelectorAll('button').forEach(button=>{
    const label=button.querySelector('span:not(.nav-badge)')?.textContent.trim();
    if(label){button.setAttribute('aria-label',label);if(!button.title)button.title=label;}
  });
  const update=()=>{
    const remaining=scroll.scrollHeight-scroll.clientHeight-scroll.scrollTop;
    scroll.style.setProperty('--sidebar-fade-top',scroll.scrollTop>1?'18px':'0px');
    scroll.style.setProperty('--sidebar-fade-bottom',remaining>1?'18px':'0px');
    window.positionNavIndicator?.();
  };
  scroll.addEventListener('scroll',update,{passive:true});
  scroll.addEventListener('focusin',()=>requestAnimationFrame(update));
  window.addEventListener('resize',update);
  const observer=new ResizeObserver(update);
  observer.observe(scroll);
  for(const element of scroll.children)observer.observe(element);
  update();
})();
