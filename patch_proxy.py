# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
PATH = r'C:\Users\NTCN\AppData\Local\Temp\trr-repo\index.html'
c = open(PATH, encoding='utf-8').read()

# Find and replace buscarContatosRR
idx = c.find('function buscarContatosRR(')
actual_start = c.rfind('\n', 0, idx) + 1

# Find end of _rrShowManualForm
last_idx = c.find('function _rrShowManualForm(')
depth = 0
i = c.find('{', last_idx)
while i < len(c):
    if c[i] == '{': depth += 1
    elif c[i] == '}':
        depth -= 1
        if depth == 0:
            i += 1
            break
    i += 1
fn_end = i

print(f'Replacing lines {c[:actual_start].count(chr(10))+1} to {c[:fn_end].count(chr(10))+1}')

NEW_BLOCK = (
"var _rrProxyUrl = 'http://localhost:7891';\n"
"\n"
"function buscarContatosRR(carCod, pid) {\n"
"  var el = document.getElementById('pdp-contatos-' + pid);\n"
"  if (!el) return;\n"
"  el.innerHTML =\n"
"    '<div style=\"display:flex;align-items:center;gap:10px;padding:12px;background:#f0f7f2;border:1px solid #c8e6c9;border-radius:9px\">'\n"
"    + '<div style=\"width:16px;height:16px;border:2px solid #1a6e42;border-top-color:transparent;border-radius:50%;animation:rrSpin 0.8s linear infinite\"></div>'\n"
"    + '<span style=\"font-size:12.5px;color:#1a6e42;font-weight:600\">Buscando contatos…</span>'\n"
"    + '</div>';\n"
"\n"
"  var rrUrl = 'https://www.registrorural.com.br/imoveis/car-' + encodeURIComponent(carCod) + '/';\n"
"\n"
"  // 1. Tenta proxy local (roda na maquina do usuario, sem restricoes de CORS/Cloudflare)\n"
"  fetch(_rrProxyUrl + '/ping', {signal: AbortSignal.timeout ? AbortSignal.timeout(2000) : undefined})\n"
"  .then(function(r) { return r.ok; })\n"
"  .catch(function() { return false; })\n"
"  .then(function(proxyOk) {\n"
"    if (proxyOk) {\n"
"      return fetch(_rrProxyUrl, {\n"
"        method: 'POST',\n"
"        headers: {'Content-Type': 'application/json'},\n"
"        body: JSON.stringify({cod_car: carCod})\n"
"      }).then(function(r) { return r.json(); });\n"
"    }\n"
"    // 2. Tenta Supabase Edge Function (check cache)\n"
"    return fetch(_rrSaveEdge, {\n"
"      method: 'POST',\n"
"      headers: {'Content-Type': 'application/json'},\n"
"      body: JSON.stringify({cod_car: carCod, action: 'check'})\n"
"    }).then(function(r) { return r.json(); });\n"
"  })\n"
"  .then(function(data) {\n"
"    if (!el) return;\n"
"    if (data && data.ok && data.contatos && data.contatos.length > 0) {\n"
"      _rrRenderContatos(el, data.contatos, data.imovel_titulo || '', data.source || 'rr');\n"
"    } else {\n"
"      _rrShowManualForm(el, carCod, pid, rrUrl);\n"
"    }\n"
"  })\n"
"  .catch(function() {\n"
"    if (el) _rrShowManualForm(el, carCod, pid, rrUrl);\n"
"  });\n"
"}\n"
"\n"
"function _rrShowManualForm(el, carCod, pid, rrUrl) {\n"
"  if (!el) return;\n"
"  el.innerHTML =\n"
"    '<div style=\"margin-bottom:6px\">'\n"
"    + '<label style=\"font-size:11px;font-weight:600;color:var(--dark);display:block;margin-bottom:3px\">Nome da Fazenda</label>'\n"
"    + '<input id=\"rr-fazenda-' + pid + '\" type=\"text\" placeholder=\"Nome conforme aparece no Registro Rural\" '\n"
"    + 'style=\"width:100%;box-sizing:border-box;padding:5px 9px;border:1px solid #dde2e7;border-radius:6px;font-size:12px\">'\n"
"    + '</div>'\n"
"    + '<div style=\"display:flex;gap:6px;margin-bottom:5px\">'\n"
"    + '<select id=\"rr-kind-' + pid + '\" style=\"padding:5px 8px;border:1px solid #dde2e7;border-radius:6px;font-size:12px\">'\n"
"    + '<option value=\"phone\">\U0001f4f1 Telefone</option>'\n"
"    + '<option value=\"email\">\U0001f4e7 E-mail</option>'\n"
"    + '<option value=\"other\">\U0001f4cb Outro</option>'\n"
"    + '</select>'\n"
"    + '<input id=\"rr-val-' + pid + '\" type=\"text\" placeholder=\"Ex: (61) 99999-9999\" '\n"
"    + 'style=\"flex:1;padding:5px 9px;border:1px solid #dde2e7;border-radius:6px;font-size:12px\">'\n"
"    + '</div>'\n"
"    + '<input id=\"rr-lbl-' + pid + '\" type=\"text\" placeholder=\"Etiqueta (ex: Telefone do imóvel)\" '\n"
"    + 'style=\"width:100%;box-sizing:border-box;padding:5px 9px;border:1px solid #dde2e7;border-radius:6px;font-size:12px;margin-bottom:7px\">'\n"
"    + '<button onclick=\"salvarContatoRR(\\'' + carCod + '\\',\\'' + pid + '\\')\" '\n"
"    + 'style=\"padding:6px 14px;background:#1a6e42;color:#fff;border:none;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer\">\U0001f4be Salvar</button>'\n"
"    + ' <a href=\"' + rrUrl + '\" target=\"_blank\" rel=\"noopener\" '\n"
"    + 'style=\"font-size:11.5px;color:#1a6e42;text-decoration:none\">\U0001f517 Abrir no RR</a>';\n"
"}"
)

c2 = c[:actual_start] + NEW_BLOCK + '\n' + c[fn_end:]
print('New size:', len(c2))

# Add spin CSS if not present
if 'rrSpin' not in c2:
    style_end = c2.find('</style>')
    if style_end > 0:
        c2 = c2[:style_end] + '@keyframes rrSpin{to{transform:rotate(360deg)}}\n' + c2[style_end:]
        print('CSS rrSpin added')

assert 'function buscarContatosRR(' in c2
assert '_rrProxyUrl' in c2
assert "action: 'check'" in c2
print('Assertions OK')
open(PATH, 'w', encoding='utf-8').write(c2)
print('Done. Written', len(c2), 'chars.')
