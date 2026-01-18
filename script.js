<script>
let flights=[];
let sortKey="date";
let sortDir=1;

const AIRPORTS = {
  DYR:[64.734,177.741],
  PVS:[64.378,-173.242],
  KPW:[67.845,166.139],
  PWE:[69.783,170.597],
  KVM:[62.591,174.520],
  "БНГ":[63.049,179.316],
  "ВГИ":[64.405,176.002],
  "ЭГТ":[66.320,179.122]
};

function aircraftColor(name){
  name = name.toUpperCase();
  if(name.includes("AN-24")) return "#d32f2f";
  if(name.includes("DHC-6")) return "#1976d2";
  if(name.includes("MI")) return "#388e3c";
  return "#616161";
}

/* ===== CSV (с кэшем) ===== */
const CACHE_KEY = "chukotavia_csv_v1";

async function loadCSV(){
  const cached = localStorage.getItem(CACHE_KEY);
  if(cached){
    flights = JSON.parse(cached);
    init();
    return;
  }

  const r = await fetch("chukotavia_api_results.csv");
  const text = await r.text();
  const lines = text.trim().split("\n");
  const headers = lines.shift().split(",");

  flights = lines.map(l=>{
    const v=l.split(",");
    let o={};
    headers.forEach((h,i)=>o[h]=v[i]);
    return o;
  });

  localStorage.setItem(CACHE_KEY, JSON.stringify(flights));
  init();
}

loadCSV();

/* ===== ФИЛЬТРЫ ===== */
function init(){
  fill("from", flights.map(f=>f.origin));
  fill("to", flights.map(f=>f.destination));
  fill("aircraft", flights.map(f=>f.aircraft));

  document.querySelectorAll("select,input").forEach(e=>e.onchange=render);

  initMap();
  render();
}

function fill(id,arr){
  const s=document.getElementById(id);
  [...new Set(arr)].sort().forEach(v=>s.add(new Option(v,v)));
}

function resetFilters(){
  from.value="";
  to.value="";
  aircraft.value="";
  dateFrom.value="";
  dateTo.value="";
  render();
}

/* ===== ДАТЫ ===== */
const norm=d=>{
  const [dd,mm,yy]=d.split(".");
  return new Date(`${yy}-${mm}-${dd}`);
};

/* ===== СОРТИРОВКА ===== */
document.querySelectorAll("th[data-sort]").forEach(th=>{
  th.onclick=()=>{
    const k=th.dataset.sort;
    sortDir = (sortKey===k) ? -sortDir : 1;
    sortKey = k;
    render();
  };
});

/* ===== MAP ===== */
let map, routeLayer, markerLayer;

function initMap(){
  map = L.map("map", {
    worldCopyJump:false,
    maxBounds:[[-90,-180],[90,180]]
  }).setView([65,170],4);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

  routeLayer = L.layerGroup().addTo(map);
  markerLayer = L.layerGroup().addTo(map);
}

function drawRoutes(list){
  routeLayer.clearLayers();
  markerLayer.clearLayers();

  let bounds=[];

  list.forEach(f=>{
    const a = AIRPORTS[f.origin];
    const b = AIRPORTS[f.destination];
    if(!a||!b) return;

    const line = L.geodesic(
      [a,b],
      {
        weight:2,
        color: aircraftColor(f.aircraft),
        opacity:0.85
      }
    ).addTo(routeLayer);

    // hover эффект
    line.on("mouseover",()=>line.setStyle({weight:4}));
    line.on("mouseout",()=>line.setStyle({weight:2}));

    // маркеры
    [a,b].forEach(p=>{
      L.circleMarker(p,{
        radius:4,
        color:"#000",
        fillColor:"#fff",
        fillOpacity:1
      }).addTo(markerLayer);
    });

    bounds.push(a,b);
  });

  if(bounds.length){
    map.fitBounds(bounds,{padding:[40,40]});
  }
}

/* ===== RENDER ===== */
function render(){
  let res = flights.filter(f=>
    (!from.value||f.origin===from.value)&&
    (!to.value||f.destination===to.value)&&
    (!aircraft.value||f.aircraft===aircraft.value)&&
    (!dateFrom.value||norm(f.date)>=new Date(dateFrom.value))&&
    (!dateTo.value||norm(f.date)<=new Date(dateTo.value))
  );

  res.sort((a,b)=>{
    let x,y;
    if(sortKey==="date"){x=norm(a.date);y=norm(b.date);}
    else{x=+a[sortKey];y=+b[sortKey];}
    return (x>y?1:-1)*sortDir;
  });

  rows.innerHTML="";
  if(!res.length){
    table.style.display="none";
    empty.style.display="block";
    drawRoutes([]);
    return;
  }

  table.style.display="table";
  empty.style.display="none";

  res.forEach(f=>{
    rows.innerHTML+=`
    <tr>
      <td>${f.date}</td>
      <td>${f.origin}</td>
      <td>${f.destination}</td>
      <td>${f.flight_number}</td>
      <td>${f.departure}</td>
      <td>${f.arrival}</td>
      <td>${f.aircraft}</td>
      <td>${(+f.price).toLocaleString()} ₽</td>
      <td>${f.available}</td>
      <td>
        <a href="https://booking.chukotavia.com/websky/" target="_blank">
          <button class="buy">от ${(+f.price).toLocaleString()} ₽</button>
        </a>
      </td>
    </tr>`;
  });

  drawRoutes(res);
}

/* DOM */
const from=document.getElementById("from");
const to=document.getElementById("to");
const aircraft=document.getElementById("aircraft");
const dateFrom=document.getElementById("dateFrom");
const dateTo=document.getElementById("dateTo");
const rows=document.getElementById("rows");
const table=document.getElementById("table");
const empty=document.getElementById("empty");
</script>
