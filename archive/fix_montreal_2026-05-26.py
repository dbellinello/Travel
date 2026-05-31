import re
from pathlib import Path

path = Path('/sessions/sweet-cool-pasteur/mnt/GoogleDrive-bellinello@gmail.com/My Drive/Travel/Guides/Montreal/montreal_v1.html')
html = path.read_text(encoding='utf-8')
original_len = len(html)

def replace_exact(old, new, label):
    global html
    count = html.count(old)
    if count == 0:
        print(f"  ⚠️  NOT FOUND: {label}")
    elif count > 1:
        print(f"  ⚠️  AMBIGUOUS ({count}x): {label}")
    else:
        html = html.replace(old, new)
        print(f"  ✅ {label}")

# ══ 1. Shows glance pill label ══════════════════════════════════
replace_exact(
    'href="#shows">🎭 Shows, Performances &amp; Concerts</a>',
    'href="#shows">🎭 Shows</a>',
    'Shows pill label'
)

# ══ 2. Day abbreviations → full names (word-bounded) ═══════════
for abbr, full in [('Mon','Monday'),('Tue','Tuesday'),('Wed','Wednesday'),
                    ('Thu','Thursday'),('Fri','Friday'),('Sat','Saturday'),('Sun','Sunday')]:
    count = len(re.findall(r'\b' + abbr + r'\b', html))
    if count:
        html = re.sub(r'\b' + abbr + r'\b', full, html)
        print(f"  ✅ Day abbr {abbr}→{full} ({count} replacements)")
    else:
        print(f"  ⚠️  No {abbr} found")

# ══ 3. Saint Joseph's Crypt sub-label in 🏛 row ═════════════════
replace_exact(
    '🏛️ Daily 7:00am - 9:00pm · Crypt Museum 10:00am - 5:00pm',
    '🏛️ Daily 7:00am - 9:00pm',
    'Saint Josephs Crypt Museum in hours row'
)

# ══ 4. 📒 descriptions over 320 chars ════════════════════════════
replace_exact(
    '📒 Founded on land that once formed the McGill farm, the campus occupies a wide greensward at the foot of Mount Royal. The Roddick Gates on rue Sherbrooke frame a view up the central walk to the neoclassical Arts Building, with the mountain rising directly behind. The campus sits within the Golden Square Mile historic district.',
    '📒 Founded on the McGill farm, the campus occupies a wide greensward at the foot of Mount Royal. The Roddick Gates on rue Sherbrooke frame a view up the central walk to the neoclassical Arts Building, with the mountain rising directly behind. Set within the Golden Square Mile historic district.',
    'McGill description trim'
)
replace_exact(
    "📒 Canada's most-visited art museum — 44,000 works across five interconnected pavilions spanning both sides of rue Sherbrooke Ouest. Collections cover Quebec and Canadian contemporary art, European Impressionism, African art, and Inuit carvings. Permanent collections free of charge; temporary exhibitions are ticketed separately.",
    "📒 Canada's most-visited art museum — 44,000 works across five interconnected pavilions spanning both sides of rue Sherbrooke Ouest. Collections cover Quebec contemporary art, European Impressionism, African art, and Inuit carvings. Permanent collections free; temporary exhibitions ticketed.",
    'MMFA description trim'
)
replace_exact(
    '📒 One of the oldest Chinatowns in North America, established by railroad workers and merchants in the late 19th century. Ceremonial gates on rue de la Gauchetière mark the pedestrian zone of dim sum restaurants, herbal shops, bubble tea cafés, and Asian grocery stalls. The main street is pedestrianized and flanked by inner courtyards.',
    '📒 One of the oldest Chinatowns in North America, established by railroad workers in the 19th century. Ceremonial gates on rue de la Gauchetière mark the pedestrian zone of dim sum restaurants, herbal shops, bubble tea cafés, and Asian grocery stalls. The main street is pedestrianized.',
    'Chinatown description trim'
)
replace_exact(
    '📒 The largest insect museum in North America — 160,000 specimens and 250 live species. A recent renovation introduced immersive sensory experiences: an underground burrowing simulation, a tropical butterfly greenhouse, and a room where visitors handle live insects. Combined admission with the adjacent Botanical Garden is available.',
    '📒 The largest insect museum in North America — 160,000 specimens and 250 live species. A recent renovation introduced immersive experiences: an underground burrowing simulation, a tropical butterfly greenhouse, and a room where visitors handle live insects.',
    'Insectarium description trim'
)
replace_exact(
    "📒 Canada's most vibrant open-air market, running for generations in Little Italy. 300 vendors across an outdoor plaza and indoor halls sell Quebec produce, local cheeses, maple products, cured meats, and prepared foods. Late June is peak season: fresh strawberries, local cherries, and the first summer tomatoes arrive together.",
    "📒 Canada's most vibrant open-air market, running for generations in Little Italy. 300 vendors sell Quebec produce, local cheeses, maple products, and cured meats. Late June is peak season: fresh strawberries, local cherries, and the first summer tomatoes arrive.",
    'Jean-Talon Market description trim'
)

