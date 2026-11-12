"""Historical North Africa railway layout, as it stood 1936-1939 (pre-war).

Each line: name, level, stations = [(name, lat, lon)].  PINS binds a station name to a
province id (named VP cities) so the lat/lon projection error cannot misplace them.
Fact-checked per region against Wikipedia (2026-11-10). Level: 3 double-track trunk,
2 main single-track/standard-gauge trunk, 1 branch/narrow/metre/Italian 950 mm/Cape gauge.
Not included on purpose (wartime or post-1939): Matruh-Misheifa-Capuzzo-Belhamed extension,
El Ferdan Canal bridge (1941), Kassala-Tessenei (1941), Safaga-Qena, Sennar-Damazin, all
post-war Sudan lines, the Tripoli-Benghazi military line (never built), Misrata station.
"""

PINS = {
    'Algiers': 1145, 'Oran': 7132, 'Casablanca': 7069, 'Marrakech': 4108, 'Constantine': 12051,
    'Annaba': 7081, 'Batna': 12034, 'Tunis': 11969, 'Bizerte': 9994, 'Sfax': 7162, 'Gabes': 7005,
    'Kasserine': 1141, 'Tripoli': 1149, 'Benghazi': 11954, 'Alexandria': 4076, 'Cairo': 7011,
    'Port Said': 10869, 'Suez': 4073, 'Asyut': 11974, 'Luxor': 7073, 'Aswan': 11999,
    'Mersa Matruh': 11967, 'El Alamein': 1071, 'Khartoum': 12806, 'Port Sudan': 12725,
    'El Obeid': 10827, 'Djelfa': 13579,
}

L = []


def line(name, level, *stations):
    L.append(dict(name=name, level=level, stations=list(stations)))


# ---------------------------------------------------------------- EGYPT (ESR, 1,435 mm)
line('Egypt: Alexandria-Damanhur-Tanta-Benha-Cairo', 3,
     ('Alexandria', 31.20, 29.92), ('Damanhur', 31.04, 30.47), ('Tanta', 30.79, 31.00),
     ('Benha', 30.46, 31.18), ('Cairo', 30.04, 31.24))
line('Egypt: Cairo-Zagazig-Ismailia', 3,
     ('Cairo', 30.04, 31.24), ('Zagazig', 30.59, 31.50), ('Ismailia', 30.60, 32.27))
line('Egypt: Ismailia-Suez', 2,
     ('Ismailia', 30.60, 32.27), ('Suez', 29.97, 32.55))
line('Egypt: Ismailia-Qantara-Port Said', 2,
     ('Ismailia', 30.60, 32.27), ('Qantara West', 30.86, 32.31), ('Port Said', 31.26, 32.30))
line('Egypt: Tanta-Mahalla-Mansura-Damietta', 2,
     ('Tanta', 30.79, 31.00), ('Mahalla el-Kubra', 30.97, 31.16), ('Mansura', 31.04, 31.38),
     ('Damietta', 31.42, 31.81))
line('Egypt: Tanta-Zifta-Zagazig', 1,
     ('Tanta', 30.79, 31.00), ('Zifta', 30.71, 31.24), ('Zagazig', 30.59, 31.50))
line('Egypt: Benha-Zagazig', 1,
     ('Benha', 30.46, 31.18), ('Zagazig', 30.59, 31.50))
line('Egypt: Tanta-Kafr el Sheikh-Desouk-Damanhur', 1,
     ('Tanta', 30.79, 31.00), ('Kafr el-Sheikh', 31.11, 30.95), ('Desouk', 31.14, 30.65),
     ('Damanhur', 31.04, 30.47))
line('Egypt: Benha-Shibin el Kom-Menouf', 1,
     ('Benha', 30.46, 31.18), ('Shibin el Kom', 30.56, 31.01), ('Menouf', 30.47, 30.93))
line('Egypt: Alexandria-Abu Qir-Edku-Rosetta', 1,
     ('Alexandria', 31.20, 29.92), ('Abu Qir', 31.32, 30.07), ('Edku', 31.30, 30.30),
     ('Rosetta', 31.40, 30.42))
