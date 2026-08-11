-- ============================================================
-- EXTERNADO FEST — Setup del proyecto Supabase nuevo
-- Proyecto: aohpheppigbqmbfpzpbg
-- Correr COMPLETO en: Dashboard → SQL Editor → New query → Run
-- Es repetible: se puede volver a correr sin romper nada.
--
-- Cubre las dos actividades:
--   · Laberinto (neon_maze.html + leaderboard.html) → tabla leaderboard
--   · CHASQUIDO (2026-2/photo_particles.html)       → bucket chasquido
-- ============================================================


-- ------------------------------------------------------------
-- 1. TABLA DEL LABERINTO
-- Columnas derivadas de las consultas reales del código:
--   neon_maze:   select id,name,time_seconds / insert / update
--   leaderboard: select * order by time_seconds / delete
-- ------------------------------------------------------------
create table if not exists public.leaderboard (
  id            bigint generated always as identity primary key,
  name          text not null,
  time_seconds  double precision not null,
  created_at    timestamptz default now()
);


-- ------------------------------------------------------------
-- 2. PERMISOS DE LA TABLA
-- Las páginas son HTML sin backend: usan la clave publicable
-- (rol anon) para todo, así que anon necesita CRUD completo.
-- OJO: esto implica que cualquiera con la página puede borrar
-- el tablero (es lo que hace hoy el botón "Borrar Todo (Admin)").
-- Aceptable para un evento de un día; no dejarlo así en producción.
-- ------------------------------------------------------------
alter table public.leaderboard enable row level security;

drop policy if exists "leaderboard_select_anon" on public.leaderboard;
create policy "leaderboard_select_anon" on public.leaderboard
  for select to anon using (true);

drop policy if exists "leaderboard_insert_anon" on public.leaderboard;
create policy "leaderboard_insert_anon" on public.leaderboard
  for insert to anon with check (true);

drop policy if exists "leaderboard_update_anon" on public.leaderboard;
create policy "leaderboard_update_anon" on public.leaderboard
  for update to anon using (true) with check (true);

drop policy if exists "leaderboard_delete_anon" on public.leaderboard;
create policy "leaderboard_delete_anon" on public.leaderboard
  for delete to anon using (true);


-- ------------------------------------------------------------
-- 3. REALTIME  ← paso fácil de olvidar
-- leaderboard.html escucha postgres_changes para actualizar el
-- tablero sin refrescar. Sin esta línea la página abre bien pero
-- NUNCA se actualiza sola: hay que recargar a mano.
-- (El DO lo hace repetible: no falla si ya estaba agregada.)
-- ------------------------------------------------------------
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and tablename = 'leaderboard'
  ) then
    alter publication supabase_realtime add table public.leaderboard;
  end if;
end $$;


-- ------------------------------------------------------------
-- 4. STORAGE PARA CHASQUIDO
-- Se crea el bucket aquí mismo (no hace falta el dashboard).
-- public = true → las fotos se pueden ver/descargar con su URL.
-- ------------------------------------------------------------
insert into storage.buckets (id, name, public)
values ('chasquido', 'chasquido', true)
on conflict (id) do update set public = true;

-- Permitir SUBIR al bucket con la clave publicable (rol anon).
-- Solo insert: sin delete ni update, para que nadie pueda borrar
-- ni sobrescribir las fotos de los demás.
drop policy if exists "chasquido_insert_anon" on storage.objects;
create policy "chasquido_insert_anon" on storage.objects
  for insert to anon with check (bucket_id = 'chasquido');


-- ------------------------------------------------------------
-- VERIFICACIÓN — se ejecuta sola al final.
-- Las tres columnas deben decir: true / true / true
-- ------------------------------------------------------------
select
  exists (select 1 from information_schema.tables
          where table_schema = 'public' and table_name = 'leaderboard') as tabla_ok,
  exists (select 1 from pg_publication_tables
          where pubname = 'supabase_realtime'
            and tablename = 'leaderboard')                              as realtime_ok,
  exists (select 1 from storage.buckets
          where id = 'chasquido' and public)                            as bucket_ok;


-- ============================================================
-- MANTENIMIENTO — correr cuando haga falta (no es parte del setup)
-- ============================================================

-- A) Vaciar el tablero del laberinto (equivale al botón "Borrar Todo").
-- delete from public.leaderboard;


-- B) BORRAR FOTOS DEL BUCKET  ← NO se puede por SQL.
--    Supabase lo bloquea con un trigger (storage.protect_delete):
--      "Direct deletion from storage tables is not allowed.
--       Use the Storage API instead."
--    Esto evita dejar archivos huérfanos en el almacenamiento.
--
--    Formas correctas de borrar:
--
--    1) Dashboard (lo más simple):
--       Storage → bucket "chasquido" → seleccionar archivos → Delete.
--
--    2) Storage API con la clave service_role, para borrar en bloque
--       después del evento. Correr LOCALMENTE en la terminal; esa clave
--       nunca debe quedar en un archivo del repo ni en el HTML:
--
--       URL="https://aohpheppigbqmbfpzpbg.supabase.co"
--       SK="<service_role del dashboard: Settings → API>"
--       curl -s -X POST "$URL/storage/v1/object/list/chasquido" \
--         -H "Authorization: Bearer $SK" -H "Content-Type: application/json" \
--         -d '{"prefix":"","limit":1000}' \
--         | python3 -c "import sys,json;print(json.dumps({'prefixes':[o['name'] for o in json.load(sys.stdin)]}))" \
--         | curl -s -X DELETE "$URL/storage/v1/object/chasquido" \
--             -H "Authorization: Bearer $SK" -H "Content-Type: application/json" --data-binary @-
--
--    Recordatorio: vaciar el bucket al terminar el evento. Son fotos de
--    las caras de los invitados en almacenamiento público.
