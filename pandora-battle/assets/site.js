const languageKey='pandora-battle-language';
function setLanguage(code){
 const language=code==='ko'?'ko':'en';
 document.documentElement.lang=language;
 document.querySelectorAll('[data-lang-choice]').forEach(button=>{const active=button.dataset.langChoice===language;button.classList.toggle('is-active',active);button.setAttribute('aria-pressed',String(active));});
 document.querySelectorAll('[data-alt-en]').forEach(image=>image.alt=image.dataset[language==='ko'?'altKo':'altEn']);
 try{localStorage.setItem(languageKey,language);}catch{}
}
let initialLanguage='en';try{initialLanguage=localStorage.getItem(languageKey)||'en';}catch{}
setLanguage(initialLanguage);
document.querySelectorAll('[data-lang-choice]').forEach(button=>button.addEventListener('click',()=>setLanguage(button.dataset.langChoice)));
const dialog=document.getElementById('mediaDialog');
if(dialog){
 let opener=null;
 document.querySelectorAll('[data-gallery]').forEach(link=>link.addEventListener('click',event=>{
  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||typeof dialog.showModal!=='function')return;
  event.preventDefault();opener=link;
  const original=link.querySelector('img');const large=document.getElementById('dialogImage');
  large.src=link.href;large.alt=original.alt;large.dataset.altEn=original.dataset.altEn;large.dataset.altKo=original.dataset.altKo;
  document.getElementById('mediaTitle').replaceChildren(link.querySelector('.image-label').cloneNode(true));
  dialog.showModal();
 }));
 dialog.querySelector('[data-close-dialog]').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',event=>{const box=dialog.getBoundingClientRect();if(event.target===dialog&&(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom))dialog.close();});
 dialog.addEventListener('close',()=>{if(opener)opener.focus();});
}
