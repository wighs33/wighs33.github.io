const nav=document.getElementById('nav');
if(nav){const update=()=>nav.classList.toggle('scrolled',window.scrollY>36);update();window.addEventListener('scroll',update,{passive:true});}

// Resize only the atlas frame on a verified same-origin message.
window.addEventListener('message', event => {
 const frame = document.getElementById('class-map-frame');
 if (!frame || event.origin !== location.origin || event.source !== frame.contentWindow || event.data?.type !== 'pandora-atlas-height') return;
 const height = event.data.height;
 if (Number.isFinite(height) && height >= 500 && height <= 4800) frame.style.height = Math.ceil(height) + 'px';
});
