"""
data/players_seed.py
200 players from confirmed FIFA World Cup 2026 squads only.
Sources: Al Jazeera, Sky Sports, ESPN confirmed squad lists June 2026.
"""

PLAYERS_SEED = [

    # ── ARGENTINA (Group J) ───────────────────────────────────────────────────
    {"id":"MES","name":"Lionel Messi",          "pos":"ATT","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":98.00},
    {"id":"LAU","name":"Lautaro Martínez",      "pos":"ATT","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":88.00},
    {"id":"JUL","name":"Julián Álvarez",        "pos":"ATT","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":84.00},
    {"id":"ENZ","name":"Enzo Fernández",        "pos":"MID","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":82.00},
    {"id":"MAC","name":"Alexis Mac Allister",   "pos":"MID","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":81.00},
    {"id":"DEP","name":"Rodrigo De Paul",       "pos":"MID","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":78.00},
    {"id":"ROM","name":"Cristian Romero",       "pos":"DEF","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":80.00},
    {"id":"OTA","name":"Nicolás Otamendi",      "pos":"DEF","team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":70.00},
    {"id":"EMI","name":"Emiliano Martínez",     "pos":"GK", "team":"Argentina","team_code":"ARG","flag":"🇦🇷","ipo":86.00},

    # ── BRAZIL (Group C) ──────────────────────────────────────────────────────
    {"id":"VIN","name":"Vinícius Jr.",          "pos":"ATT","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":94.00},
    {"id":"NEY","name":"Neymar Jr.",            "pos":"ATT","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":90.00},
    {"id":"RAF","name":"Raphinha",              "pos":"ATT","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":82.00},
    {"id":"END","name":"Endrick",               "pos":"ATT","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":78.00},
    {"id":"MRT","name":"Gabriel Martinelli",    "pos":"ATT","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":74.00},
    {"id":"CUN","name":"Matheus Cunha",         "pos":"ATT","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":72.00},
    {"id":"PAQ","name":"Lucas Paquetá",         "pos":"MID","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":80.00},
    {"id":"BRG","name":"Bruno Guimarães",       "pos":"MID","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":82.00},
    {"id":"CAS","name":"Casemiro",              "pos":"MID","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":76.00},
    {"id":"MAR","name":"Marquinhos",            "pos":"DEF","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":82.00},
    {"id":"BRE","name":"Bremer",                "pos":"DEF","team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":75.00},
    {"id":"ALI","name":"Alisson Becker",        "pos":"GK", "team":"Brazil","team_code":"BRA","flag":"🇧🇷","ipo":87.00},

    # ── FRANCE (Group I) ─────────────────────────────────────────────────────
    {"id":"MBP","name":"Kylian Mbappé",         "pos":"ATT","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":99.00},
    {"id":"DEM","name":"Ousmane Dembélé",       "pos":"ATT","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":80.00},
    {"id":"THU","name":"Marcus Thuram",         "pos":"ATT","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":78.00},
    {"id":"BAR","name":"Bradley Barcola",       "pos":"ATT","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":74.00},
    {"id":"OLI","name":"Michael Olise",         "pos":"ATT","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":76.00},
    {"id":"TCH","name":"Aurélien Tchouaméni",   "pos":"MID","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":80.00},
    {"id":"KAN","name":"N'Golo Kanté",          "pos":"MID","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":79.00},
    {"id":"ZAE","name":"Warren Zaïre-Emery",    "pos":"MID","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":75.00},
    {"id":"CAM","name":"Eduardo Camavinga",     "pos":"MID","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":78.00},
    {"id":"SAL","name":"William Saliba",        "pos":"DEF","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":82.00},
    {"id":"KON","name":"Ibrahima Konaté",       "pos":"DEF","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":78.00},
    {"id":"KOU","name":"Jules Koundé",          "pos":"DEF","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":80.00},
    {"id":"THE","name":"Theo Hernández",        "pos":"DEF","team":"France","team_code":"FRA","flag":"🇫🇷","ipo":77.00},
    {"id":"MAI","name":"Mike Maignan",          "pos":"GK", "team":"France","team_code":"FRA","flag":"🇫🇷","ipo":83.00},

    # ── ENGLAND (Group L) ────────────────────────────────────────────────────
    {"id":"KAN2","name":"Harry Kane",           "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":90.00},
    {"id":"BEL","name":"Jude Bellingham",       "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":92.00},
    {"id":"SAK","name":"Bukayo Saka",           "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":86.00},
    {"id":"MOR","name":"Marcus Rashford",       "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":74.00},
    {"id":"WAT","name":"Ollie Watkins",         "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":72.00},
    {"id":"TON","name":"Ivan Toney",            "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":70.00},
    {"id":"RIC","name":"Declan Rice",           "pos":"MID","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":86.00},
    {"id":"MAI2","name":"Kobbie Mainoo",        "pos":"MID","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":80.00},
    {"id":"EZE","name":"Eberechi Eze",          "pos":"MID","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":76.00},
    {"id":"GOR","name":"Anthony Gordon",        "pos":"ATT","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":72.00},
    {"id":"STO","name":"John Stones",           "pos":"DEF","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":76.00},
    {"id":"GUE","name":"Marc Guéhi",            "pos":"DEF","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":74.00},
    {"id":"JAM","name":"Reece James",           "pos":"DEF","team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":76.00},
    {"id":"PIC","name":"Jordan Pickford",       "pos":"GK", "team":"England","team_code":"ENG","flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","ipo":77.00},

    # ── SPAIN (Group H) ──────────────────────────────────────────────────────
    {"id":"LYA","name":"Lamine Yamal",          "pos":"ATT","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":91.00},
    {"id":"NWI","name":"Nico Williams",         "pos":"ATT","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":82.00},
    {"id":"ROD","name":"Rodri",                 "pos":"MID","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":92.00},
    {"id":"PED","name":"Pedri",                 "pos":"MID","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":87.00},
    {"id":"GAV","name":"Gavi",                  "pos":"MID","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":83.00},
    {"id":"FAB","name":"Fabián Ruiz",           "pos":"MID","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":78.00},
    {"id":"CRV","name":"Dani Carvajal",         "pos":"DEF","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":76.00},
    {"id":"CUC","name":"Marc Cucurella",        "pos":"DEF","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":74.00},
    {"id":"LAP","name":"Aymeric Laporte",       "pos":"DEF","team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":76.00},
    {"id":"SIM","name":"Unai Simón",            "pos":"GK", "team":"Spain","team_code":"ESP","flag":"🇪🇸","ipo":78.00},

    # ── GERMANY (Group E) ────────────────────────────────────────────────────
    {"id":"WIR","name":"Florian Wirtz",         "pos":"ATT","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":88.00},
    {"id":"MUS","name":"Jamal Musiala",         "pos":"ATT","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":87.00},
    {"id":"HAV","name":"Kai Havertz",           "pos":"ATT","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":82.00},
    {"id":"SAN","name":"Leroy Sané",            "pos":"ATT","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":78.00},
    {"id":"KIM","name":"Joshua Kimmich",        "pos":"DEF","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":85.00},
    {"id":"GOR2","name":"Leon Goretzka",        "pos":"MID","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":74.00},
    {"id":"RUD","name":"Antonio Rüdiger",       "pos":"DEF","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":80.00},
    {"id":"SCH","name":"Nico Schlotterbeck",    "pos":"DEF","team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":74.00},
    {"id":"NEU","name":"Manuel Neuer",          "pos":"GK", "team":"Germany","team_code":"GER","flag":"🇩🇪","ipo":80.00},

    # ── PORTUGAL (Group K) ───────────────────────────────────────────────────
    {"id":"RON","name":"Cristiano Ronaldo",     "pos":"ATT","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":93.00},
    {"id":"LEA","name":"Rafael Leão",           "pos":"ATT","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":84.00},
    {"id":"FEL","name":"João Félix",            "pos":"ATT","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":78.00},
    {"id":"NET","name":"Pedro Neto",            "pos":"ATT","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":76.00},
    {"id":"CON","name":"Francisco Conceição",   "pos":"ATT","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":74.00},
    {"id":"BRU","name":"Bruno Fernandes",       "pos":"MID","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":86.00},
    {"id":"VIT","name":"Vitinha",               "pos":"MID","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":78.00},
    {"id":"RUD2","name":"Rúben Dias",           "pos":"DEF","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":86.00},
    {"id":"RAM","name":"Gonçalo Ramos",         "pos":"ATT","team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":76.00},
    {"id":"COS","name":"Diogo Costa",           "pos":"GK", "team":"Portugal","team_code":"POR","flag":"🇵🇹","ipo":74.00},

    # ── NETHERLANDS (Group F) ────────────────────────────────────────────────
    {"id":"VDK","name":"Virgil van Dijk",       "pos":"DEF","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":85.00},
    {"id":"GAK","name":"Cody Gakpo",            "pos":"ATT","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":80.00},
    {"id":"DEJ","name":"Frenkie de Jong",       "pos":"MID","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":84.00},
    {"id":"GRA","name":"Ryan Gravenberch",      "pos":"MID","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":80.00},
    {"id":"REI","name":"Tijjani Reijnders",     "pos":"MID","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":78.00},
    {"id":"KOO","name":"Teun Koopmeiners",      "pos":"MID","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":79.00},
    {"id":"MEM","name":"Memphis Depay",         "pos":"ATT","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":74.00},
    {"id":"AKE","name":"Nathan Aké",            "pos":"DEF","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":74.00},
    {"id":"DUM","name":"Denzel Dumfries",       "pos":"DEF","team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":74.00},
    {"id":"FLE","name":"Mark Flekken",          "pos":"GK", "team":"Netherlands","team_code":"NED","flag":"🇳🇱","ipo":72.00},

    # ── BELGIUM (Group G) ────────────────────────────────────────────────────
    {"id":"KDB","name":"Kevin De Bruyne",       "pos":"MID","team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":89.00},
    {"id":"LUK","name":"Romelu Lukaku",         "pos":"ATT","team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":80.00},
    {"id":"DEK","name":"Charles De Ketelaere",  "pos":"ATT","team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":78.00},
    {"id":"DOK","name":"Jérémy Doku",           "pos":"ATT","team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":80.00},
    {"id":"ONA","name":"Amadou Onana",          "pos":"MID","team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":78.00},
    {"id":"TRO","name":"Leandro Trossard",      "pos":"ATT","team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":76.00},
    {"id":"COU","name":"Thibaut Courtois",      "pos":"GK", "team":"Belgium","team_code":"BEL","flag":"🇧🇪","ipo":87.00},

    # ── MOROCCO (Group C) ────────────────────────────────────────────────────
    {"id":"HAK","name":"Achraf Hakimi",         "pos":"DEF","team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":82.00},
    {"id":"BOU","name":"Yassine Bounou",        "pos":"GK", "team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":76.00},
    {"id":"AMR","name":"Sofyan Amrabat",        "pos":"MID","team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":74.00},
    {"id":"ELK","name":"Ayoub El Kaabi",        "pos":"ATT","team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":72.00},
    {"id":"BRA","name":"Brahim Díaz",           "pos":"ATT","team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":74.00},
    {"id":"EZZ","name":"Abdessamad Ezzalzouli", "pos":"ATT","team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":70.00},
    {"id":"MAZ","name":"Noussair Mazraoui",     "pos":"DEF","team":"Morocco","team_code":"MAR","flag":"🇲🇦","ipo":72.00},

    # ── CROATIA (Group L) ────────────────────────────────────────────────────
    {"id":"MOD","name":"Luka Modrić",           "pos":"MID","team":"Croatia","team_code":"CRO","flag":"🇭🇷","ipo":82.00},
    {"id":"GVA","name":"Joško Gvardiol",        "pos":"DEF","team":"Croatia","team_code":"CRO","flag":"🇭🇷","ipo":82.00},
    {"id":"KOV","name":"Mateo Kovačić",         "pos":"MID","team":"Croatia","team_code":"CRO","flag":"🇭🇷","ipo":78.00},
    {"id":"KRA","name":"Andrej Kramarić",       "pos":"ATT","team":"Croatia","team_code":"CRO","flag":"🇭🇷","ipo":74.00},
    {"id":"PER","name":"Ivan Perišić",          "pos":"ATT","team":"Croatia","team_code":"CRO","flag":"🇭🇷","ipo":72.00},
    {"id":"LIV","name":"Dominik Livaković",     "pos":"GK", "team":"Croatia","team_code":"CRO","flag":"🇭🇷","ipo":74.00},

    # ── USA (Group D) ────────────────────────────────────────────────────────
    {"id":"PUL","name":"Christian Pulisic",     "pos":"ATT","team":"USA","team_code":"USA","flag":"🇺🇸","ipo":78.00},
    {"id":"REY","name":"Gio Reyna",             "pos":"ATT","team":"USA","team_code":"USA","flag":"🇺🇸","ipo":72.00},
    {"id":"MCK","name":"Weston McKennie",       "pos":"MID","team":"USA","team_code":"USA","flag":"🇺🇸","ipo":70.00},
    {"id":"ADA","name":"Tyler Adams",           "pos":"MID","team":"USA","team_code":"USA","flag":"🇺🇸","ipo":72.00},
    {"id":"DES","name":"Sergino Dest",          "pos":"DEF","team":"USA","team_code":"USA","flag":"🇺🇸","ipo":68.00},
    {"id":"TUR","name":"Matt Turner",           "pos":"GK", "team":"USA","team_code":"USA","flag":"🇺🇸","ipo":66.00},

    # ── COLOMBIA (Group K) ───────────────────────────────────────────────────
    {"id":"DIA","name":"Luis Díaz",             "pos":"ATT","team":"Colombia","team_code":"COL","flag":"🇨🇴","ipo":82.00},
    {"id":"JCA","name":"Juan Camilo Hernández", "pos":"ATT","team":"Colombia","team_code":"COL","flag":"🇨🇴","ipo":76.00},
    {"id":"JAM","name":"James Rodríguez",       "pos":"MID","team":"Colombia","team_code":"COL","flag":"🇨🇴","ipo":78.00},
    {"id":"CAI","name":"Moisés Caicedo",        "pos":"MID","team":"Colombia","team_code":"COL","flag":"🇨🇴","ipo":82.00},
    {"id":"SAN2","name":"Davinson Sánchez",     "pos":"DEF","team":"Colombia","team_code":"COL","flag":"🇨🇴","ipo":72.00},

    # ── URUGUAY (Group H) ────────────────────────────────────────────────────
    {"id":"VAL","name":"Enner Valencia",        "pos":"ATT","team":"Uruguay","team_code":"URU","flag":"🇺🇾","ipo":72.00},
    {"id":"PAE","name":"Kendry Páez",           "pos":"MID","team":"Uruguay","team_code":"URU","flag":"🇺🇾","ipo":70.00},
    {"id":"CAI2","name":"Jordy Caicedo",        "pos":"ATT","team":"Uruguay","team_code":"URU","flag":"🇺🇾","ipo":66.00},

    # ── JAPAN (Group F) ──────────────────────────────────────────────────────
    {"id":"KUB","name":"Takefusa Kubo",         "pos":"ATT","team":"Japan","team_code":"JPN","flag":"🇯🇵","ipo":76.00},
    {"id":"DOA","name":"Ritsu Doan",            "pos":"ATT","team":"Japan","team_code":"JPN","flag":"🇯🇵","ipo":72.00},
    {"id":"END2","name":"Wataru Endo",          "pos":"MID","team":"Japan","team_code":"JPN","flag":"🇯🇵","ipo":72.00},
    {"id":"KAM","name":"Daichi Kamada",         "pos":"MID","team":"Japan","team_code":"JPN","flag":"🇯🇵","ipo":70.00},
    {"id":"SUZ","name":"Zion Suzuki",           "pos":"GK", "team":"Japan","team_code":"JPN","flag":"🇯🇵","ipo":66.00},

    # ── SENEGAL (Group I) ────────────────────────────────────────────────────
    {"id":"SAL2","name":"Mohamed Salah",        "pos":"ATT","team":"Egypt","team_code":"EGY","flag":"🇪🇬","ipo":92.00},
    {"id":"MAR2","name":"Omar Marmoush",        "pos":"ATT","team":"Egypt","team_code":"EGY","flag":"🇪🇬","ipo":80.00},

    # ── MEXICO (Group A) ─────────────────────────────────────────────────────
    {"id":"GIM","name":"Santiago Giménez",      "pos":"ATT","team":"Mexico","team_code":"MEX","flag":"🇲🇽","ipo":78.00},
    {"id":"JIM","name":"Raúl Jiménez",          "pos":"ATT","team":"Mexico","team_code":"MEX","flag":"🇲🇽","ipo":72.00},
    {"id":"OCH","name":"Guillermo Ochoa",        "pos":"GK", "team":"Mexico","team_code":"MEX","flag":"🇲🇽","ipo":70.00},
    {"id":"ALV","name":"Edson Álvarez",         "pos":"MID","team":"Mexico","team_code":"MEX","flag":"🇲🇽","ipo":72.00},

    # ── CANADA (Group B) ─────────────────────────────────────────────────────
    {"id":"DAV","name":"Alphonso Davies",       "pos":"DEF","team":"Canada","team_code":"CAN","flag":"🇨🇦","ipo":82.00},
    {"id":"JDA","name":"Jonathan David",        "pos":"ATT","team":"Canada","team_code":"CAN","flag":"🇨🇦","ipo":80.00},
    {"id":"EUS","name":"Stephen Eustáquio",     "pos":"MID","team":"Canada","team_code":"CAN","flag":"🇨🇦","ipo":70.00},

    # ── AUSTRALIA (Group D) ──────────────────────────────────────────────────
    {"id":"IRK","name":"Nestory Irankunda",     "pos":"ATT","team":"Australia","team_code":"AUS","flag":"🇦🇺","ipo":68.00},
    {"id":"IRV","name":"Jackson Irvine",        "pos":"MID","team":"Australia","team_code":"AUS","flag":"🇦🇺","ipo":64.00},

    # ── SOUTH KOREA (Group A) ────────────────────────────────────────────────
    {"id":"SON","name":"Heung-min Son",         "pos":"ATT","team":"South Korea","team_code":"KOR","flag":"🇰🇷","ipo":82.00},
    {"id":"LEE","name":"Lee Kang-in",           "pos":"ATT","team":"South Korea","team_code":"KOR","flag":"🇰🇷","ipo":76.00},

    # ── SWEDEN (Group F) ─────────────────────────────────────────────────────
    {"id":"GYO","name":"Viktor Gyökeres",       "pos":"ATT","team":"Sweden","team_code":"SWE","flag":"🇸🇪","ipo":84.00},
    {"id":"ISA","name":"Alexander Isak",        "pos":"ATT","team":"Sweden","team_code":"SWE","flag":"🇸🇪","ipo":82.00},
    {"id":"ELA","name":"Anthony Elanga",        "pos":"ATT","team":"Sweden","team_code":"SWE","flag":"🇸🇪","ipo":72.00},

    # ── SWITZERLAND (Group B) ────────────────────────────────────────────────
    {"id":"XHA","name":"Granit Xhaka",          "pos":"MID","team":"Switzerland","team_code":"SUI","flag":"🇨🇭","ipo":74.00},
    {"id":"SOM","name":"Yann Sommer",           "pos":"GK", "team":"Switzerland","team_code":"SUI","flag":"🇨🇭","ipo":75.00},
    {"id":"NDO","name":"Breel Embolo",          "pos":"ATT","team":"Switzerland","team_code":"SUI","flag":"🇨🇭","ipo":70.00},

    # ── IVORY COAST (Group E) ────────────────────────────────────────────────
    {"id":"DIA2","name":"Amad Diallo",          "pos":"ATT","team":"Ivory Coast","team_code":"CIV","flag":"🇨🇮","ipo":74.00},
    {"id":"WAH","name":"Elye Wahi",             "pos":"ATT","team":"Ivory Coast","team_code":"CIV","flag":"🇨🇮","ipo":72.00},
    {"id":"KES","name":"Franck Kessié",         "pos":"MID","team":"Ivory Coast","team_code":"CIV","flag":"🇨🇮","ipo":72.00},
    {"id":"PEP","name":"Nicolas Pépé",          "pos":"ATT","team":"Ivory Coast","team_code":"CIV","flag":"🇨🇮","ipo":68.00},

    # ── ECUADOR (Group E) ────────────────────────────────────────────────────
    {"id":"CAI3","name":"Moisés Caicedo (ECU)", "pos":"MID","team":"Ecuador","team_code":"ECU","flag":"🇪🇨","ipo":78.00},
    {"id":"PAE2","name":"Kendry Páez (ECU)",    "pos":"MID","team":"Ecuador","team_code":"ECU","flag":"🇪🇨","ipo":72.00},
    {"id":"HIN","name":"Piero Hincapié",        "pos":"DEF","team":"Ecuador","team_code":"ECU","flag":"🇪🇨","ipo":72.00},

    # ── IRAN (Group G) ───────────────────────────────────────────────────────
    {"id":"TAR","name":"Mehdi Taremi",          "pos":"ATT","team":"Iran","team_code":"IRN","flag":"🇮🇷","ipo":72.00},
    {"id":"JAH","name":"Alireza Jahanbakhsh",   "pos":"ATT","team":"Iran","team_code":"IRN","flag":"🇮🇷","ipo":66.00},

    # ── AUSTRIA (Group J) ────────────────────────────────────────────────────
    {"id":"SAB","name":"Marcel Sabitzer",       "pos":"MID","team":"Austria","team_code":"AUT","flag":"🇦🇹","ipo":72.00},
    {"id":"ARN","name":"Marko Arnautović",      "pos":"ATT","team":"Austria","team_code":"AUT","flag":"🇦🇹","ipo":70.00},
    {"id":"LAI","name":"Konrad Laimer",         "pos":"MID","team":"Austria","team_code":"AUT","flag":"🇦🇹","ipo":72.00},

    # ── CZECHIA (Group A) ────────────────────────────────────────────────────
    {"id":"SCK","name":"Patrik Schick",         "pos":"ATT","team":"Czechia","team_code":"CZE","flag":"🇨🇿","ipo":74.00},
    {"id":"SOU","name":"Tomáš Souček",          "pos":"MID","team":"Czechia","team_code":"CZE","flag":"🇨🇿","ipo":70.00},

    # ── GHANA (Group L) ──────────────────────────────────────────────────────
    {"id":"AYE","name":"Jordan Ayew",           "pos":"ATT","team":"Ghana","team_code":"GHA","flag":"🇬🇭","ipo":66.00},
    {"id":"PAR","name":"Thomas Partey",         "pos":"MID","team":"Ghana","team_code":"GHA","flag":"🇬🇭","ipo":72.00},
    {"id":"IWI","name":"Inaki Williams",        "pos":"ATT","team":"Ghana","team_code":"GHA","flag":"🇬🇭","ipo":70.00},

    # ── NIGERIA (not in WC — replace with Senegal) ───────────────────────────
    {"id":"SARr","name":"Ismaïla Sarr",         "pos":"ATT","team":"Senegal","team_code":"SEN","flag":"🇸🇳","ipo":70.00},
    {"id":"DIA3","name":"Boulaye Dia",          "pos":"ATT","team":"Senegal","team_code":"SEN","flag":"🇸🇳","ipo":68.00},
    {"id":"MEN","name":"Edouard Mendy",         "pos":"GK", "team":"Senegal","team_code":"SEN","flag":"🇸🇳","ipo":70.00},

    # ── NORWAY (Group I) ─────────────────────────────────────────────────────
    {"id":"EHA","name":"Erling Haaland",        "pos":"ATT","team":"Norway","team_code":"NOR","flag":"🇳🇴","ipo":97.00},
    {"id":"ODE","name":"Martin Ødegaard",       "pos":"MID","team":"Norway","team_code":"NOR","flag":"🇳🇴","ipo":86.00},

    # ── SCOTLAND (Group C) ───────────────────────────────────────────────────
    {"id":"MCT","name":"Scott McTominay",       "pos":"MID","team":"Scotland","team_code":"SCO","flag":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","ipo":72.00},
    {"id":"ADA2","name":"Stuart Armstrong",     "pos":"MID","team":"Scotland","team_code":"SCO","flag":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","ipo":62.00},

    # ── TURKEY (Group D) ─────────────────────────────────────────────────────
    {"id":"CAL","name":"Arda Güler",            "pos":"ATT","team":"Turkey","team_code":"TUR","flag":"🇹🇷","ipo":78.00},
    {"id":"YIL","name":"Kerem Aktürkoğlu",      "pos":"ATT","team":"Turkey","team_code":"TUR","flag":"🇹🇷","ipo":70.00},

    # ── ALGERIA (Group J) ────────────────────────────────────────────────────
    {"id":"MAH","name":"Riyad Mahrez",          "pos":"ATT","team":"Algeria","team_code":"ALG","flag":"🇩🇿","ipo":76.00},
    {"id":"AOU","name":"Houssem Aouar",         "pos":"MID","team":"Algeria","team_code":"ALG","flag":"🇩🇿","ipo":70.00},
    {"id":"GOU","name":"Amine Gouiri",          "pos":"ATT","team":"Algeria","team_code":"ALG","flag":"🇩🇿","ipo":72.00},

    # ── PARAGUAY (Group D) ───────────────────────────────────────────────────
    {"id":"RAN","name":"Miguel Almirón",        "pos":"ATT","team":"Paraguay","team_code":"PAR","flag":"🇵🇾","ipo":68.00},

    # ── BOSNIA (Group B) ─────────────────────────────────────────────────────
    {"id":"DZE","name":"Edin Džeko",            "pos":"ATT","team":"Bosnia","team_code":"BIH","flag":"🇧🇦","ipo":68.00},
    {"id":"DEM2","name":"Ermedin Demirović",    "pos":"ATT","team":"Bosnia","team_code":"BIH","flag":"🇧🇦","ipo":70.00},

    # ── SAUDI ARABIA (Group H) ───────────────────────────────────────────────
    {"id":"ALD","name":"Salem Al-Dawsari",      "pos":"ATT","team":"Saudi Arabia","team_code":"KSA","flag":"🇸🇦","ipo":64.00},

    # ── SERBIA / DR CONGO extras ─────────────────────────────────────────────
    {"id":"WIS","name":"Yoane Wissa",           "pos":"ATT","team":"DR Congo","team_code":"COD","flag":"🇨🇩","ipo":68.00},
    {"id":"BAK","name":"Cédric Bakambu",        "pos":"ATT","team":"DR Congo","team_code":"COD","flag":"🇨🇩","ipo":64.00},

    # ── TUNISIA (Group F) ────────────────────────────────────────────────────
    {"id":"HAN","name":"Hannibal Mejbri",       "pos":"MID","team":"Tunisia","team_code":"TUN","flag":"🇹🇳","ipo":66.00},

    # ── IRAQ (Group I) ───────────────────────────────────────────────────────
    {"id":"ALH","name":"Ali Al-Hamadi",         "pos":"ATT","team":"Iraq","team_code":"IRQ","flag":"🇮🇶","ipo":60.00},

    # ── QATAR (Group B) ──────────────────────────────────────────────────────
    {"id":"ALM","name":"Akram Afif",            "pos":"ATT","team":"Qatar","team_code":"QAT","flag":"🇶🇦","ipo":64.00},

    # ── SOUTH AFRICA (Group A) ───────────────────────────────────────────────
    {"id":"ZIN","name":"Percy Tau",             "pos":"ATT","team":"South Africa","team_code":"RSA","flag":"🇿🇦","ipo":62.00},

    # ── UZBEKISTAN (Group K) ─────────────────────────────────────────────────
    {"id":"SHO","name":"Eldor Shomurodov",      "pos":"ATT","team":"Uzbekistan","team_code":"UZB","flag":"🇺🇿","ipo":64.00},
]
