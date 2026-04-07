from itertools import combinations

# Funcția de calcul punctaj, neschimbată
def calc_punctaj(combinatie, culori):
    combinatii = {
        (1, 1, 1): 20,
        (2, 2, 2): 30,
        (3, 3, 3): 40,
        (4, 4, 4): 50,
        (5, 5, 5): 60,
        (6, 6, 6): 70,
        (7, 7, 7): 80,
        (8, 8, 8): 90
    }
    
    consecutive = [
        (1, 2, 3),
        (2, 3, 4),
        (3, 4, 5),
        (4, 5, 6),
        (5, 6, 7),
        (6, 7, 8)
    ]
    
    if tuple(sorted(combinatie)) in combinatii:
        return combinatii[tuple(sorted(combinatie))]
    
    for con in consecutive:
        if tuple(sorted(combinatie)) == con:
            if len(set(culori)) == 1:  # Dacă toate cărțile sunt de aceeași culoare
                return 50 + 10 * (con[0] - 1)
            else:
                return 10 * (con[0])  # Corectăm punctajul pentru culori diferite
    
    return 0

# Funcția ce identifică combinațiile viitoare potențial valoroase
def evaluare_potential_carte(carti, culori):
    potential_combinatii = 0
    consecutive = [
        (1, 2, 3),
        (2, 3, 4),
        (3, 4, 5),
        (4, 5, 6),
        (5, 6, 7),
        (6, 7, 8)
    ]

    for con in consecutive:
        carti_in_con = [carte for carte in carti if carte in con]
        if len(carti_in_con) >= 2:  # Dacă există cel puțin 2 cărți care sunt aproape de a forma o combinație valoroasă
            potential_combinatii += 1

    return potential_combinatii

# Găsește combinația optimă care prioritizează culorile identice
def gaseste_combinatia_optima(carti, culori, pachet):
    max_score = 0
    combinatia_ideala = ()
    prioritate_culoare = False
    
    for comb in combinations(range(len(carti)), 3):
        carti_comb = [carti[i] for i in comb]
        culori_comb = [culori[i] for i in comb]

        # Dacă toate cărțile sunt de aceeași culoare, le prioritizăm
        if len(set(culori_comb)) == 1:
            prioritate_culoare = True
            score = calc_punctaj(carti_comb, culori_comb) + 10  # Bonus pentru aceeași culoare
        else:
            score = calc_punctaj(carti_comb, culori_comb)
        
        # Dacă combinația este sub un prag minim, o ignorăm
        if score < 30:
            continue

        # Dacă găsim o combinație de aceeași culoare, o prioritizăm
        if prioritate_culoare and len(set(culori_comb)) == 1 and score > max_score:
            max_score = score
            combinatia_ideala = comb
        
        # Dacă nu avem o combinație de aceeași culoare, dar punctajul este mai mare decât cel anterior
        elif not prioritate_culoare and score > max_score:
            max_score = score
            combinatia_ideala = comb

    # Dacă nu găsim nicio combinație care să depășească pragul minim
    if max_score == 0:
        return [], [], 0, carti, culori

    carti_de_scos = [carti[i] for i in combinatia_ideala]
    culori_de_scos = [culori[i] for i in combinatia_ideala]
    
    carti_ramase = [carti[i] for i in range(len(carti)) if i not in combinatia_ideala]
    culori_ramase = [culori[i] for i in range(len(culori)) if i not in combinatia_ideala]
    
    return carti_de_scos, culori_de_scos, max_score, carti_ramase, culori_ramase


# Funcția de eliminare a unei cărți, îmbunătățită pentru a păstra cărțile mari și a analiza combinațiile viitoare
def cartea_de_eliminat(carti, culori):
    potential = {i: evaluare_potential_carte([c for idx, c in enumerate(carti) if idx != i], 
                                             [cul for idx, cul in enumerate(culori) if idx != i]) 
                 for i in range(len(carti))}
    
    # Prioritizăm eliminarea cărților mici (1, 2, 3)
    # Dacă două cărți au același potențial, eliminăm prima carte mică găsită
    index_carte_min_potential = min(potential, key=lambda i: (potential[i], carti[i]))

    # Dacă cartea este mare (7 sau 8) și nu e necesar să o eliminăm, eliminăm cartea cea mai mică posibilă
    if carti[index_carte_min_potential] >= 7:
        index_carte_min_potential = min((i for i in range(len(carti)) if carti[i] < 7), key=potential.get, default=index_carte_min_potential)
    
    return carti.pop(index_carte_min_potential), culori.pop(index_carte_min_potential)


# Funcția de actualizare a pachetului rămâne neschimbată
def actualizeaza_pachet(pachet, carti_de_scos, culori_de_scos):
    for carte, culoare in zip(carti_de_scos, culori_de_scos):
        pachet.remove(f"{carte}{culoare}")
    return pachet

# Funcția principală de rulare a programului
def ruleaza_programul():
    pachet = [f"{n}{c}" for n in range(1, 9) for c in ['r', 'g', 'a']]  # Pachetul de 1-8 roșii, galbene, albastre
    carti_ramase = []
    culori_ramase = []
    
    while len(pachet) > 0:
        try:
            # Completează setul curent cu cărți noi din pachet
            while len(carti_ramase) < 5:
                carti_noi = input(f"Introduceți {5 - len(carti_ramase)} cărți noi (de forma 1r, 2a, 3g, etc., separate prin spațiu): ").split()
                if len(carti_noi) != 5 - len(carti_ramase):
                    print(f"Trebuie să introduceți exact {5 - len(carti_ramase)} cărți.")
                    continue

                carti_ramase.extend([int(c[:-1]) for c in carti_noi])
                culori_ramase.extend([c[-1] for c in carti_noi])
                
                if any(f"{carte}{culoare}" not in pachet for carte, culoare in zip(carti_ramase, culori_ramase)):
                    print("Ați introdus cărți care nu sunt valide sau nu mai sunt în pachet. Încercați din nou.")
                    carti_ramase = []
                    culori_ramase = []
                    continue

            print(f"\nPachetul rămas: {' '.join(pachet)}")
            
            # Găsește combinația optimă care maximizează punctajul
            carti_de_scos, culori_de_scos, punctaj, carti_ramase, culori_ramase = gaseste_combinatia_optima(carti_ramase, culori_ramase, pachet)

            if punctaj == 0:
                carte_de_eliminat, culoare_de_eliminat = cartea_de_eliminat(carti_ramase, culori_ramase)
                print(f"Nu există combinații avantajoase. Eliminați cartea {carte_de_eliminat}{culoare_de_eliminat}.")
                pachet = actualizeaza_pachet(pachet, [carte_de_eliminat], [culoare_de_eliminat])
                continue

            print(f"Cărțile de scos pentru punctaj maxim: {carti_de_scos} cu culorile: {culori_de_scos}")
            print(f"Punctaj maxim obținut: {punctaj}\n")

            pachet = actualizeaza_pachet(pachet, carti_de_scos, culori_de_scos)

            if len(pachet) < 3:
                print("Nu mai sunt suficiente cărți pentru a continua. Programul se oprește.")
                break
            
        except ValueError:
            print("Datele introduse nu sunt valide. Vă rog să încercați din nou.")

# Rulăm programul
ruleaza_programul()
