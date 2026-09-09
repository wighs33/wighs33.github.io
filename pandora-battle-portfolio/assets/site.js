const nav=document.getElementById('nav');
if(nav){const update=()=>nav.classList.toggle('scrolled',window.scrollY>36);update();window.addEventListener('scroll',update,{passive:true});}