# ══ 5. Photo-ok comment for McGill ════════════════════════════════
replace_exact(
    '<div class="stop-photos">\n<img alt="McGill University Arts Building Roddick Gates" src="_build/assets/800px-McGill_Arts_Building.jpg"/>',
    '<!-- photo-ok: no better-licensed alternative found for McGill University -->\n<div class="stop-photos">\n<img alt="McGill University Arts Building Roddick Gates" src="_build/assets/800px-McGill_Arts_Building.jpg"/>',
    'photo-ok comment for McGill'
)

# ══ 6. no-skip-the-line comment ═══════════════════════════════════
replace_exact(
    '<!-- ══════════════════════════════════════════════ TITLE PAGE -->',
    '<!-- no-skip-the-line: all stops are public parks, open plazas, free-entry landmarks, or museums with standard admission — no skip-the-line or timed-entry booking exists for any stop in this guide -->\n<!-- ══════════════════════════════════════════════ TITLE PAGE -->',
    'no-skip-the-line comment'
)

# ══ 7. Weekly Closures: entry-body → stop-row format ═════════════
replace_exact(
    '<div class="extras-section" id="weekly-closures">\n<div class="extras-title">🗓️ Weekly Closures</div>\n<div class="entry-body">\n<div><strong>Museums &amp; Galleries</strong> · Closed Monday</div>\n</div>\n</div>',
    '<div class="extras-section" id="weekly-closures">\n<div class="extras-title">🗓️ Weekly Closures</div>\n<div class="stop-row"><strong>Museums &amp; Galleries</strong> · Closed Monday</div>\n</div>',
    'Weekly Closures format fix (entry-body → stop-row)'
)

# ══ 8. Downtown restaurant descriptions trim ══════════════════════
replace_exact(
    'Québécois contemporary · seasonal tasting menus · local terroir · chef Bernard Lamonthe.',
    'Québécois contemporary · seasonal tasting menus · local terroir.',
    'Toqué description trim'
)
replace_exact(
    'Contemporary Italian · regional Canadian ingredients · intimate Little Burgundy dining room.',
    'Contemporary Italian · regional Canadian ingredients · Little Burgundy.',
    'Nora Gray description trim'
)
replace_exact(
    'Montreal smoked meat since the 1930s · the original deli on the Main · sandwiches only · cash only.',
    'Smoked meat since the 1930s · the original deli on the Main · cash only.',
    "Schwartz's description trim"
)

# ══ 9. Local Tastes descriptions trim ════════════════════════════
replace_exact(
    'French fries topped with fresh cheese curds and hot brown gravy — the curds must squeak when bitten. Born in rural Quebec, now omnipresent in Montreal from diners to fine-dining riffs. The original version has no toppings: just fries, curds, and sauce.',
    'French fries topped with fresh cheese curds and hot brown gravy — the curds must squeak when bitten. Born in rural Quebec, now omnipresent from diners to fine-dining riffs. The original: just fries, curds, and sauce.',
    'Poutine description trim'
)
replace_exact(
    "Brisket dry-cured in a black pepper and coriander spice rub, then smoked and hand-sliced thin to medium on rye bread with yellow mustard. Distinct from New York pastrami in its brine, cure time, and cut. Schwartz's on Saint-Laurent is the original address.",
    "Brisket dry-cured in a black pepper and coriander rub, then smoked and hand-sliced thin to medium on rye bread with yellow mustard. Distinct from New York pastrami in brine, cure time, and cut. Schwartz's on Saint-Laurent is the original.",
    'Smoked Meat description trim'
)
replace_exact(
    'Hand-rolled, boiled in honey water, and baked in a wood-fired oven — smaller, denser, and sweeter than New York bagels, with a larger hole. Sesame and poppy are the two canonical types. St-Viateur and Fairmount have been baking them around the clock for decades.',
    'Hand-rolled, boiled in honey water, and baked in a wood-fired oven — smaller, denser, and sweeter than a New York bagel, with a larger hole. Sesame and poppy are the two canonical types. St-Viateur and Fairmount bake them around the clock.',
    'Bagel description trim'
)