line('Egypt: Cairo-Beni Suef-Minya-Asyut', 2,
     ('Cairo', 30.04, 31.24), ('Beni Suef', 29.07, 31.10), ('Minya', 28.11, 30.75), ('Asyut', 27.18, 31.18))
line('Egypt: Asyut-Luxor-Aswan', 2,
     ('Asyut', 27.18, 31.18), ('Luxor', 25.70, 32.64), ('Aswan', 24.09, 32.90))
line('Egypt: Wasta-Fayum branch', 1,
     ('Wasta', 29.33, 31.20), ('Fayum', 29.31, 30.84))
line('Egypt: Alexandria-Alamein-Mersa Matruh (Western Desert line)', 1,
     ('Alexandria', 31.20, 29.92), ('Burg el Arab', 30.88, 29.55), ('El Alamein', 30.83, 28.95),
     ('Daba', 30.93, 28.46), ('Fuka', 31.07, 27.83), ('Mersa Matruh', 31.35, 27.23))
line('Sinai: Kantara East-El Arish-Rafah (Palestine Railways)', 1,
     ('Kantara East', 30.87, 32.35), ('Bir el Abd', 31.02, 32.98), ('El Arish', 31.13, 33.80),
     ('Rafah', 31.28, 34.25), ('Gaza', 31.50, 34.47))

# ---------------------------------------------------------------- SUDAN (1,067 mm)
line('Sudan: Wadi Halfa-Abu Hamed-Atbara-Shendi-Khartoum', 1,
     ('Wadi Halfa', 21.80, 31.37), ('Abu Hamed', 19.54, 33.34), ('Berber', 18.03, 33.99),
     ('Atbara', 17.70, 33.97), ('Ad Damer', 17.59, 33.96), ('Shendi', 16.69, 33.43),
     ('Khartoum', 15.60, 32.53))
line('Sudan: Abu Hamed-Kareima branch', 1,
     ('Abu Hamed', 19.54, 33.34), ('Kareima', 18.55, 31.85))
line('Sudan: Atbara-Haiya-Port Sudan', 1,
     ('Atbara', 17.70, 33.97), ('Haiya', 18.35, 36.40), ('Sinkat', 18.83, 36.83),
     ('Gebeit', 18.96, 36.83), ('Port Sudan', 19.60, 37.21))
line('Sudan: Haiya-Kassala-Gedaref-Sennar', 1,
     ('Haiya', 18.35, 36.40), ('Kassala', 15.45, 36.40), ('Gedaref', 14.03, 35.38), ('Sennar', 13.55, 33.62))
line('Sudan: Khartoum-Wad Medani-Sennar-Kosti-El Obeid', 1,
     ('Khartoum', 15.60, 32.53), ('Wad Medani', 14.40, 33.52), ('Sennar', 13.55, 33.62),
     ('Kosti', 13.17, 32.66), ('Er Rahad', 12.70, 30.65), ('El Obeid', 13.18, 30.22))

# ---------------------------------------------------------------- LIBYA (Italian 950 mm stubs)
line('Libya: Tripoli-Sabratha-Zuara', 1,
     ('Tripoli', 32.89, 13.19), ('Zawiya', 32.76, 12.73), ('Sabratha', 32.79, 12.48), ('Zuara', 32.93, 12.08))
line('Libya: Tripoli-Azizia-Garian', 1,
     ('Tripoli', 32.89, 13.19), ('Azizia', 32.53, 13.01), ('Garian', 32.17, 13.02))
line('Libya: Tripoli-Tagiura', 1,
     ('Tripoli', 32.89, 13.19), ('Tagiura', 32.88, 13.35))
line('Libya: Benghazi-Benina-El Abiar-Barce', 1,
     ('Benghazi', 32.12, 20.07), ('Benina', 32.08, 20.26), ('El Abiar', 32.19, 20.60), ('Barce', 32.49, 20.83))
