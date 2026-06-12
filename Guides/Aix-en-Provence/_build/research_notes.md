# Aix-en-Provence v1 — research notes

## Hotel (city + day count → hotel research path; not in Trips.html)
Hôtel des Augustins · 3 Rue de la Masse · Vieil Aix (historic centre, steps from Cours Mirabeau)

## Motion times — method
Google/Apple Maps unreadable in Cowork sandbox (heavy SPAs never reach document_idle).
Per Glasgow v1 precedent (Brain.md Part 2, 2026-06-12): walk + drive minutes from a real
routing engine — Valhalla (valhalla1.openstreetmap.de) pedestrian + auto profiles over OSM,
Nominatim geocoding. Actual computed route durations, not estimates/ride-share APIs.
NOTE: Aix old town is heavily pedestrianized — car routes loop the ring road, so inner-core
drive times legitimately exceed walk times.

## Route order (south→north monotonic sweep, ends back near hotel)
Day opener: Hotel → Caumont  : walk 6 · drive 5
1. Hôtel de Caumont (🎟)
   Caumont → Cours Mirabeau    : walk 8 · drive 6
2. Cours Mirabeau (🎒)
   Cours Mirabeau → Albertas   : walk 7 · drive 18
3. Place d'Albertas (🎒)
   Albertas → Cathédrale       : walk 8 · drive 13
4. Cathédrale Saint-Sauveur (🎒)
   Cathédrale → Atelier        : walk 12 · drive 15
5. Atelier de Cézanne (🎟)
Day closer: Atelier → hotel    : walk 20 · drive 9