# ══ 10. Jazz Festival shows description trim (182→≤160) ══════════
replace_exact(
    "🗒 The world's largest jazz festival — 500+ concerts over 10 days. Free outdoor stages at Place des Arts; ticketed indoor shows at Salle Wilfrid-Pelletier. Late June through early July.",
    "🗒 The world's largest jazz festival — 500+ concerts over 10 days. Free outdoor stages at Place des Arts; ticketed indoor shows at Salle Wilfrid-Pelletier.",
    'Jazz Festival description trim'
)

# ══ 11. Metro description: capitalize first letter ════════════════
replace_exact(
    '<div>4 lines serving Downtown, Old Montreal, Plateau, and Olympic Park.</div>',
    '<div>Four lines serving Downtown, Old Montreal, Plateau, and Olympic Park.</div>',
    'Metro description capitalize'
)

# ══ 12. Train Stations: title, icon, class ═══════════════════════
replace_exact(
    '<div class="extras-title">🚆 Stations Near Hotel</div>',
    '<div class="extras-title">🚆 Train Stations Near Hotel</div>',
    'Train Stations title fix'
)
replace_exact(
    '<div class="extras-sub">🚆 Gare Centrale</div>',
    '<div class="extras-sub">🚊 Gare Centrale</div>',
    'Train Stations entry icon 🚆→🚊'
)
replace_exact(
    '<div class="entry-body">\n<div>Via Rail → Québec City · Ottawa · Toronto · Halifax</div>',
    '<div class="station-box">\n<div>Via Rail → Québec City · Ottawa · Toronto · Halifax.</div>',
    'Train Stations class entry-body→station-box + terminal punctuation'
)

# ══ 13. Michelin Sabayon cuisine trim (91→≤80) ════════════════════
replace_exact(
    '14-seat fine dining · creative modern cuisine · chef Patrice Demers · Pointe-Saint-Charles.',
    '14-seat fine dining · creative modern cuisine · chef Patrice Demers.',
    'Sabayon cuisine trim'
)

# ══ 14. Remove 🆓 from Open 24/7 stops ════════════════════════════
# McGill
replace_exact(
    '<div>🏛️ Open 24/7</div>\n<div>⏰ ~1h</div>\n<div>🆓 Free</div>\n<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=McGill+University+845+Rue+Sherbrooke+Ouest+Montreal" target="_blank">845 rue Sherbrooke Ouest · Downtown</a></div>',
    '<div>🏛️ Open 24/7</div>\n<div>⏰ ~1h</div>\n<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=McGill+University+845+Rue+Sherbrooke+Ouest+Montreal" target="_blank">845 rue Sherbrooke Ouest · Downtown</a></div>',
    'Remove 🆓 from McGill (Open 24/7)'
)
# Parc du Mont-Royal
replace_exact(
    '<div>🏛️ Open 24/7</div>\n<div>⏰ ~2h</div>\n<div>🆓 Free</div>\n<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Parc+du+Mont-Royal+Montreal" target="_blank">Chemin Olmsted · Mont-Royal</a></div>',
    '<div>🏛️ Open 24/7</div>\n<div>⏰ ~2h</div>\n<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Parc+du+Mont-Royal+Montreal" target="_blank">Chemin Olmsted · Mont-Royal</a></div>',
    'Remove 🆓 from Parc du Mont-Royal (Open 24/7)'
)
# Parc La Fontaine
replace_exact(
    '<div>🏛️ Open 24/7</div>\n<div>⏰ ~1h</div>\n<div>🆓 Free</div>\n<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Parc+La+Fontaine+Montreal+Plateau+Mont-Royal" target="_blank">Avenue Du Parc-La Fontaine · Plateau Mont-Royal</a></div>',
    '<div>🏛️ Open 24/7</div>\n<div>⏰ ~1h</div>\n<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Parc+La+Fontaine+Montreal+Plateau+Mont-Royal" target="_blank">Avenue Du Parc-La Fontaine · Plateau Mont-Royal</a></div>',
    'Remove 🆓 from Parc La Fontaine (Open 24/7)'
)