line('Libya: Benghazi-Soluch', 1,
     ('Benghazi', 32.12, 20.07), ('Soluch', 31.66, 20.25))

# ---------------------------------------------------------------- TUNISIA
line('Tunisia: Ghardimaou-Souk el Arba-Beja-Medjez-Tunis (standard gauge)', 2,
     ('Ghardimaou', 36.45, 8.44), ('Souk el Arba', 36.50, 8.78), ('Beja', 36.73, 9.18),
     ('Medjez el Bab', 36.65, 9.61), ('Tebourba', 36.83, 9.84), ('Tunis', 36.80, 10.18))
line('Tunisia: Djedeida-Mateur-Bizerte', 2,
     ('Djedeida', 36.83, 9.92), ('Mateur', 37.04, 9.66), ('Bizerte', 37.27, 9.87))
line('Tunisia: Beja-Mateur', 1,
     ('Beja', 36.73, 9.18), ('Mateur', 37.04, 9.66))
line('Tunisia: Mateur-Sedjenane-Nefza-Tabarka', 1,
     ('Mateur', 37.04, 9.66), ('Sedjenane', 37.05, 9.23), ('Nefza', 36.97, 9.08), ('Tabarka', 36.95, 8.76))
line('Tunisia: Tunis-Sousse-Sfax-Gabes (metre gauge coastal line)', 2,
     ('Tunis', 36.80, 10.18), ('Hammam-Lif', 36.73, 10.34), ('Enfidha', 36.13, 10.38),
     ('Sousse', 35.83, 10.64), ('El Djem', 35.30, 10.71), ('Sfax', 34.74, 10.76),
     ('Skhira', 34.30, 10.07), ('Gabes', 33.88, 10.10))
line('Tunisia: Tunis-Pont du Fahs-Dahmani-Le Kef', 1,
     ('Tunis', 36.80, 10.18), ('Pont du Fahs', 36.38, 9.90), ('Bou Arada', 36.35, 9.62),
     ('Gaafour', 36.34, 9.32), ('Dahmani', 35.94, 8.83), ('Le Kef', 36.18, 8.71))
line('Tunisia: Dahmani-Kalaat Khasba', 1,
     ('Dahmani', 35.94, 8.83), ('Kalaat Khasba', 35.67, 8.58))
line('Tunisia: Tunis-Zaghouan', 1,
     ('Tunis', 36.80, 10.18), ('Zaghouan', 36.41, 10.14))
line('Tunisia: Tunis-Grombalia-Nabeul (Cap Bon branch)', 1,
     ('Tunis', 36.80, 10.18), ('Bir Bou Regba', 36.40, 10.55), ('Nabeul', 36.45, 10.73))
line('Tunisia: Sousse-Moknine-Mahdia', 1,
     ('Sousse', 35.83, 10.64), ('Moknine', 35.63, 10.90), ('Mahdia', 35.50, 11.07))
line('Tunisia: Sousse-Kairouan-Sbeitla-Kasserine-Feriana-Metlaoui', 1,
     ('Sousse', 35.83, 10.64), ('Kairouan', 35.68, 10.10), ('Jilma', 35.27, 9.43), ('Sbeitla', 35.23, 9.12),
     ('Kasserine', 35.17, 8.83), ('Feriana', 34.95, 8.57), ('Metlaoui', 34.32, 8.40))
line('Tunisia: Sfax-Maknassy-Gafsa-Metlaoui-Tozeur (phosphate railway)', 1,
     ('Sfax', 34.74, 10.76), ('Mezzouna', 34.58, 9.83), ('Maknassy', 34.62, 9.60), ('Gafsa', 34.42, 8.78),
     ('Metlaoui', 34.32, 8.40), ('Tozeur', 33.92, 8.13))
line('Tunisia: Metlaoui-Redeyef', 1,
     ('Metlaoui', 34.32, 8.40), ('Redeyef', 34.38, 8.15))

