# Librerías vendorizadas

Copia local de las dependencias de `photo_particles.html`, para que la
instalación **arranque sin depender de la wifi del venue**. Solo la subida a
Supabase Storage (botón "📱 Descargar" → QR) sigue necesitando internet real;
todo lo demás (espejo, cuenta regresiva, armado, disolución, sonido) funciona
completamente offline.

No se toca `foto.html`: esa página la abre el celular del invitado con su
propio internet (datos móviles), no depende de la wifi del venue, así que
sigue cargando su fuente desde Google Fonts.

## Contenido y versión exacta

| Carpeta | Librería | Versión | Fuente original |
|---|---|---|---|
| `three/three.min.js` | Three.js core | r128 | `cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js` |
| `three/shaders/` | CopyShader, LuminosityHighPassShader | r128 | `.../three@0.128.0/examples/js/shaders/` |
| `three/postprocessing/` | EffectComposer, RenderPass, ShaderPass, UnrealBloomPass | r128 | `.../three@0.128.0/examples/js/postprocessing/` |
| `supabase/supabase.js` | `@supabase/supabase-js` (UMD) | v2 (`@2`, última menor al vendorizar) | `cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js` |
| `qrcode/qrcode.js` | `qrcode-generator` | 1.4.4 | `cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.js` |
| `fonts/fonts.css` + `fonts/files/*.woff2` | Google Fonts: Inter (300–900) y Unbounded (700, 900) | — | `fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Unbounded:wght@700;900` |

`fonts.css` es el CSS tal cual lo sirve Google (con todos los subsets:
latin, latin-ext, cyrillic, cyrillic-ext, greek, greek-ext, vietnamese), solo
con las URLs reescritas de `https://fonts.gstatic.com/...` a `files/<archivo
local>`. Cada peso (300, 400, 500…) declara su propio `@font-face`, pero
varios pesos comparten el mismo archivo `.woff2` — es el mecanismo normal de
Google Fonts para fuentes variables, no una duplicación accidental.

## Cómo re-vendorizar (si se sube de versión Three.js, Supabase, etc.)

```bash
cd "2026-2/vendor"
BASE="https://cdn.jsdelivr.net/npm/three@0.128.0"   # ajustar versión
curl -sf "$BASE/build/three.min.js" -o three/three.min.js
curl -sf "$BASE/examples/js/shaders/CopyShader.js" -o three/shaders/CopyShader.js
curl -sf "$BASE/examples/js/shaders/LuminosityHighPassShader.js" -o three/shaders/LuminosityHighPassShader.js
curl -sf "$BASE/examples/js/postprocessing/EffectComposer.js" -o three/postprocessing/EffectComposer.js
curl -sf "$BASE/examples/js/postprocessing/RenderPass.js" -o three/postprocessing/RenderPass.js
curl -sf "$BASE/examples/js/postprocessing/ShaderPass.js" -o three/postprocessing/ShaderPass.js
curl -sf "$BASE/examples/js/postprocessing/UnrealBloomPass.js" -o three/postprocessing/UnrealBloomPass.js
curl -sf "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js" -o supabase/supabase.js
curl -sf "https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.js" -o qrcode/qrcode.js
```

Para las fuentes, el CSS de Google solo trae URLs `.woff2` si el
`User-Agent` del request es de un navegador moderno:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
curl -sf -A "$UA" "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Unbounded:wght@700;900&display=swap" -o fonts/fonts.css
grep -oE "url\(https://fonts\.gstatic\.com/[^)]*\)" fonts/fonts.css | sed 's/url(//;s/)$//' | sort -u | \
  while read -r url; do curl -sf "$url" -o "fonts/files/$(basename "$url")"; done
sed -i '' -E 's#https://fonts\.gstatic\.com/[^)]*/([A-Za-z0-9_.-]+\.woff2)#files/\1#' fonts/fonts.css
```

## Verificación

```bash
cd "2026-2" && python3 -m http.server 8000
# abrir http://localhost:8000/photo_particles.html con las devtools abiertas,
# pestaña Network filtrada por dominio — no debe haber peticiones a
# cdn.jsdelivr.net ni fonts.g(oogleapis|static).com, solo a *.supabase.co
# cuando se sube una foto.
```
