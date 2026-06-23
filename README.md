# Usporedba relacijske i grafovske baze podataka za modeliranje bioloških vrsta

Projekt uspoređuje DuckDB (relacijska) i Kuzu (grafovska) bazu podataka na domeni praćenja ugroženih bioloških vrsta. Implementirane su obje baze s identičnim skupom podataka, a zatim izmjerene performanse na šest kategorija upita.

## Tehnologije

- **Python 3.11+**
- **Marimo** – reaktivne bilježnice
- **DuckDB** – relacijska baza (in-process, analitička)
- **Kuzu** – grafovska baza (in-process, property graph)
- **Pandas**, **Plotly**, **Graphviz** – analiza i vizualizacija

## Pokretanje

```bash
pip install -r requirements.txt

# kreiranje baza i punjenje podataka
marimo edit biljeznice/konstrukcija_baza.py

# usporedba upita
marimo edit biljeznice/usporedba_baza.py
```

> Direktorij `baze/` se briše i kreira iznova pri svakom pokretanju `01_kreiranje.py`.

## Podaci

Podaci su generirani bibliotekom Faker. Ukupno ~400 000 redaka raspoređenih u 19 tablica / 12 tipova čvorova. Veće tablice (akcije, rezervacije, edukacije) imaju između 10 000 i 277 000 zapisa.

## Rezultati

Svi upiti mjereni 11 puta, prikazano medijansko vrijeme.

| Upit | DuckDB | Kuzu |
|------|--------|------|
| Aktivnost tima (1-hop) | 14 ms | 19 ms |
| Pregled rezervoara | 11 ms | 73 ms |
| Taksonomska hijerarhija | 21 ms | 1361 ms |
| Osobe i uloge u timu (M:N) | 10 ms | 24 ms |
| Slobodne akcije (bez filtera) | 18 ms | 183 ms |
| Kontekstualna agregacija | 22 ms | 132 ms |

DuckDB je brži na svim upitima. Najveća razlika je kod taksonomske hijerarhije gdje Cypher radi generalizirani graph traversal umjesto determinističkog parent-pointer joina.

Kuzu je brži samo pri **punjenju podataka** (16 s vs 84 s), ali zauzima duplo više prostora na disku (74 MB vs 36 MB).