# ---------------------------------------------------------------- ALGERIA
line('Algeria: Oran-Relizane-Chlef-Blida-Algiers', 2,
     ('Oran', 35.70, -0.63), ('Relizane', 35.74, 0.55), ('Chlef', 36.16, 1.33),
     ('Khemis Miliana', 36.26, 2.22), ('Blida', 36.47, 2.83), ('Algiers', 36.75, 3.06))
line('Algeria: Algiers-Bouira-Setif-Constantine', 2,
     ('Algiers', 36.75, 3.06), ('Thenia', 36.73, 3.55), ('Bouira', 36.37, 3.90),
     ('Bordj Bou Arreridj', 36.07, 4.76), ('Setif', 36.19, 5.41), ('Constantine', 36.37, 6.61))
line('Algeria: Constantine-Skikda', 1,
     ('Constantine', 36.37, 6.61), ('Skikda', 36.88, 6.91))
line('Algeria: Constantine-Guelma-Duvivier-Souk Ahras-Ghardimaou', 2,
     ('Constantine', 36.37, 6.61), ('El Khroub', 36.26, 6.69), ('Guelma', 36.46, 7.43),
     ('Duvivier', 36.47, 7.72), ('Souk Ahras', 36.29, 7.95), ('Ghardimaou', 36.45, 8.44))
line('Algeria: Annaba-Duvivier', 2,
     ('Annaba', 36.90, 7.77), ('Duvivier', 36.47, 7.72))
line('Algeria: Annaba-La Calle', 1,
     ('Annaba', 36.90, 7.77), ('La Calle', 36.90, 8.43))
line('Algeria: Annaba-Berrahal-Ramdane Djamel', 1,
     ('Annaba', 36.90, 7.77), ('Berrahal', 36.83, 7.45), ('Ramdane Djamel', 36.76, 6.89))
line('Algeria: Souk Ahras-Tebessa (standard gauge)', 1,
     ('Souk Ahras', 36.29, 7.95), ('Tebessa', 35.40, 8.12))
line('Algeria: Souk Ahras-Ouenza (iron ore)', 1,
     ('Souk Ahras', 36.29, 7.95), ('Ouenza', 35.96, 8.12))
line('Algeria: Constantine-Ouled Rahmoun-Ain Beida-Tebessa (metre gauge)', 1,
     ('Constantine', 36.37, 6.61), ('Ouled Rahmoun', 36.18, 6.70), ('Ain Beida', 35.80, 7.40),
     ('Tebessa', 35.40, 8.12))
line('Algeria: Ain Beida-Khenchela', 1,
     ('Ain Beida', 35.80, 7.40), ('Khenchela', 35.42, 7.13))
line('Algeria: Constantine-Batna-Biskra', 1,
     ('Constantine', 36.37, 6.61), ('Ouled Rahmoun', 36.18, 6.70), ('Batna', 35.56, 6.17),
     ('El Kantara', 35.22, 5.70), ('Biskra', 34.85, 5.73))
line('Algeria: Biskra-Touggourt (metre gauge)', 1,
     ('Biskra', 34.85, 5.73), ('Touggourt', 33.10, 6.07))
line('Algeria: Beni Mansour-Bejaia', 1,
     ('Beni Mansour', 36.42, 4.23), ('Bejaia', 36.75, 5.06))
line('Algeria: Thenia-Tizi Ouzou', 1,
     ('Thenia', 36.73, 3.55), ('Tizi Ouzou', 36.71, 4.05))
line('Algeria: Oran-Sidi Bel Abbes-Tlemcen-Oujda', 2,
     ('Oran', 35.70, -0.63), ('Sidi Bel Abbes', 35.19, -0.63), ('Tlemcen', 34.88, -1.32),
     ('Lalla Marnia', 34.85, -1.73), ('Oujda', 34.68, -1.91))
line('Algeria: Oran-Ain Temouchent-Beni Saf', 1,
     ('Oran', 35.70, -0.63), ('Ain Temouchent', 35.30, -1.13), ('Beni Saf', 35.30, -1.39))
