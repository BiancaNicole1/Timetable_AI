import os
import csv
import re
import itertools
from collections import defaultdict, deque
import pandas as pd

class Profesor:
    def __init__(self, nume, zile_permise, ore_permise, max_ore_pe_zi):
        self.nume = nume
        self.zile_permise = zile_permise
        self.ore_permise = ore_permise
        self.max_ore_pe_zi = max_ore_pe_zi

    def __repr__(self):
        return f"Profesor('{self.nume}', Zile permise: {self.zile_permise}, Ore permise: {self.ore_permise}, Max ore/zi: {self.max_ore_pe_zi})"

class Curs:
    def __init__(self, nume, profesor, grupa, tip):
        self.nume = nume
        self.profesor = profesor
        self.grupa = grupa
        self.tip = tip

    def __repr__(self):
        return f"{self.nume}, Profesor: {self.profesor.nume}, Grupa: {self.grupa}, Tip: {self.tip})"

class Sala:
    def __init__(self, nume, capacitate):
        self.nume = nume
        self.capacitate = capacitate

    def __repr__(self):
        return f'{self.nume}'

class Eveniment:
    def __init__(self, curs, sala, zi, ora):
        self.curs = curs
        self.sala = sala
        self.zi = zi
        self.ora = ora

    def __repr__(self):
        return f"Eveniment(Curs: {self.curs.nume}, Sala: {self.sala.nume}, Zi: {self.zi}, Ora: {self.ora})"

class Orar:
    def __init__(self, zile, ore, sali):
        self.zile = zile
        self.ore = ore
        self.sali = sali
        self.evenimente = []
        self.domenii = defaultdict(list)  # Domenii pentru fiecare curs

    def init_domenii(self, cursuri):
        for curs in cursuri:
            self.domenii[curs] = [(zi, ora, sala) for zi in self.zile for ora in self.ore for sala in self.sali]

    def verifica_constrangeri(self, curs, zi, ora, sala):
        profesor = curs.profesor

        # Verificare: Ziua și ora sunt permise pentru profesor
        if zi not in profesor.zile_permise or ora not in profesor.ore_permise:
            return False

        # Verificare: Profesorul nu depășește numărul maxim de ore pe zi
        ore_in_zi = [ev for ev in self.evenimente if ev.curs.profesor == profesor and ev.zi == zi]
        if len(ore_in_zi) >= profesor.max_ore_pe_zi:
            return False

        # Verificare: Sala nu este deja ocupată
        if any(ev.sala == sala and ev.zi == zi and ev.ora == ora for ev in self.evenimente):
            return False

        # Verificare: Grupa nu este deja ocupată
        if any(ev.curs.grupa == curs.grupa and ev.zi == zi and ev.ora == ora for ev in self.evenimente):
            return False

        # Verificare: Profesorul nu are alte seminarii/cursuri la aceeași oră
        if any(ev.curs.profesor == profesor and ev.zi == zi and ev.ora == ora for ev in self.evenimente):
            return False

        return True

    def aplica_ac3(self):
        queue = deque(itertools.combinations(self.domenii.keys(), 2))
        while queue:
            x, y = queue.popleft()
            if self.restrange_domeniu(x, y):
                for z in (set(self.domenii.keys()) - {x, y}):
                    queue.append((z, x))

    def restrange_domeniu(self, x, y):
        restrans = False
        for valoare_x in self.domenii[x]:
            if not any(self.verifica_constrangeri_arc(valoare_x, valoare_y) for valoare_y in self.domenii[y]):
                self.domenii[x].remove(valoare_x)
                restrans = True
        return restrans

    def verifica_constrangeri_arc(self, valoare_x, valoare_y):
        zi_x, ora_x, sala_x = valoare_x
        zi_y, ora_y, sala_y = valoare_y
        return not (zi_x == zi_y and ora_x == ora_y and sala_x == sala_y)

    def backtracking(self, variabile):
        if not variabile:
            return True

        curs = variabile[0]
        for valoare in self.domenii[curs]:
            zi, ora, sala = valoare
            if self.verifica_constrangeri(curs, zi, ora, sala):
                self.evenimente.append(Eveniment(curs, sala, zi, ora))
                if self.backtracking(variabile[1:]):
                    return True
                self.evenimente.pop()

        return False

    def genereaza_orar(self, cursuri):
        self.init_domenii(cursuri)
        self.aplica_ac3()
        succes = self.backtracking(cursuri)
        if not succes:
            print("Nu s-a putut genera un orar valid.")
        else:
            self.afisare_orar_in_fisier('orar_output.txt')
    def afisare_orar_in_fisier(self, fisier_output):
        with open(fisier_output, 'w', encoding='utf-8') as f:
            f.write("Orar final organizat pe zile si ore:\n\n")
            zilele_saptamanii = {1: "Luni", 2: "Marti", 3: "Miercuri", 4: "Joi", 5: "Vineri"}

            for zi in range(1, 6):
                f.write(f"{zilele_saptamanii[zi]}:\n")
                evenimente_in_zi = [ev for ev in self.evenimente if ev.zi == zi]

                if evenimente_in_zi:
                    for ora in [8, 10, 12, 14, 16, 18]:
                        evenimente_in_ora = [ev for ev in evenimente_in_zi if ev.ora == ora]

                        if evenimente_in_ora:
                            f.write(f"  Ora {ora}:00\n")
                            for ev in evenimente_in_ora:
                                f.write(f"   {ev.curs.tip} {ev.curs.nume}, Profesor: {ev.curs.profesor.nume}, "
                                        f"Sala: {ev.sala.nume}, Grupa: {ev.curs.grupa}\n")
                else:
                    f.write("  Nu sunt evenimente programate.\n")
                f.write("\n")

        print(f"Orarul a fost salvat în fisierul '{fisier_output}'.")

