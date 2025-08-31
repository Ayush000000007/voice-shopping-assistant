let recognition;
let lang = "en-US";

if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();
  recognition.lang = lang;
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = async (e) => {
    let transcript = e.results[0][0].transcript.toLowerCase();
    document.getElementById("status").innerText = "Heard: " + transcript;

    if (transcript.includes("add")) {
      let item = transcript.replace("add","").trim();
      await fetch("/api/list",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({item:item,category:"general",quantity:"1"})});
    } else if (transcript.includes("remove")) {
      let list = await (await fetch("/api/list")).json();
      let target = transcript.replace("remove","").trim();
      let found = list.find(i=>i.item.toLowerCase().includes(target));
      if(found){
        await fetch("/api/list?id="+found.id,{method:"DELETE"});
      }
    }
    loadList();
  }
}

document.getElementById("micBtn").addEventListener("click",()=> recognition.start());

async function loadList(){
  let list = await (await fetch("/api/list")).json();
  let ul = document.getElementById("list");
  ul.innerHTML="";
  if(list.length===0) document.getElementById("empty").style.display="block";
  else document.getElementById("empty").style.display="none";
  list.forEach(i=>{
    ul.innerHTML+=`<li>${i.quantity} × ${i.item}</li>`;
  });

  let sugg = await (await fetch("/api/suggest")).json();
  document.getElementById("suggestions").innerHTML = `
    <b>History:</b> ${sugg.history.join(", ")}<br>
    <b>Seasonal:</b> ${sugg.seasonal.join(", ")}<br>
    <b>Substitutes:</b> ${Object.entries(sugg.substitutes).map(([k,v])=>`${k}→${v}`).join(", ")}
  `;
}

loadList();