line('Algeria: Lalla Marnia-Ghazaouet', 1,
     ('Lalla Marnia', 34.85, -1.73), ('Ghazaouet', 35.09, -1.86))
line('Algeria: Mohammadia-Mostaganem', 1,
     ('Mohammadia', 35.58, 0.07), ('Mostaganem', 35.93, 0.09))
line('Algeria: Mostaganem-Relizane-Tiaret', 1,
     ('Mostaganem', 35.93, 0.09), ('Relizane', 35.74, 0.55), ('Tiaret', 35.37, 1.32))
line('Algeria: Mohammadia-Mascara-Saida-Mecheria-Ain Sefra-Colomb-Bechar (narrow gauge)', 1,
     ('Mohammadia', 35.58, 0.07), ('Mascara', 35.40, 0.13), ('Saida', 34.83, 0.15),
     ('El Kheiter', 34.15, 0.07), ('Mecheria', 33.55, -0.28), ('Ain Sefra', 32.75, -0.58),
     ('Beni Ounif', 32.04, -1.25), ('Colomb-Bechar', 31.62, -2.22))
line('Algeria: Colomb-Bechar-Kenadsa', 1,
     ('Colomb-Bechar', 31.62, -2.22), ('Kenadsa', 31.55, -2.42))
line('Algeria: Blida-Medea-Berrouaghia-Boghari-Djelfa', 1,
     ('Blida', 36.47, 2.83), ('Medea', 36.27, 2.75), ('Berrouaghia', 36.12, 2.92),
     ('Boghari', 35.88, 2.75), ('Djelfa', 35.20, 3.25))

# ---------------------------------------------------------------- MOROCCO (1,435 mm)
line('Morocco: Oujda-Taza-Fez-Meknes-Rabat-Casablanca', 2,
     ('Oujda', 34.68, -1.91), ('Taourirt', 34.40, -2.90), ('Guercif', 34.23, -3.36), ('Taza', 34.21, -4.01),
     ('Fez', 34.03, -5.00), ('Meknes', 33.89, -5.55), ('Sidi Kacem', 34.22, -5.71),
     ('Sidi Slimane', 34.26, -5.93), ('Kenitra', 34.26, -6.58), ('Rabat', 34.02, -6.84),
     ('Mohammedia', 33.69, -7.38), ('Casablanca', 33.57, -7.59))
line('Morocco: Casablanca-Settat-Ben Guerir-Marrakech', 2,
     ('Casablanca', 33.57, -7.59), ('Berrechid', 33.27, -7.59), ('Settat', 33.00, -7.62),
     ('Ben Guerir', 32.23, -7.95), ('Marrakech', 31.63, -8.01))
line('Morocco: Ben Guerir-Youssoufia-Safi (opened May 1936)', 1,
     ('Ben Guerir', 32.23, -7.95), ('Youssoufia', 32.25, -8.53), ('Safi', 32.30, -9.24))
line('Morocco: Berrechid-Ben Ahmed-Khouribga-Oued Zem (phosphate)', 1,
     ('Berrechid', 33.27, -7.59), ('Ben Ahmed', 33.07, -7.26), ('Khouribga', 32.88, -6.91), ('Oued Zem', 32.86, -6.57))
line('Morocco: Sidi Kacem-Ksar el Kebir-Tangier', 1,
     ('Sidi Kacem', 34.22, -5.71), ('Ksar el Kebir', 35.00, -5.90), ('Tangier', 35.77, -5.80))
# Bou Arfa shares a province with Colomb-Bechar; the two lines were never joined (unfinished 1940 Trans-Saharan
# work), so this line stops at Tendrara to avoid a false connection.
line('Morocco: Oujda-Tendrara (towards Bou Arfa)', 1,
     ('Oujda', 34.68, -1.91), ('Tendrara', 33.05, -2.00))
line('Spanish Morocco: Ceuta-Tetuan', 1,
     ('Ceuta', 35.89, -5.32), ('Tetuan', 35.57, -5.37))