def citeste_profesori_din_csv(fisier):
    profesori = []
    with open(fisier, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)  # Sar peste antet
        for row in reader:
            nume = row[0]
            zile_permise = list(map(int, row[1].split('|'))) if row[1] else []
            ore_permise = list(map(int, row[2].split('|'))) if row[2] else []
            max_ore_pe_zi = int(row[3])
            profesori.append(Profesor(nume, zile_permise, ore_permise, max_ore_pe_zi))
    return profesori

def citeste_cursuri_din_csv(fisier, profesori):
    cursuri = []
    with open(fisier, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            nume_curs = row[0]
            nume_profesor = row[1]
            grupe = row[2].split('|')
            profesor = next((p for p in profesori if p.nume == nume_profesor), None)
            if profesor:
                for grupa in grupe:
                    cursuri.append(Curs(nume_curs, profesor, grupa.strip(), "Curs"))
    return cursuri

def citeste_seminare_din_csv(fisier, profesori):
    seminare = []
    with open(fisier, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            nume_seminar = row[0]
            nume_profesor = row[1]
            grupe = row[2].split('|')
            profesor = next((p for p in profesori if p.nume == nume_profesor), None)
            if profesor:
                for grupa in grupe:
                    seminare.append(Curs(nume_seminar, profesor, grupa.strip(), "Seminar"))
    return seminare

def citeste_sali_din_csv(fisier):
    sali = []
    with open(fisier, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            nume = row[0]
            capacitate = int(row[1])
            sali.append(Sala(nume, capacitate))
    return sali

cuvinte_cheie = ["curs", "lab", "seminar", "profesor", "ora"]
constrangeri = []

profesori_df = pd.read_csv("profesori.csv")
seminare_df = pd.read_csv("seminare.csv")
sali_df = pd.read_csv("sali.csv")

# Verificarea și înregistrarea constrângerilor care conțin cuvinte-cheie
with open("constrangeri_modelate.txt", "w") as fisier:
    for constrangere in constrangeri:
        for cuvant in cuvinte_cheie:
            if re.search(rf"\b{cuvant}\b", constrangere, re.IGNORECASE):
                #fisier.write(f"{constrangere}\n")
                print(f"Constrangerea '{constrangere}' a fost modelata si inregistrata in fisier.")
                break  # Nu mai verificăm alte cuvinte pentru această constrângere

# Funcție pentru modelarea constrângerilor
def modeleaza_constrangere(constrangere, sali_df=None):
    # Template: Maxim ore intr-o zi pentru toti profesorii
    if re.search(r"profesorii sa nu aiba mai mult de (\d+) ore(?: (.+))?", constrangere, re.IGNORECASE):
        match = re.search(r"profesorii sa nu aiba mai mult de (\d+) ore(?: (.+))?", constrangere, re.IGNORECASE)
        max_ore = int(match.group(1))
        zi = match.group(2).lower() if match.group(2) else None  # Ziua dacă este specificată
        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        if zi and zi in zile:
            return f"max_ore_profesori_{zi} = {max_ore}"
        else:
            return f"max_ore_profesori = {max_ore}"

    # Template: Profesor indisponibil
    if re.search(r"profesorul ([\w\s\.]+) nu este disponibil (.+)", constrangere, re.IGNORECASE):
        match = re.search(r"profesorul ([\w\s\.]+) nu este disponibil (.+)", constrangere, re.IGNORECASE)
        nume_profesor = match.group(1).strip()
        zile_interzise = match.group(2)
        zile_interzise = re.split(r"\s*si\s*|\s*,\s*", zile_interzise)  # Split pe "si" și ","
        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        zile_permise = {zile[z] for z in zile if z not in [zi.lower() for zi in zile_interzise]}
        return f"zile_permise_{nume_profesor} = {zile_permise}"

    # Template: Maxim ore pe zi la un profesor
    if re.search(r"profesorul ([\w\s\.]+) sa nu aiba mai mult de (\d+) ore(?: (.+))?", constrangere, re.IGNORECASE):
        match = re.search(r"profesorul ([\w\s\.]+) sa nu aiba mai mult de (\d+) ore(?: (.+))?", constrangere, re.IGNORECASE)
        profesor = match.group(1).strip()
        max_ore = int(match.group(2))
        zi = match.group(3).lower() if match.group(3) else None  # Ziua dacă este specificată
        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        if zi and zi in zile:
            return f"max_ore_{profesor}_{zi} = {max_ore}"
        else:
            return f"max_ore_{profesor} = {max_ore}"

    # Template: Profesorul nu poate veni dupa ora x
    if re.search(r"profesorul ([\w\s\.]+) nu poate veni dupa ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"profesorul ([\w\s\.]+) nu poate veni dupa ora (\d+)", constrangere, re.IGNORECASE)
        nume_profesor = match.group(1).strip()  # Numele profesorului
        ora_limita = int(match.group(2))  # Ora după care profesorul nu poate veni
        ore_permise = [hour for hour in range(8, 19, 2) if hour < ora_limita]
        return f"ore_permise_{nume_profesor} = {ore_permise}"

    if re.search(r"profesorul ([\w\s\.]+) nu poate veni inainte de ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"profesorul ([\w\s\.]+) nu poate veni inainte de ora (\d+)", constrangere, re.IGNORECASE)
        nume_profesor = match.group(1).strip()  # Numele profesorului
        ora_limita = int(match.group(2))  # Ora după care profesorul nu poate veni
        ore_permise = [hour for hour in range(8, 19, 2) if hour >= ora_limita]
        return f"ore_permise_{nume_profesor} = {ore_permise}"

    # Template: Sala indisponibilă
    if re.search(r"sala (\w+) este indisponibila (.+)", constrangere, re.IGNORECASE):
        match = re.search(r"sala (\w+) este indisponibila (.+)", constrangere, re.IGNORECASE)
        sala = match.group(1)
        zile_interzise = match.group(2)

        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        zile_specificate = {
            zile[zi.lower()]
            for zi in re.split(r"\s*si\s*|\s*,\s*", zile_interzise)
            if zi.lower() in zile
        }
        zile_permise = set(zile.values()) - zile_specificate
        # Actualizăm datele sălii
        if sali_df is not None:
            sali_df = actualizeaza_zile_sala(sali_df, sala, zile_interzise)
            sali_df.to_csv("sali_actualizate.csv", index=False)
        return f"zile_disponibile_sala_{sala} = {zile_permise}"

    if re.search(r"sala (\w+) este indisponibila dupa ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"sala (\w+) este indisponibila dupa ora (\d+)", constrangere, re.IGNORECASE)
        sala = match.group(1)
        ora_limita = int(match.group(2))
        ore_permise = [hour for hour in range(8, 19, 2) if hour < ora_limita]

        # Actualizăm datele sălii
        if sali_df is not None:
            sali_df = actualizeaza_sala_dupa_ora(sali_df, sala, ora_limita)
            sali_df.to_csv("sali_actualizate.csv", index=False)
        return f"ore_disponibile_sala_{sala} = {ore_permise}"

    if re.search(r"sala (\w+) este indisponibila pana la ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"sala (\w+) este indisponibila pana la ora (\d+)", constrangere, re.IGNORECASE)
        sala = match.group(1)
        ora_limita = int(match.group(2))
        ore_permise = [hour for hour in range(8, 19, 2) if hour >= ora_limita]

        # Actualizăm datele sălii
        if sali_df is not None:
            sali_df = actualizeaza_sala_pana_ora(sali_df, sala, ora_limita)
            sali_df.to_csv("sali_actualizate.csv", index=False)
        return f"ore_disponibile_sala_{sala} = {ore_permise}"

    # Template: Fara cursuri/laboratoare/seminare dupa ora x in ziua y
    if re.search(r"nu pune cursuri (\w+) dupa ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"nu pune cursuri (\w+) dupa ora (\d+)", constrangere, re.IGNORECASE)
        zi = match.group(1).lower()  # Ziua specificată
        ora = int(match.group(2))  # Ora specificată

        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        if zi in zile:
            # Definim intervalul de ore permise, care sunt mai mici decat ora specificata
            ore_permise = [hour for hour in range(8, 19, 2) if hour < ora]
            return f"ore_cursuri_{zi} = {ore_permise}"

    if re.search(r"nu pune seminare (\w+) dupa ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"nu pune seminare (\w+) dupa ora (\d+)", constrangere, re.IGNORECASE)
        zi = match.group(1).lower()  # Ziua specificată
        ora = int(match.group(2))  # Ora specificată

        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        if zi in zile:
            # Definim intervalul de ore permise, care sunt mai mici decat ora specificata
            ore_permise = [hour for hour in range(8, 19, 2) if hour < ora]
            return f"ore_seminare_{zi} = {ore_permise}"

    if re.search(r"nu pune cursuri (\w+) inainte de ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"nu pune cursuri (\w+) inainte de ora (\d+)", constrangere, re.IGNORECASE)
        zi = match.group(1).lower()  # Ziua specificată
        ora = int(match.group(2))  # Ora specificată

        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        if zi in zile:
            # Definim intervalul de ore permise, care sunt mai mari decat ora specificata
            ore_permise = [hour for hour in range(8, 19, 2) if hour >= ora]
            return f"ore_cursuri_{zi} = {ore_permise}"

    if re.search(r"nu pune seminare (\w+) inainte de ora (\d+)", constrangere, re.IGNORECASE):
        match = re.search(r"nu pune seminare (\w+) inainte de ora (\d+)", constrangere, re.IGNORECASE)
        zi = match.group(1).lower()  # Ziua specificată
        ora = int(match.group(2))  # Ora specificată

        zile = {"luni": 1, "marti": 2, "miercuri": 3, "joi": 4, "vineri": 5}
        if zi in zile:
            # Definim intervalul de ore permise, care sunt mai mari decat ora specificata
            ore_permise = [hour for hour in range(8, 19, 2) if hour >= ora]
            return f"ore_seminare_{zi} = {ore_permise}"

    return None  # Dacă nu se potrivește cu niciun template
#Actualizari
def actualizeaza_prof_dupa_max_ore_pe_zi(profesori_df, max_ore_pe_zi):
    max_ore_pe_zi = int(max_ore_pe_zi)  # Convertim numărul maxim de ore la tipul int
    for index, row in profesori_df.iterrows():
        # Preluăm orele permise ale profesorului
        ore_permise = row['ore_permise'].split('|')
        ore_permise = list(map(int, ore_permise))  # Convertim orele la întregi

        # Dacă numărul de ore depășește limita, le actualizăm
        if len(ore_permise) > max_ore_pe_zi:
            ore_permise = ore_permise[:max_ore_pe_zi]  # Păstrăm doar primele `max_ore_pe_zi` ore

            # Actualizăm orele permise în DataFrame
            profesori_df.at[index, 'ore_permise'] = '|'.join(map(str, ore_permise))
            profesori_df.to_csv("profesori_actualizat.csv", index=False)

    return profesori_df

def actualizeaza_profesor_pana_ora(profesori_df, profesor, ora_limita):
    ore_permise = profesori_df.loc[profesori_df['nume'] == profesor, 'ore_permise'].values[0]
    ore_permise = list(map(int, ore_permise.split('|')))
    ore_permise = [ore for ore in ore_permise if ore >= ora_limita]
    profesori_df.loc[profesori_df['nume'] == profesor, 'ore_permise'] = '|'.join(map(str, ore_permise))
    profesori_df.to_csv("profesori_actualizat.csv", index=False)

    return profesori_df

def actualizeaza_profesor_dupa_ora(profesori_df, profesor, ora_limita):
    # Transformăm orele permise în format listă
    ore_permise = profesori_df.loc[profesori_df['nume'] == profesor, 'ore_permise'].values[0]
    ore_permise = list(map(int, ore_permise.split('|')))

    # Filtrăm orele care sunt mai mici decât ora limită
    ore_permise = [ore for ore in ore_permise if ore < ora_limita]

    # Actualizăm fișierul cu noile ore permise
    profesori_df.loc[profesori_df['nume'] == profesor, 'ore_permise'] = '|'.join(map(str, ore_permise))
    profesori_df.to_csv("profesori_actualizat.csv", index=False)

    return profesori_df

def actualizeaza_zile_profesor(profesori_df, nume_profesor, zile_indisponibile):
    zile_indisponibile = zile_indisponibile.split('|')  # Separăm zilele de indisponibilitate

    # Căutăm profesorul în DataFrame
    for index, row in profesori_df.iterrows():
        if row['nume'].strip().lower() == nume_profesor.strip().lower():
            # Preluăm zilele disponibile
            zile_disponibile = row['zile_disponibile'].split('|')

            # Eliminăm zilele de indisponibilitate
            zile_disponibile = [z for z in zile_disponibile if z not in zile_indisponibile]

            # Actualizăm zilele disponibile
            profesori_df.at[index, 'zile_disponibile'] = '|'.join(zile_disponibile)
            profesori_df.to_csv("profesori_actualizat.csv", index=False)

    return profesori_df

#profesori_df = pd.read_csv("profesori.csv")
#profesori_df = actualizeaza_profesor_dupa_ora(profesori_df, 'Albert Ramona', 12)
#profesori_df.to_csv("profesori_actualizat.csv", index=False)

def actualizeaza_zile_sala(sali_df, nume_sala, zile_indisponibile):
    zile_indisponibile = zile_indisponibile.split('|')
    for index, row in sali_df.iterrows():
        if row['nume'].strip().lower() == nume_sala.strip().lower():
            zile_disponibile = row['zile_disponibile'].split('|')
            zile_disponibile = [z for z in zile_disponibile if z not in zile_indisponibile]
            sali_df.at[index, 'zile_disponibile'] = '|'.join(zile_disponibile)
            sali_df.to_csv("seminare_actualizat.csv", index=False)
    return sali_df

def actualizeaza_sala_pana_ora(sali_df, sala, ora_limita):
    ore_disponibile = sali_df.loc[sali_df['nume_sala'] == sala, 'ore_disponibile'].values[0]
    ore_disponibile = list(map(int, ore_disponibile.split('|')))
    ore_disponibile = [ore for ore in ore_disponibile if ore >= ora_limita]
    sali_df.loc[sali_df['nume_sala'] == sala, 'ore_disponibile'] = '|'.join(map(str, ore_disponibile))
    sali_df.to_csv("seminare_actualizat.csv", index=False)

    return sali_df

def actualizeaza_sala_dupa_ora(sali_df, sala, ora_limita):
    ore_disponibile = sali_df.loc[sali_df['nume_sala'] == sala, 'ore_disponibile'].values[0]
    ore_disponibile = list(map(int, ore_disponibile.split('|')))
    ore_disponibile = [ore for ore in ore_disponibile if ore < ora_limita]
    sali_df.loc[sali_df['nume_sala'] == sala, 'ore_disponibile'] = '|'.join(map(str, ore_disponibile))
    sali_df.to_csv("seminare_actualizat.csv", index=False)

    return sali_df

def actualizeaza_cursuri_dupa_zi_si_ora(cursuri_df, zi_spec, ora_limită):
    ora_limită = int(ora_limită)
    for index, row in cursuri_df.iterrows():
        zile_disponibile = row['zile_disponibile'].split('|')
        if zi_spec in zile_disponibile:
            ore_permise = list(map(int, row['ore_permise'].split('|')))
            ore_permise = [ora for ora in ore_permise if ora <= ora_limită]
            cursuri_df.at[index, 'ore_permise'] = '|'.join(map(str, ore_permise))
            cursuri_df.to_csv("seminare_actualizat.csv", index=False)
    return cursuri_df

def actualizeaza_seminare_dupa_zi_si_ora(seminare_df, zi_spec, ora_limită):
    ora_limită = int(ora_limită)
    for index, row in seminare_df.iterrows():
        zile_disponibile = row['zile_disponibile'].split('|')
        if zi_spec in zile_disponibile:
            ore_permise = list(map(int, row['ore_permise'].split('|')))
            ore_permise = [ora for ora in ore_permise if ora <= ora_limită]
            seminare_df.at[index, 'ore_permise'] = '|'.join(map(str, ore_permise))
            seminare_df.to_csv("seminare_actualizat.csv", index=False)

    return seminare_df

def actualizeaza_cursuri_inainte_zi_si_ora(cursuri_df, zi_spec, ora_limită):
    ora_limită = int(ora_limită)
    for index, row in cursuri_df.iterrows():
        zile_disponibile = row['zile_disponibile'].split('|')
        if zi_spec in zile_disponibile:
            ore_permise = list(map(int, row['ore_permise'].split('|')))
            ore_permise = [ora for ora in ore_permise if ora > ora_limită]
            cursuri_df.at[index, 'ore_permise'] = '|'.join(map(str, ore_permise))
            cursuri_df.to_csv("seminare_actualizat.csv", index=False)

    return cursuri_df

def actualizeaza_seminare_inainte_zi_si_ora(seminare_df, zi_spec, ora_limită):
    ora_limită = int(ora_limită)
    for index, row in seminare_df.iterrows():
        zile_disponibile = row['zile_disponibile'].split('|')
        if zi_spec in zile_disponibile:
            ore_permise = list(map(int, row['ore_permise'].split('|')))
            ore_permise = [ora for ora in ore_permise if ora > ora_limită]
            seminare_df.at[index, 'ore_permise'] = '|'.join(map(str, ore_permise))
            seminare_df.to_csv("seminare_actualizat.csv", index=False)

    return seminare_df


#MAIN
print("Introduceti constrangerile (scrie 'ok' ca sa primesti orarul generat) "
      "sau scrieti 'f' daca doriti sa importati constrangerile din fisier:")

variabile_declarate = {}
constrangeri = set()  # Utilizăm un set pentru a evita duplicatele


def citeste_din_fisier(fisier_nume):
    try:
        with open(fisier_nume, 'r') as fisier:
            return fisier.readlines()
    except FileNotFoundError:
        print(f"Fișierul {fisier_nume} nu a fost găsit.")
        return []


while True:
    user_input = input("-> ")

    if user_input.lower() == "ok":
        with open("constrangeri_modelate.txt", "w") as fisier:
            for constrangere in constrangeri:
                fisier.write(constrangere + "\n")
        print("Orarul generat pe baza constrângerilor va fi afișat in fisier...")
        break

    elif user_input.lower() == "f":
        constrangeri_input = citeste_din_fisier("input.txt")
        for linie in constrangeri_input:
            linie = linie.strip()  # Îndepărtăm eventualele spații
            model = modeleaza_constrangere(linie)
            if model:
                variabila, valoare = model.split(" = ")
                valoare_evaluata = eval(valoare)

                if variabila in variabile_declarate:
                    # Dacă variabila există, facem intersecția valorilor
                    intersectie = set(variabile_declarate[variabila]).intersection(set(valoare_evaluata))
                    if not intersectie:
                        intersectie = {0}
                    variabile_declarate[variabila] = intersectie
                else:
                    # Dacă variabila nu există, o adăugăm
                    variabile_declarate[variabila] = valoare_evaluata

                # Adăugăm constrângerea modelată la setul de constrângeri
                constrangeri.add(f"{variabila} = {variabile_declarate[variabila]}")

                print(f"Constrângere adăugată: {variabila} = {variabile_declarate[variabila]}")
            else:
                print(f"Constrângerea '{linie}' nu se potrivește niciunui template și a fost ignorată.")
        break

    else: #de la prompt
        model = modeleaza_constrangere(user_input)
        if model:
            variabila, valoare = model.split(" = ")
            valoare_evaluata = eval(valoare)

            if variabila in variabile_declarate:
                # Dacă variabila există, facem intersecția valorilor
                intersectie = set(variabile_declarate[variabila]).intersection(set(valoare_evaluata))
                if not intersectie:
                    intersectie = {0}
                variabile_declarate[variabila] = intersectie
            else:
                # Dacă variabila nu există, o adăugăm
                variabile_declarate[variabila] = valoare_evaluata

            # Adăugăm constrângerea modelată la setul de constrângeri
            constrangeri.add(f"{variabila} = {variabile_declarate[variabila]}")

            print(f"Constrângere adăugată: {variabila} = {variabile_declarate[variabila]}")
        else:
            print(f"Constrângerea '{user_input}' nu se potrivește niciunui template și a fost ignorată.")

def main():
    profesori = citeste_profesori_din_csv('profesori_actualizat.csv')
    cursuri = citeste_cursuri_din_csv('cursuri_actualizat.csv', profesori)
    seminare = citeste_seminare_din_csv('seminare_actualizat.csv', profesori)
    sali = citeste_sali_din_csv('sali_actualizat.csv')

    toate_cursurile = cursuri + seminare
    orar = Orar([1, 2, 3, 4, 5], [8, 10, 12, 14, 16, 18], sali)
    orar.genereaza_orar(toate_cursurile)


if __name__ == "__main__":
    main()