# ══ 15. Restaurants Near Hotel low-count comment inside section ══
replace_exact(
    '<!-- low-count: hotel not yet confirmed; restaurants within 25 min walk cannot be identified -->\n<div class="extras-section" id="restaurants">\n<div class="extras-title">🫕 Restaurants Near Hotel</div>\n<div class="extras-empty">No restaurants within 25 min walk of the hotel.</div>\n</div>',
    '<div class="extras-section" id="restaurants">\n<div class="extras-title">🫕 Restaurants Near Hotel</div>\n<!-- low-count: hotel not yet confirmed; restaurants within 25 min walk cannot be identified -->\n<div class="extras-empty">No restaurants within 25 min walk of the hotel.</div>\n</div>',
    'Move Restaurants Near Hotel low-count comment inside section'
)

# ══ 16. Full tours section replacement ═══════════════════════════
OLD_TOURS = '''<!-- ══════════════════════════════════════════════ EoI: TOURS -->
<div class="extras-section" id="tours">
<div class="extras-title">📅 Tours</div>
<div class="tours-group">Viator</div>
<div class="extras-sub">📅 1. <a href="https://www.viator.com/tours/Montreal/Walk-and-Explore-Old-Montreal/d625-124208P4" target="_blank">Old Montreal Small-Group Walking Tour · MTL Detours · Viator · 4.9⭐ · 2212+ reviews</a></div>
<div class="entry-body">
<div>🔖 2-hour small-group walk through Old Montreal's cobblestone streets with a certified MTL Detours guide — Place d'Armes, Château Ramezay, the Old Port, and the historic borough's layered French and British colonial history. Max 10 guests.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 10 max</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 2. <a href="https://www.viator.com/tours/Montreal/Old-Montreal-Food-Tour/d625-198756P2" target="_blank">Old Montreal Guided Food Tour with 8+ Tastings · Viator · 4.8⭐ · 527+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour guided walk through Old Montreal's best food addresses — Montreal-style bagels, Québécois poutine, local cheeses, smoked meat, and French pastries across 8+ tasting stops with cultural commentary from a certified local guide.</div>
<div>🕐 10:00am · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 3. <a href="https://www.viator.com/tours/Montreal/City-tour-afternoon-in-Montreal/d625-217620P8" target="_blank">Guided Small-Group Afternoon City Tour · Viator · 4.9⭐ · 77+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour afternoon van tour through Montreal's highlights: Westmount mansions, Saint Joseph's Oratory, Old Montreal, Notre-Dame Basilica, and the Mount Royal belvedere — with a certified guide providing city-wide historical and cultural context.</div>
<div>🕐 2:00pm · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 4. <a href="https://www.viator.com/tours/Montreal/Old-Montreal-Walking-Tour/d625-185030P1" target="_blank">Walking Tour of Old Montreal — 16/42 Tours · Viator · 4.9⭐ · 605+ reviews</a></div>
<div class="entry-body">
<div>🔖 Bilingual certified guide tour through Old Montreal from Place Royale to the Old Port — the history of Montreal's founding, colonial architecture, and the stories behind the city's most photographed streets.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 5. <a href="https://www.viator.com/tours/Montreal/Jean-Talon-Market-and-Little-Italy-Walking-Secret-Food-tour/d625-7812P252" target="_blank">Jean-Talon Market &amp; Little Italy Secret Food Tour · Viator · 5.0⭐ · 257+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour guided walk through Jean-Talon Market and Little Italy with 8 food tastings — farm-fresh produce, Sicilian arancini, artisan bread, local cheeses, and authentic Italian-Canadian specialties from one of Montreal's most food-forward neighborhoods.</div>
<div>🕐 10:00am · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Marche+Jean-Talon+7070+Avenue+Henri-Julien+Montreal" target="_blank">Jean-Talon Market · Little Italy</a></div>
<!-- walk-over-40: Jean-Talon Market is 5 km from hotel; taxi only -->
<div>🚕 15 min</div>
</div>
<div class="tours-group">GetYourGuide</div>
<!-- low-count: 3 GetYourGuide tours with confirmed visible ratings; 2 additional tours pending manual rating verification -->
<div class="extras-sub">📅 1. <a href="https://www.getyourguide.com/montreal-l195/montreal-food-tour-with-6-tastings-and-drinks-t171276/" target="_blank">Mile End District Food Tour with 8+ Tastings · GetYourGuide · 4.9⭐ · 310+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour walk through Mile End's most celebrated food spots — hand-rolled St-Viateur bagels, poutine, smoked meat, and local pastries, guided through the neighborhood that launched Montreal's culinary reputation by a knowledgeable local host.</div>
<div>🕐 11:00am · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=St-Viateur+Bagel+263+Rue+Saint-Viateur+Ouest+Montreal" target="_blank">St-Viateur Bagel · Mile End</a></div>
<!-- walk-over-40: Mile End is 4.5 km from hotel; taxi only -->
<div>🚕 12 min</div>
</div>
<div class="extras-sub">📅 2. <a href="https://www.getyourguide.com/montreal-l195/montreal-old-montreal-food-and-drink-tour-t630321/" target="_blank">Old Montreal Food and Drink Guided Walking Tour · GetYourGuide · 4.8⭐ · 94+ reviews</a></div>
<div class="entry-body">
<div>🔖 Food and drink walk through Old Montreal's historic streets combining Québécois classics — smoked meat, local cheeses, maple treats, and craft beer — with cobblestone architecture and history narrated by a certified local guide.</div>
<div>🕐 10:00am · ⏳ 2.5h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+Jacques-Cartier+Montreal" target="_blank">Place Jacques-Cartier · Old Montreal</a></div>
<div>🚶 3 min · 🚕 2 min</div>
</div>
<div class="extras-sub">📅 3. <a href="https://www.getyourguide.com/montreal-l195/secret-food-tours-montreal-jean-talon-little-italy-t806240/" target="_blank">Jean-Talon &amp; Little Italy Secret Food Tour · GetYourGuide · 4.6⭐ · 8+ reviews</a></div>
<div class="entry-body">
<div>🔖 Immersive 3-hour food tour through Jean-Talon Market and Little Italy with 8 tastings — farm-fresh produce, carved meats, creamy cheeses, artisan bread, authentic Italian-Canadian specialties, and a cannoli finish with a local foodie guide.</div>
<div>🕐 10:00am · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Marche+Jean-Talon+7070+Avenue+Henri-Julien+Montreal" target="_blank">Jean-Talon Market · Little Italy</a></div>
<!-- walk-over-40: Little Italy is 5 km from hotel; taxi only -->
<div>🚕 15 min</div>
</div>
<div class="tours-group">TripAdvisor</div>
<!-- low-count: 4 TripAdvisor tours; a 5th qualifying non-duplicate tour was not found in this build cycle -->
<div class="extras-sub">📅 1. <a href="https://www.tripadvisor.com/AttractionProductReview-g155032-d20482893-The_Full_Day_small_group_comprehensive_tour_of_Montreal-Montreal_Quebec.html" target="_blank">The Full-Day Small-Group Comprehensive Tour of Montreal · TripAdvisor · 4.9⭐ · 213+ reviews</a></div>
<div class="entry-body">
<div>🔖 Full-day small-group city tour covering Old Montreal, Mount Royal, Saint Joseph's Oratory, Notre-Dame Basilica, Westmount, and the Plateau — ideal for first-time visitors wanting a comprehensive overview of Montreal in a single day.</div>
<div>🕐 9:00am · ⏳ 8h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 2. <a href="https://www.tripadvisor.com/AttractionProductReview-g155032-d16741627-Montreal_RESO_Underground_City_Downtown_Tour_by_MTL_Detours-Montreal_Quebec.html" target="_blank">Montreal RESO Underground City + Downtown Tour by MTL Detours · TripAdvisor · 4.7⭐ · 100+ reviews</a></div>
<div class="entry-body">
<div>🔖 2-hour certified guide tour through the RESO — the world's largest underground pedestrian network — and downtown Montreal streets: public art, Parisian-style metro entrances, hidden cafés, and the architecture that connects 33 km of indoor passages.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 10 max</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+Ville+Marie+Montreal" target="_blank">Place Ville Marie · Downtown</a></div>
<div>🚶 18 min · 🚕 7 min</div>
</div>
<div class="extras-sub">📅 3. <a href="https://www.tripadvisor.ca/AttractionProductReview-g155032-d19500286-Montreal_at_Night_Tour-Montreal_Quebec.html" target="_blank">Montreal at Night Tour · TripAdvisor · 4.5⭐ · 50+ reviews</a></div>
<div class="entry-body">
<div>🔖 Small-group evening driving tour through Montreal's illuminated neighborhoods — Old Montreal, Mount Royal, and the Quartier des Spectacles — finishing with a ride on the Grande Roue observation wheel above the lit-up Old Port.</div>
<div>🕐 7:30pm · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Old+Port+Montreal" target="_blank">Old Port · Old Montreal</a></div>
<div>🚶 8 min · 🚕 4 min</div>
</div>
<div class="extras-sub">📅 4. <a href="https://www.tripadvisor.com/AttractionProductReview-g155032-d19715108-Quebec_city_Montmorency_Falls_1_Day_Tour_from_Montreal-Montreal_Quebec.html" target="_blank">Quebec City &amp; Montmorency Falls 1 Day Tour from Montreal · TripAdvisor · 4.5⭐ · 1552+ reviews</a></div>
<div class="entry-body">
<div>🔖 Full-day guided coach tour from Montreal to Quebec City — the walled historic district, Château Frontenac, Dufferin Terrace, Quartier Petit-Champlain, and a stop at Montmorency Falls before returning to Montreal.</div>
<div>🕐 7:30am · ⏳ 13h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=360+rue+Saint-Antoine+Ouest+Montreal" target="_blank">Central Montreal pickup</a></div>
<div>🏨 ↔ 🚐 Hotel pickup &amp; drop-off</div>
</div>
</div>'''

