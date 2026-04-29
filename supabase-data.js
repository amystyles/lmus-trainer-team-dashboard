/* LMUS TAP — Supabase data loader
   Replaces bookings-data.js. Sets window.BOOKINGS, TEAM_MEMBERS,
   TRAINER_HOME_REGION, then calls window.initTAP() when ready. */

const _SB_URL = 'https://ptvzqqvbhrbophaotlnn.supabase.co/rest/v1';
const _SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0dnpxcXZiaHJib3BoYW90bG5uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MTU5ODMsImV4cCI6MjA5Mjk5MTk4M30.3YDiQKdUPGdjpSnsjUdNJ0brzCh8Lw27Bzk49Cu-7SI';
const _SB_H   = { apikey: _SB_KEY, Authorization: 'Bearer ' + _SB_KEY };

function _isoToMDY(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-');
  return `${parseInt(m)}/${parseInt(d)}/${y}`;
}

(async function _sbLoad() {
  // Loading overlay
  const overlay = document.createElement('div');
  overlay.id = 'sb-loading';
  overlay.innerHTML = `<div style="text-align:center">
    <div style="font-family:'Rajdhani',sans-serif;font-size:13px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#00FF63;margin-bottom:10px;">Loading TAP Data</div>
    <div style="display:flex;gap:6px;justify-content:center">${[0,1,2].map(i=>`<div style="width:6px;height:6px;border-radius:50%;background:#00FF63;animation:sbDot 1.2s ${i*0.2}s ease-in-out infinite"></div>`).join('')}</div>
  </div>`;
  Object.assign(overlay.style, {
    position:'fixed',inset:'0',display:'flex',alignItems:'center',
    justifyContent:'center',background:'#080808',zIndex:'9999'
  });
  const style = document.createElement('style');
  style.textContent = '@keyframes sbDot{0%,80%,100%{opacity:.2;transform:scale(.8)}40%{opacity:1;transform:scale(1)}}';
  document.head.appendChild(style);
  document.body.appendChild(overlay);

  try {
    const [mRes, bRes] = await Promise.all([
      fetch(`${_SB_URL}/team_members?select=*&limit=500&order=full_name`, { headers: _SB_H }),
      fetch(`${_SB_URL}/bookings?select=*&limit=2000&order=start_date`, { headers: _SB_H }),
    ]);

    const members  = await mRes.json();
    const rawBooks = await bRes.json();

    // Expose team members
    window.TEAM_MEMBERS = members;

    // Build TRAINER_HOME_REGION from authoritative address data
    window.TRAINER_HOME_REGION = {};
    members.forEach(m => {
      if (m.home_region) window.TRAINER_HOME_REGION[m.full_name] = m.home_region;
    });

    // Transform bookings to match existing page format
    window.BOOKINGS = rawBooks.map(b => ({
      event:          b.event,
      bookingId:      b.booking_id,
      trainer:        b.trainer,
      eventType:      b.event_type,
      program:        b.program,
      startDate:      _isoToMDY(b.start_date),
      region:         b.region,
      isOnline:       b.is_online,
      fiscalYear:     b.fiscal_year,
      fiscalQuarter:  b.fiscal_quarter,
      status:         b.status,
      confirmed:      b.confirmed,
      dualGroup:      b.dual_group,
    }));

    window.SUPABASE_ACTIVE = true;

  } catch (err) {
    console.error('Supabase load failed:', err);
    overlay.innerHTML = `<div style="font-family:'Rajdhani',sans-serif;color:#ff4444;text-align:center;letter-spacing:2px;font-size:13px;font-weight:700">CONNECTION ERROR<br><span style="font-size:11px;opacity:0.6;letter-spacing:1px">${err.message}</span></div>`;
    return;
  }

  overlay.remove();
  if (typeof window.initTAP === 'function') window.initTAP();
})();