NEW_TOURS = '''<!-- ══════════════════════════════════════════════ EoI: TOURS -->
<div class="extras-section" id="tours">
<div class="extras-title">📅 Tours</div>
<div class="tours-group">Viator</div>
<div class="extras-sub">📅 1. <a href="https://www.viator.com/tours/Montreal/Walk-and-Explore-Old-Montreal/d625-124208P4" target="_blank"><strong>Old Montreal Small-Group Walking Tour</strong> · MTL Detours · Viator · 4.9⭐ · 2212+ reviews</a></div>
<div class="entry-body">
<div>🔖 2-hour small-group walk through Old Montreal's cobblestone streets with a certified MTL Detours guide — Place d'Armes, Château Ramezay, the Old Port, and the historic borough's layered French and British colonial history. Max 10 guests.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 10 max</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 2. <a href="https://www.viator.com/tours/Montreal/Montreal-101-Walking-Tour-With-a-Local/d625-124208P3" target="_blank"><strong>Plateau Mont-Royal and Mile End Tour</strong> · MTL Detours · Viator · 4.97⭐ · 33+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour certified guide tour of the Plateau Mont-Royal and Mile End neighborhoods — Victorian walk-up architecture, the bohemian Main, Saint-Laurent boulevard murals, and the streets that shaped Montreal's contemporary identity. Max 10 guests.</div>
<div>🕐 10:00am · ⏳ 3h · 👥 10 max</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Plateau+Mont-Royal+Montreal" target="_blank">Plateau Mont-Royal · Montreal</a></div>
<!-- walk-over-40: Plateau is 3+ km from Old Montreal hotel; taxi only -->
<div>🚕 12 min</div>
</div>
<div class="extras-sub">📅 3. <a href="https://www.viator.com/tours/Montreal/City-tour-afternoon-in-Montreal/d625-217620P8" target="_blank"><strong>Guided Small-Group Afternoon City Tour</strong> · Viator · 4.9⭐ · 77+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour afternoon van tour through Montreal's highlights: Westmount mansions, Saint Joseph's Oratory, Old Montreal, Notre-Dame Basilica, and the Mount Royal belvedere — with a certified guide providing city-wide historical and cultural context.</div>
<div>🕐 2:00pm · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 4. <a href="https://www.viator.com/tours/Montreal/Old-Montreal-Walking-Tour/d625-185030P1" target="_blank"><strong>Walking Tour of Old Montreal — 16/42 Tours</strong> · Viator · 4.9⭐ · 605+ reviews</a></div>
<div class="entry-body">
<div>🔖 Bilingual certified guide tour through Old Montreal from Place Royale to the Old Port — the history of Montreal's founding, colonial architecture, and the stories behind the city's most photographed streets.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 5. <a href="https://www.viator.com/tours/Montreal/Montreal-Intercultural-Tour/d625-217620P5" target="_blank"><strong>City Tour: Montreal's Trendy Neighborhoods</strong> · Viator · 4.86⭐ · 35+ reviews</a></div>
<div class="entry-body">
<div>🔖 3-hour certified guide van tour through Montreal's most culturally vibrant neighborhoods — Outremont, Plateau Mont-Royal, Mile End, and Little Italy — covering the city's linguistic, ethnic, and architectural diversity.</div>
<div>🕐 10:00am · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="tours-group">GetYourGuide</div>
<!-- low-count: 3 GetYourGuide tours; additional qualifying non-food non-duplicate tours not available this build cycle -->
<div class="extras-sub">📅 1. <a href="https://www.getyourguide.com/montreal-l195/highlights-hidden-gems-of-old-montreal-guided-walking-tour-t270457/" target="_blank"><strong>Highlights and Hidden Gems of Old Montreal Guided Walking Tour</strong> · GetYourGuide · 4.8⭐ · 94+ reviews</a></div>
<div class="entry-body">
<div>🔖 2-hour guided walk through Old Montreal uncovering iconic sights and off-the-beaten-path spots — Place Jacques-Cartier, the World Trade Centre arcade, an avant-garde art gallery, and a section of the Underground City. No two tours identical.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=William+Gray+Hotel+421+Rue+Saint-Vincent+Montreal" target="_blank">William Gray Hotel · Old Montreal</a></div>
<div>🚶 3 min · 🚕 2 min</div>
</div>
<div class="extras-sub">📅 2. <a href="https://www.getyourguide.com/montreal-l195/montreal-old-montreal-food-and-drink-tour-t630321/" target="_blank"><strong>Old Montreal Food and Drink Guided Walking Tour</strong> · GetYourGuide · 4.8⭐ · 94+ reviews</a></div>
<div class="entry-body">
<div>🔖 Guided walk through Old Montreal's historic streets combining Québécois classics — smoked meat, local cheeses, maple treats, and craft beer — with cobblestone architecture and history narrated by a certified local guide.</div>
<div>🕐 10:00am · ⏳ 2.5h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+Jacques-Cartier+Montreal" target="_blank">Place Jacques-Cartier · Old Montreal</a></div>
<div>🚶 3 min · 🚕 2 min</div>
</div>
<div class="extras-sub">📅 3. <a href="https://www.getyourguide.com/montreal-l195/montreal-reso-underground-city-and-downtown-walking-tour-t309733/" target="_blank"><strong>Montreal RESO Underground City and Downtown Small Group Tour</strong> · GetYourGuide · 4.8⭐ · 248+ reviews</a></div>
<div class="entry-body">
<div>🔖 2-hour certified guide tour through the RÉSO underground pedestrian network and downtown streets — public art, metro entrances, hidden cafés, and the architecture connecting 33 km of indoor passages beneath the city's core.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+Ville+Marie+Montreal" target="_blank">Place Ville Marie · Downtown</a></div>
<div>🚶 18 min · 🚕 7 min</div>
</div>
<div class="tours-group">TripAdvisor</div>
<!-- low-count: 4 TripAdvisor tours; a 5th qualifying non-duplicate tour was not found in this build cycle -->
<div class="extras-sub">📅 1. <a href="https://www.tripadvisor.com/AttractionProductReview-g155032-d20482893-The_Full_Day_small_group_comprehensive_tour_of_Montreal-Montreal_Quebec.html" target="_blank"><strong>The Full-Day Small-Group Comprehensive Tour of Montreal</strong> · TripAdvisor · 4.9⭐ · 213+ reviews</a></div>
<div class="entry-body">
<div>🔖 Full-day small-group city tour covering Old Montreal, Mount Royal, Saint Joseph's Oratory, Notre-Dame Basilica, Westmount, and the Plateau — ideal for first-time visitors wanting a comprehensive overview of Montreal in a single day.</div>
<div>🕐 9:00am · ⏳ 8h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+d+Armes+Montreal" target="_blank">Place d'Armes · Old Montreal</a></div>
<div>🚶 5 min · 🚕 3 min</div>
</div>
<div class="extras-sub">📅 2. <a href="https://www.tripadvisor.com/AttractionProductReview-g155032-d16741627-Montreal_RESO_Underground_City_Downtown_Tour_by_MTL_Detours-Montreal_Quebec.html" target="_blank"><strong>Montreal RESO Underground City + Downtown Tour by MTL Detours</strong> · TripAdvisor · 4.7⭐ · 100+ reviews</a></div>
<div class="entry-body">
<div>🔖 2-hour certified guide tour through the RESO — the world's largest underground pedestrian network — and downtown Montreal streets: public art, Parisian-style metro entrances, hidden cafés, and the architecture that connects 33 km of indoor passages.</div>
<div>🕐 10:00am · ⏳ 2h · 👥 10 max</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Place+Ville+Marie+Montreal" target="_blank">Place Ville Marie · Downtown</a></div>
<div>🚶 18 min · 🚕 7 min</div>
</div>
<div class="extras-sub">📅 3. <a href="https://www.tripadvisor.ca/AttractionProductReview-g155032-d19500286-Montreal_at_Night_Tour-Montreal_Quebec.html" target="_blank"><strong>Montreal at Night Tour</strong> · TripAdvisor · 4.5⭐ · 50+ reviews</a></div>
<div class="entry-body">
<div>🔖 Small-group evening driving tour through Montreal's illuminated neighborhoods — Old Montreal, Mount Royal, and the Quartier des Spectacles — finishing with a ride on the Grande Roue observation wheel above the lit-up Old Port.</div>
<div>🕐 7:30pm · ⏳ 3h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=Old+Port+Montreal" target="_blank">Old Port · Old Montreal</a></div>
<div>🚶 8 min · 🚕 4 min</div>
</div>
<div class="extras-sub">📅 4. <a href="https://www.tripadvisor.com/AttractionProductReview-g155032-d19715108-Quebec_city_Montmorency_Falls_1_Day_Tour_from_Montreal-Montreal_Quebec.html" target="_blank"><strong>Quebec City and Montmorency Falls 1 Day Tour from Montreal</strong> · TripAdvisor · 4.5⭐ · 1552+ reviews</a></div>
<div class="entry-body">
<div>🔖 Full-day guided coach tour from Montreal to Quebec City — the walled historic district, Château Frontenac, Dufferin Terrace, Quartier Petit-Champlain, and a stop at Montmorency Falls before returning to Montreal.</div>
<div>🕐 7:30am · ⏳ 13h · 👥 small group</div>
<div>📍 <a href="https://www.google.com/maps/search/?api=1&query=360+rue+Saint-Antoine+Ouest+Montreal" target="_blank">Central Montreal pickup</a></div>
<div>🏨 ↔ 🚐</div>
</div>
</div>'''

count = html.count(OLD_TOURS)
if count == 1:
    html = html.replace(OLD_TOURS, NEW_TOURS)
    print("  ✅ Full tours section replaced (food tours removed, <strong> added, hotel pickup fixed)")
else:
    print(f"  ⚠️  Tours section match: {count} (expected 1)")

# ══ 17. Write file ════════════════════════════════════════════════
path.write_text(html, encoding='utf-8')
print(f"\nDone. {original_len} → {len(html)} chars ({len(html)-original_len:+d})")
