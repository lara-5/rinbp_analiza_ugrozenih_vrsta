import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Usporedba relacijske i grafovske baze podataka za modeliranje bioloških vrsta
    """)
    return


@app.cell
def _():
    # Importi
    import marimo as mo
    import duckdb
    import kuzu
    import os
    import shutil
    import time
    import pandas as pd
    from graphviz import Digraph
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    return duckdb, go, kuzu, make_subplots, mo, os, pd, shutil, time


@app.cell
def _(os, shutil):
    # Putanje
    PODACI      = "podaci"
    BAZE        = "baze"
    DUCKDB_PATH = os.path.join(BAZE, "relacijska_baza.duckdb")
    KUZU_PATH  = os.path.join(BAZE, "graf_baza.kuzu")

    shutil.rmtree(BAZE, ignore_errors=True)
    os.makedirs(BAZE, exist_ok=True)
    return DUCKDB_PATH, KUZU_PATH, PODACI


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. Kreiranje baza
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.1. Relacijska baza podataka (DuckDB)
    """)
    return


@app.cell
def _(DUCKDB_PATH, duckdb):
    duckdb_conn = duckdb.connect(DUCKDB_PATH)
    return (duckdb_conn,)


@app.cell
def _(duckdb_conn):
    # kreiranje sheme - sve u jednoj shemi s prefiksima

    duckdb_conn.execute("""
        CREATE TABLE VRSTE_SUSTAVI_STUPNJEVA_UGROZENOSTI (
            ID_sustava                  INTEGER PRIMARY KEY,
            datum_pocetka_koristenja    DATE    NOT NULL,
            datum_kraja_koristenja      DATE
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_STUPNJEVI_UGROZENOSTI (
            ID_stupnja                               INTEGER PRIMARY KEY,
            red_stupnja_ugrozenosti                  INTEGER NOT NULL,
            oznaka_stupnja                           VARCHAR NOT NULL,
            opis_stupnja                             VARCHAR NOT NULL,
            SUSTAVI_STUPNJEVA_UGROZENOSTI_ID_sustava INTEGER NOT NULL,
            FOREIGN KEY (SUSTAVI_STUPNJEVA_UGROZENOSTI_ID_sustava) 
                REFERENCES VRSTE_SUSTAVI_STUPNJEVA_UGROZENOSTI(ID_sustava)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_TIPOVI_TAKSONOMIJA (
            ID_tipa     INTEGER PRIMARY KEY,
            ime_tipa    VARCHAR NOT NULL
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_TAKSONOMIJA_SELF (
            ID_taksonomije_self         INTEGER PRIMARY KEY,
            ime_kategorije              VARCHAR NOT NULL,
            TIPOVI_TAKSONOMIJA_ID_tipa  INTEGER NOT NULL,
            TAKSONOMIJA_SELF_predak     INTEGER,
            FOREIGN KEY (TIPOVI_TAKSONOMIJA_ID_tipa) 
                REFERENCES VRSTE_TIPOVI_TAKSONOMIJA(ID_tipa),
            FOREIGN KEY (TAKSONOMIJA_SELF_predak) 
                REFERENCES VRSTE_TAKSONOMIJA_SELF(ID_taksonomije_self)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_STANISTA (
            ID_stanista INTEGER PRIMARY KEY,
            naziv       VARCHAR  NOT NULL,
            opis        VARCHAR,
            povrsina    INTEGER
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_INTERAKCIJE (
            ID_interakcije  INTEGER PRIMARY KEY,
            interakcija     VARCHAR NOT NULL,
            uloga1          VARCHAR NOT NULL,
            uloga2          VARCHAR,
            mutualan        BOOLEAN NOT NULL
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_POPULACIJE (
            ID_populacije                        INTEGER PRIMARY KEY,
            TAKSONOMIJA_SELF_ID_taksonomije_self INTEGER NOT NULL,
            STANISTA_ID_stanista                 INTEGER NOT NULL,
            FOREIGN KEY (TAKSONOMIJA_SELF_ID_taksonomije_self) 
                REFERENCES VRSTE_TAKSONOMIJA_SELF(ID_taksonomije_self),
            FOREIGN KEY (STANISTA_ID_stanista) 
                REFERENCES VRSTE_STANISTA(ID_stanista)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_STUPNJEVI_UGROZENOSTI_POPULACIJE (
            ID_oznacavanja                   INTEGER PRIMARY KEY,
            STUPNJEVI_UGROZENOSTI_ID_stupnja INTEGER NOT NULL,
            POPULACIJE_ID_populacije         INTEGER NOT NULL,
            datum                            DATE    NOT NULL,
            FOREIGN KEY (STUPNJEVI_UGROZENOSTI_ID_stupnja) 
                REFERENCES VRSTE_STUPNJEVI_UGROZENOSTI(ID_stupnja),
            FOREIGN KEY (POPULACIJE_ID_populacije) 
                REFERENCES VRSTE_POPULACIJE(ID_populacije)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE VRSTE_MEDUODNOSI (
            PK_ID_meduodnosa            INTEGER PRIMARY KEY,
            POPULACIJE_ID_populacije1   INTEGER NOT NULL,
            POPULACIJE_ID_populacije2   INTEGER NOT NULL,
            INTERAKCIJE_ID_interakcije  INTEGER NOT NULL,
            FOREIGN KEY (POPULACIJE_ID_populacije1) 
                REFERENCES VRSTE_POPULACIJE(ID_populacije),
            FOREIGN KEY (POPULACIJE_ID_populacije2) 
                REFERENCES VRSTE_POPULACIJE(ID_populacije),
            FOREIGN KEY (INTERAKCIJE_ID_interakcije) 
                REFERENCES VRSTE_INTERAKCIJE(ID_interakcije)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_MJESTA (
            ID_mjesta       INTEGER PRIMARY KEY,
            naziv_mjesta    VARCHAR NOT NULL,
            postanski_br    VARCHAR NOT NULL
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_TIPOVI_AKCIJA (
            ID_tipa_akcije      INTEGER PRIMARY KEY,
            naziv_akcije        VARCHAR NOT NULL,
            opis_tipa_akcije    VARCHAR
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_REZERVOARI (
            ID_rezervoara       INTEGER         PRIMARY KEY,
            naziv_rezervoara    VARCHAR         NOT NULL,
            pocetni_broj_vrsta  INTEGER,
            povrsina            DECIMAL(18, 4),
            MJESTA_ID_mjesta    INTEGER         NOT NULL,
            FOREIGN KEY (MJESTA_ID_mjesta) 
                REFERENCES AKCIJE_MJESTA(ID_mjesta)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_OSOBE (
            ID_osobe                    INTEGER PRIMARY KEY,
            ime                         VARCHAR NOT NULL,
            prezime                     VARCHAR NOT NULL,
            mail                        VARCHAR NOT NULL,
            datum_rodenja               DATE,
            MJESTA_ID_mjesta_stanovanja INTEGER,
            FOREIGN KEY (MJESTA_ID_mjesta_stanovanja) 
                REFERENCES AKCIJE_MJESTA(ID_mjesta)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_TIMOVI (
            ID_tima         INTEGER PRIMARY KEY,
            datum_nastanka  DATE    NOT NULL
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_ULOGE (
            ID_uloga        INTEGER PRIMARY KEY,
            naziv_uloge     VARCHAR NOT NULL
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_TIMOVI_OSOBE (
            TIMOVI_ID_tima  INTEGER NOT NULL,
            ULOGE_ID_uloga  INTEGER NOT NULL,
            OSOBE_ID_osobe  INTEGER NOT NULL,
            PRIMARY KEY (TIMOVI_ID_tima, ULOGE_ID_uloga, OSOBE_ID_osobe),
            FOREIGN KEY (TIMOVI_ID_tima) 
                REFERENCES AKCIJE_TIMOVI(ID_tima),
            FOREIGN KEY (ULOGE_ID_uloga) 
                REFERENCES AKCIJE_ULOGE(ID_uloga),
            FOREIGN KEY (OSOBE_ID_osobe) 
                REFERENCES AKCIJE_OSOBE(ID_osobe)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_EDUKACIJE (
            ID_edukacije        INTEGER PRIMARY KEY,
            naziv_edukacije     VARCHAR NOT NULL,
            opis_edukacije      VARCHAR NOT NULL,
            datum_odrzavanja    DATE    NOT NULL,
            broj_mjesta         INTEGER,
            broj_posjetitelja   INTEGER,
            TIMOVI_ID_tima      INTEGER NOT NULL,
            MJESTA_ID_mjesta    INTEGER NOT NULL,
            FOREIGN KEY (TIMOVI_ID_tima) 
                REFERENCES AKCIJE_TIMOVI(ID_tima),
            FOREIGN KEY (MJESTA_ID_mjesta) 
                REFERENCES AKCIJE_MJESTA(ID_mjesta)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_REZERVACIJE_EDUKACIJA (
            ID_rezervacije          INTEGER   PRIMARY KEY,
            EDUKACIJE_ID_edukacije  INTEGER   NOT NULL,
            OSOBE_ID_osobe          INTEGER   NOT NULL,
            timestamp_rezervacije   TIMESTAMP NOT NULL,
            FOREIGN KEY (EDUKACIJE_ID_edukacije) 
                REFERENCES AKCIJE_EDUKACIJE(ID_edukacije),
            FOREIGN KEY (OSOBE_ID_osobe) 
                REFERENCES AKCIJE_OSOBE(ID_osobe)
        )
    """)
    duckdb_conn.execute("""
        CREATE TABLE AKCIJE_AKCIJE (
            ID_akcija                    INTEGER PRIMARY KEY,
            datum                        DATE,
            POPULACIJE_ID_populacije     INTEGER NOT NULL,
            TIPOVI_AKCIJA_ID_tipa_akcije INTEGER NOT NULL,
            TIMOVI_ID_tima               INTEGER,
            REZERVOARI_ID_rezervoara     INTEGER,
            FOREIGN KEY (POPULACIJE_ID_populacije) 
                REFERENCES VRSTE_POPULACIJE(ID_populacije),
            FOREIGN KEY (TIPOVI_AKCIJA_ID_tipa_akcije) 
                REFERENCES AKCIJE_TIPOVI_AKCIJA(ID_tipa_akcije),
            FOREIGN KEY (TIMOVI_ID_tima) 
                REFERENCES AKCIJE_TIMOVI(ID_tima),
            FOREIGN KEY (REZERVOARI_ID_rezervoara) 
                REFERENCES AKCIJE_REZERVOARI(ID_rezervoara)
        )
    """)

    print("DuckDB shema kreirana.")
    return


@app.cell
def _(duckdb_conn, mo):
    # prikaz sheme
    _tables_df  = duckdb_conn.sql(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_name LIKE 'VRSTE_%' OR table_name LIKE 'AKCIJE_%'"
    ).df()
    _columns_df = duckdb_conn.sql(
        "SELECT table_name, column_name, data_type "
        "FROM information_schema.columns "
        "WHERE table_name LIKE 'VRSTE_%' OR table_name LIKE 'AKCIJE_%'"
    ).df()

    # Dohvati informacije o stranim ključevima
    _fk_df = duckdb_conn.sql("""
        SELECT 
            fk.table_name as source_table,
            fk.column_name as source_column,
            pk.table_name as target_table,
            pk.column_name as target_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage fk 
            ON tc.constraint_name = fk.constraint_name
            AND tc.table_name = fk.table_name
        JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
        JOIN information_schema.key_column_usage pk
            ON rc.unique_constraint_name = pk.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
    """).df()

    _popis_tablica = set(_tables_df['table_name'].tolist())

    _mermaid_kod = "erDiagram\n"

    # Dodaj tablice i njihove stupce
    for _, _t_row in _tables_df.iterrows():
        _tablica = _t_row['table_name']
        _stapci_tablice = _columns_df[_columns_df['table_name'] == _tablica]

        _mermaid_kod += f"    {_tablica} {{\n"
        for _, _c_row in _stapci_tablice.iterrows():
            _col_name = _c_row['column_name']
            _col_type = _c_row['data_type']

            # Provjeri je li stupac primarni ključ
            _is_pk = False
            if 'ID_' in _col_name:
                # Provjeri je li ovo primarni ključ tablice
                _pk_check = duckdb_conn.sql(f"""
                    SELECT COUNT(*) as cnt
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_name = kcu.table_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_name = '{_tablica}'
                        AND kcu.column_name = '{_col_name}'
                """).fetchone()[0]
                _is_pk = _pk_check > 0

            _pk_oznaka = "PK" if _is_pk else ""
            _cisti_tip = _col_type.split("(")[0]
            _mermaid_kod += f"        {_cisti_tip} {_col_name} {_pk_oznaka}\n"
        _mermaid_kod += "    }\n"

    # Dodaj veze između tablica na temelju FK constrainta
    _dodane_veze = set()
    for _, _fk_row in _fk_df.iterrows():
        _source = _fk_row['source_table']
        _target = _fk_row['target_table']
        _veza_kljuc = f"{_source}->{_target}"

        if _veza_kljuc not in _dodane_veze and _source in _popis_tablica and _target in _popis_tablica:
            _mermaid_kod += f'    {_target} ||--o{{ {_source} : ""\n'
            _dodane_veze.add(_veza_kljuc)

    mo.mermaid(_mermaid_kod)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.2. Grafovska baza podataka (Kuzu)
    """)
    return


@app.cell
def _(mo):
    def vizualiziraj_kuzu_shemu(conn) -> mo.Html:
        tablice = conn.execute("CALL show_tables() RETURN *").get_as_df()

        node_defs = {}
        rel_defs = []

        for _, row in tablice.iterrows():
            naziv = row["name"]
            tip = row["type"]

            props = conn.execute(
                f"CALL table_info('{naziv}') RETURN *"
            ).get_as_df()

            if tip == "NODE":
                kolone = []
                for _, p in props.iterrows():
                    pk = " PK" if p.get("primary key", False) else ""
                    kolone.append(f"    {p['type']} {p['name']}{pk}")
                node_defs[naziv] = "\n".join(kolone)

            elif tip == "REL":
                src_rows = conn.execute(
                    f"CALL show_connection('{naziv}') RETURN *"
                ).get_as_df()
                for _, r in src_rows.iterrows():
                    rel_defs.append((r["source table name"], r["destination table name"], naziv))

        linije = ["erDiagram"]

        for naziv, kolone in node_defs.items():
            linije.append(f"  {naziv} {{")
            linije.append(kolone)
            linije.append("  }")

        for src, dst, naziv in rel_defs:
            linije.append(f'  {src} }}o--|| {dst} : "{naziv}"')

        return mo.mermaid("\n".join(linije))

    return (vizualiziraj_kuzu_shemu,)


@app.cell
def _(KUZU_PATH, kuzu):
    db_kuzu = kuzu.Database(KUZU_PATH)
    conn_kuzu = kuzu.Connection(db_kuzu)
    return (conn_kuzu,)


@app.cell
def _(conn_kuzu):
    # NODES

    # 1. Populacije
    conn_kuzu.execute("CREATE NODE TABLE Populacija(id INT64, PRIMARY KEY (id))")

    # 2. Taksonomija
    conn_kuzu.execute("""
        CREATE NODE TABLE TaksonomskaKategorija(
            id INT64, 
            ime STRING, 
            tip_id INT64, 
            ime_tipa STRING, 
            PRIMARY KEY (id)
        )
    """)

    # 3. Staništa
    conn_kuzu.execute("""
        CREATE NODE TABLE Staniste(
            id INT64, 
            naziv STRING, 
            opis STRING, 
            povrsina INT64, 
            PRIMARY KEY (id)
        )
    """)

    # 4. Ugroženost
    conn_kuzu.execute("""
        CREATE NODE TABLE StupanjUgrozenosti(
            id INT64, 
            oznaka STRING, 
            opis STRING, 
            red_stupnja INT64, 
            sustav_id INT64, 
            PRIMARY KEY(id)
        )
    """)

    conn_kuzu.execute("""
        CREATE NODE TABLE SustavStupnjeva(
            id INT64, 
            datum_pocetka STRING,
            datum_kraja STRING,
            PRIMARY KEY(id)
        )
    """)

    # 5. Timovi i organizacija (Dodana Mjesta i Edukacije)
    conn_kuzu.execute("CREATE NODE TABLE Osoba(id INT64, ime STRING, prezime STRING, mail STRING, datum_rodenja DATE, PRIMARY KEY(id))")
    conn_kuzu.execute("CREATE NODE TABLE Tim(id INT64, datum_nastanka DATE, PRIMARY KEY(id))")
    conn_kuzu.execute("CREATE NODE TABLE Mjesto(id INT64, naziv_mjesta STRING, postanski_br STRING, PRIMARY KEY(id))")
    conn_kuzu.execute("CREATE NODE TABLE Rezervoar(id INT64, naziv STRING, pocetni_broj_vrsta INT64, povrsina DOUBLE, PRIMARY KEY(id))")
    conn_kuzu.execute("CREATE NODE TABLE Akcija(id INT64, datum DATE, tip_akcije STRING, PRIMARY KEY(id))")
    conn_kuzu.execute("CREATE NODE TABLE Edukacija(id INT64, naziv_edukacije STRING, opis_edukacije STRING, datum_odrzavanja DATE, broj_mjesta INT64, broj_posjetitelja INT64, PRIMARY KEY(id))")
    conn_kuzu.execute("CREATE NODE TABLE Rezervacija(id INT64, timestamp_rezervacije TIMESTAMP, PRIMARY KEY(id))")
    return


@app.cell
def _(conn_kuzu):
    # RELATIONS

    # Taksonomija 
    conn_kuzu.execute("CREATE REL TABLE IMA_PREDKA(FROM TaksonomskaKategorija TO TaksonomskaKategorija)")
    conn_kuzu.execute("CREATE REL TABLE PRIPADA_TAKSONOMIJI(FROM Populacija TO TaksonomskaKategorija)")

    # Interakcije 
    conn_kuzu.execute("""
        CREATE REL TABLE INTERAGIRA(
            FROM Populacija TO Populacija,
            interakcija_id INT64,
            tip STRING,
            uloga1 STRING,
            uloga2 STRING,
            mutualan BOOLEAN
        )
    """)

    # Populacija - Stanište 
    conn_kuzu.execute("CREATE REL TABLE ZIVI_U(FROM Populacija TO Staniste)")

    # Ugroženost 
    conn_kuzu.execute("CREATE REL TABLE OZNACENA(FROM Populacija TO StupanjUgrozenosti, datum DATE)")
    conn_kuzu.execute("CREATE REL TABLE PRIPADA_SUSTAVU(FROM StupanjUgrozenosti TO SustavStupnjeva)")

    # Timovi, Mjesta i Edukacije 
    conn_kuzu.execute("CREATE REL TABLE CLAN_TIMA(FROM Osoba TO Tim, uloga STRING)")
    conn_kuzu.execute("CREATE REL TABLE STANUJE_U(FROM Osoba TO Mjesto)")
    conn_kuzu.execute("CREATE REL TABLE NALAZI_SE_U(FROM Rezervoar TO Mjesto)")
    conn_kuzu.execute("CREATE REL TABLE PROVODI(FROM Tim TO Akcija)")
    conn_kuzu.execute("CREATE REL TABLE CILJA(FROM Akcija TO Populacija)")
    conn_kuzu.execute("CREATE REL TABLE KORISTI_REZERVOAR(FROM Akcija TO Rezervoar)")

    # Edukacije veze
    conn_kuzu.execute("CREATE REL TABLE ORGANIZIRA(FROM Tim TO Edukacija)")
    conn_kuzu.execute("CREATE REL TABLE ODRZAVA_SE_U(FROM Edukacija TO Mjesto)")

    # Rezervacije edukacija veze
    conn_kuzu.execute("CREATE REL TABLE IMA_REZERVACIJU(FROM Edukacija TO Rezervacija)")
    conn_kuzu.execute("CREATE REL TABLE REZERVIRAO(FROM Osoba TO Rezervacija)")
    return


@app.cell
def _(conn_kuzu, vizualiziraj_kuzu_shemu):
    vizualiziraj_kuzu_shemu(conn_kuzu)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. Punjenje podataka
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.1. Relacijske baze
    """)
    return


@app.cell
def _(PODACI):
    # pomoćna funkcija za unos podataka
    def insert(conn, tablica, csv_ime):
        conn.execute(f"""
            INSERT INTO {tablica}
            SELECT * FROM read_csv_auto('{PODACI}/{csv_ime}', header=true)
        """)


    return (insert,)


@app.cell
def _(PODACI, os, pd):
    # pomoćna funkcija za predobradu podataka za taksonomiju, self-join
    def predobrada_taksonomija_self():
        nodes_df = pd.read_csv(os.path.join(PODACI, "taksonomija_nodes.csv"), sep=";")

        edges_df = pd.read_csv(os.path.join(PODACI, "taksonomija_edges.csv"), sep=";")

        parent_map = {
            int(r["target"]): int(r["source"]) for _, r in edges_df.iterrows()
        }

        all_ids = set(nodes_df["id"].astype(int))
        roots = all_ids - set(parent_map.keys())

        node_lookup = {int(r["id"]): r for _, r in nodes_df.iterrows()}

        children_map = {}
        for child, parent in parent_map.items():
            children_map.setdefault(parent, []).append(child)

        rows = []
        queue = list(sorted(roots))

        while queue:
            node_id = queue.pop(0)
            row = node_lookup[node_id]

            tip = row["type"]
            if pd.isna(tip):
                tip = None
            else:
                tip = int(tip)

            parent = parent_map.get(node_id)
            if pd.isna(parent):
                parent = None
            else:
                parent = int(parent)

            rows.append([int(node_id), str(row["label"]), tip, parent])

            queue.extend(children_map.get(node_id, []))

        df = pd.DataFrame(
            rows,
            columns=[
                "ID_taksonomije_self",
                "ime_kategorije",
                "TIPOVI_TAKSONOMIJA_ID_tipa",
                "TAKSONOMIJA_SELF_predak",
            ],
        )

        df = df.where(pd.notnull(df), None)

        return df

    return (predobrada_taksonomija_self,)


@app.cell
def _(
    DUCKDB_PATH,
    PODACI,
    duckdb_conn,
    insert,
    os,
    pd,
    predobrada_taksonomija_self,
    time,
):
    # insert, mjerenje performansi

    _t0 = time.perf_counter()

    insert(duckdb_conn, "VRSTE_SUSTAVI_STUPNJEVA_UGROZENOSTI", "sustavi_stupnjeva_ugrozenosti.csv")
    insert(duckdb_conn, "VRSTE_STUPNJEVI_UGROZENOSTI",          "stupnjevi_ugrozenosti.csv")
    insert(duckdb_conn, "VRSTE_TIPOVI_TAKSONOMIJA",             "tipovi_taksonomija.csv")
    insert(duckdb_conn, "VRSTE_STANISTA",                       "stanista.csv")
    insert(duckdb_conn, "VRSTE_INTERAKCIJE",                    "interakcije.csv")

    insert(duckdb_conn, "AKCIJE_MJESTA",                "mjesta.csv")
    insert(duckdb_conn, "AKCIJE_OSOBE",                 "osobe.csv")
    insert(duckdb_conn, "AKCIJE_TIMOVI",                "timovi.csv")
    insert(duckdb_conn, "AKCIJE_ULOGE",                 "uloge.csv")
    insert(duckdb_conn, "AKCIJE_TIPOVI_AKCIJA",         "tipovi_akcija.csv")
    insert(duckdb_conn, "AKCIJE_REZERVOARI",            "rezervoari.csv")

    # taksonomije moraju ovako jer csv zahtjeva predobradu, ona se računa u vrijeme jer je realan trošak
    _t0_taks = time.perf_counter()
    _taksonomija_df = predobrada_taksonomija_self()

    podaci_za_unos = [
        [None if pd.isna(val) else val for val in row]# osigurava da DuckDB dobije None, ne nan
        for row in _taksonomija_df.values.tolist()
    ]
    duckdb_taksonomija_predobrada_vrijeme = time.perf_counter() - _t0_taks

    duckdb_conn.executemany(
        """
        INSERT INTO VRSTE_TAKSONOMIJA_SELF 
        VALUES (?, ?, ?, ?)
        """,
        podaci_za_unos,
    )



    # populacije moraju ovako jer csv ima viška kolonu koju treba izbaciti prije unošenja
    _df = pd.read_csv(os.path.join(PODACI, "populacije.csv"), sep=";")
    duckdb_conn.register(
        "tmp_populacije",
        _df.drop(columns=["TAKSONOMIJE_C_ID_taksonomije"])
    )
    duckdb_conn.execute("""
        INSERT INTO VRSTE_POPULACIJE
        SELECT * FROM tmp_populacije
    """)
    insert(duckdb_conn, "VRSTE_STUPNJEVI_UGROZENOSTI_POPULACIJE", "stupnjevi_ugrozenosti_populacije.csv")
    insert(duckdb_conn, "VRSTE_MEDUODNOSI",                     "meduodnosi.csv")

    insert(duckdb_conn, "AKCIJE_TIMOVI_OSOBE",          "timovi_osobe.csv")
    insert(duckdb_conn, "AKCIJE_EDUKACIJE",             "edukacije.csv")
    insert(duckdb_conn, "AKCIJE_REZERVACIJE_EDUKACIJA", "rezervacije_edukacija.csv")
    insert(duckdb_conn, "AKCIJE_AKCIJE",                "akcije.csv")

    duckdb_vrijeme  = time.perf_counter() - _t0
    duckdb_velicina = os.path.getsize(DUCKDB_PATH)

    print(f"DuckDB:\n punjenje: {duckdb_vrijeme:.3f}s | Veličina: {duckdb_velicina/1024:.1f} KB")
    return (
        duckdb_taksonomija_predobrada_vrijeme,
        duckdb_velicina,
        duckdb_vrijeme,
    )


@app.cell
def _(duckdb_taksonomija_predobrada_vrijeme):
    print(f"DuckDB:\n potrošeno na predobradu: {duckdb_taksonomija_predobrada_vrijeme:.3f}s")
    return


@app.cell(hide_code=True)
def _(
    akcije_akcije,
    akcije_edukacije,
    akcije_mjesta,
    akcije_osobe,
    akcije_rezervacije_edukacija,
    akcije_rezervoari,
    akcije_timovi,
    akcije_timovi_osobe,
    akcije_tipovi_akcija,
    akcije_uloge,
    duckdb_conn,
    mo,
    vrste_interakcije,
    vrste_meduodnosi,
    vrste_populacije,
    vrste_stanista,
    vrste_stupnjevi_ugrozenosti,
    vrste_stupnjevi_ugrozenosti_populacije,
    vrste_sustavi_stupnjeva_ugrozenosti,
    vrste_taksonomija_self,
    vrste_tipovi_taksonomija,
):
    _df = mo.sql(
        f"""
        SELECT 'VRSTE_SUSTAVI_STUPNJEVA_UGROZENOSTI' AS tablica, COUNT(*) AS broj_redova FROM VRSTE_SUSTAVI_STUPNJEVA_UGROZENOSTI
            UNION ALL SELECT 'VRSTE_STUPNJEVI_UGROZENOSTI', COUNT(*) FROM VRSTE_STUPNJEVI_UGROZENOSTI
            UNION ALL SELECT 'VRSTE_TIPOVI_TAKSONOMIJA', COUNT(*) FROM VRSTE_TIPOVI_TAKSONOMIJA
            UNION ALL SELECT 'VRSTE_TAKSONOMIJA_SELF', COUNT(*) FROM VRSTE_TAKSONOMIJA_SELF
            UNION ALL SELECT 'VRSTE_STANISTA', COUNT(*) FROM VRSTE_STANISTA
            UNION ALL SELECT 'VRSTE_INTERAKCIJE', COUNT(*) FROM VRSTE_INTERAKCIJE
            UNION ALL SELECT 'VRSTE_POPULACIJE', COUNT(*) FROM VRSTE_POPULACIJE
            UNION ALL SELECT 'VRSTE_STUPNJEVI_UGROZENOSTI_POPULACIJE',  COUNT(*) FROM VRSTE_STUPNJEVI_UGROZENOSTI_POPULACIJE
            UNION ALL SELECT 'VRSTE_MEDUODNOSI', COUNT(*) FROM VRSTE_MEDUODNOSI
            UNION ALL SELECT 'AKCIJE_MJESTA', COUNT(*) FROM AKCIJE_MJESTA
            UNION ALL SELECT 'AKCIJE_TIPOVI_AKCIJA', COUNT(*) FROM AKCIJE_TIPOVI_AKCIJA
            UNION ALL SELECT 'AKCIJE_REZERVOARI', COUNT(*) FROM AKCIJE_REZERVOARI
            UNION ALL SELECT 'AKCIJE_OSOBE', COUNT(*) FROM AKCIJE_OSOBE
            UNION ALL SELECT 'AKCIJE_TIMOVI', COUNT(*) FROM AKCIJE_TIMOVI
            UNION ALL SELECT 'AKCIJE_ULOGE', COUNT(*) FROM AKCIJE_ULOGE
            UNION ALL SELECT 'AKCIJE_TIMOVI_OSOBE', COUNT(*) FROM AKCIJE_TIMOVI_OSOBE
            UNION ALL SELECT 'AKCIJE_EDUKACIJE', COUNT(*) FROM AKCIJE_EDUKACIJE
            UNION ALL SELECT 'AKCIJE_REZERVACIJE_EDUKACIJA', COUNT(*) FROM AKCIJE_REZERVACIJE_EDUKACIJA
            UNION ALL SELECT 'AKCIJE_AKCIJE', COUNT(*) FROM AKCIJE_AKCIJE
            ORDER BY tablica
        """,
        engine=duckdb_conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.2. Graf baze
    """)
    return


@app.function
# pomoćna funkcija za castanje tipova podataka
def kuzu_fix(df):
    df = df.copy()
    for col in df.columns:
        if str(df[col].dtype) not in ("int64", "int32", "float64", "float32", "bool"):
            df[col] = df[col].astype(str).astype(object)
    return df


@app.cell
def _(KUZU_PATH, PODACI, conn_kuzu, os, pd, time):
    _t0 = time.perf_counter()

    # 1. NODES

    # Populacija
    pop_df = pd.read_csv(os.path.join(PODACI, "populacije.csv"), sep=";")
    pop_nodes = pop_df[['ID_populacije']].dropna().rename(columns={'ID_populacije': 'id'})
    pop_nodes['id'] = pop_nodes['id'].astype('int64')
    pop_nodes = pop_nodes[['id']]
    pop_nodes = kuzu_fix(pop_nodes)
    conn_kuzu.execute("COPY Populacija FROM pop_nodes")

    # Staniste
    stan_df = pd.read_csv(os.path.join(PODACI, "stanista.csv"), sep=";")
    stan_nodes = stan_df.dropna(subset=['ID_stanista']).rename(columns={'ID_stanista': 'id'})
    stan_nodes['id'] = stan_nodes['id'].astype('int64')
    stan_nodes['naziv'] = stan_nodes['naziv'].fillna('').astype(str)
    stan_nodes['opis'] = stan_nodes['opis'].fillna('').astype(str)
    stan_nodes['povrsina'] = stan_nodes['povrsina'].fillna(0).astype('int64')
    stan_nodes = stan_nodes[['id', 'naziv', 'opis', 'povrsina']]
    stan_nodes = kuzu_fix(stan_nodes)
    conn_kuzu.execute("COPY Staniste FROM stan_nodes")

    # TaksonomskaKategorija
    tax_nodes_df = pd.read_csv(os.path.join(PODACI, "taksonomija_nodes.csv"), sep=";")
    tax_nodes = tax_nodes_df.dropna(subset=['id']).rename(columns={'id': 'id', 'label': 'ime', 'type': 'tip_id'})
    tax_nodes['id'] = tax_nodes['id'].astype('int64')
    tax_nodes['ime'] = tax_nodes['ime'].fillna('').astype(str)
    tax_nodes['tip_id'] = tax_nodes['tip_id'].astype('int64')
    _tipovi_df = pd.read_csv(os.path.join(PODACI, "tipovi_taksonomija.csv"), sep=";")
    tip_id_to_ime = dict(zip(_tipovi_df['ID_tipa'], _tipovi_df['ime_tipa']))
    tax_nodes['ime_tipa'] = tax_nodes['tip_id'].map(tip_id_to_ime).fillna('').astype(str)
    tax_nodes = tax_nodes[['id', 'ime', 'tip_id', 'ime_tipa']]
    tax_nodes = kuzu_fix(tax_nodes)
    conn_kuzu.execute("COPY TaksonomskaKategorija FROM tax_nodes")

    # StupanjUgrozenosti
    st_ugr = pd.read_csv(os.path.join(PODACI, "stupnjevi_ugrozenosti.csv"), sep=";").rename(
        columns={
            'ID_stupnja': 'id',
            'oznaka_stupnja': 'oznaka',
            'opis_stupnja': 'opis',
            'red_stupnja_ugrozenosti': 'red_stupnja',
            'SUSTAVI_STUPNJEVA_UGROZENOSTI_ID_sustava': 'sustav_id'
        }
    )
    st_ugr = st_ugr.dropna(subset=['id'])
    st_ugr['id'] = st_ugr['id'].astype('int64')
    st_ugr['oznaka'] = st_ugr['oznaka'].fillna('').astype(str)
    st_ugr['opis'] = st_ugr['opis'].fillna('').astype(str)
    st_ugr['red_stupnja'] = st_ugr['red_stupnja'].astype('int64')
    st_ugr['sustav_id'] = st_ugr['sustav_id'].astype('int64')
    st_ugr = st_ugr[['id', 'oznaka', 'opis', 'red_stupnja', 'sustav_id']]
    st_ugr = kuzu_fix(st_ugr)
    conn_kuzu.execute("COPY StupanjUgrozenosti FROM st_ugr")

    # SustavStupnjeva
    sust_ugr = pd.read_csv(os.path.join(PODACI, "sustavi_stupnjeva_ugrozenosti.csv"), sep=";").rename(
        columns={
            'ID_sustava': 'id',
            'datum_pocetka_koristenja': 'datum_pocetka',
            'datum_kraja_koristenja': 'datum_kraja'
        }
    )
    sust_ugr = sust_ugr.dropna(subset=['id'])
    sust_ugr['id'] = sust_ugr['id'].astype('int64')
    sust_ugr['datum_pocetka'] = pd.to_datetime(sust_ugr['datum_pocetka']).dt.strftime('%Y-%m-%d').fillna('')
    sust_ugr['datum_kraja'] = pd.to_datetime(sust_ugr['datum_kraja']).dt.strftime('%Y-%m-%d').fillna('')

    sust_ugr = sust_ugr[['id', 'datum_pocetka', 'datum_kraja']]
    sust_ugr = kuzu_fix(sust_ugr)
    conn_kuzu.execute("COPY SustavStupnjeva FROM sust_ugr")

    # Osoba
    osobe_df = pd.read_csv(os.path.join(PODACI, "osobe.csv"), sep=";").rename(columns={'ID_osobe': 'id'})
    osobe_df = osobe_df.dropna(subset=['id'])
    osobe_df['id'] = osobe_df['id'].astype('int64')
    osobe_df['ime'] = osobe_df['ime'].fillna('').astype(str)
    osobe_df['prezime'] = osobe_df['prezime'].fillna('').astype(str)
    osobe_df['mail'] = osobe_df['mail'].fillna('').astype(str)
    osobe_df['datum_rodenja'] = pd.to_datetime(osobe_df['datum_rodenja']).dt.date
    osobe_df = osobe_df[['id', 'ime', 'prezime', 'mail', 'datum_rodenja']]
    osobe_df = kuzu_fix(osobe_df)
    conn_kuzu.execute("COPY Osoba FROM osobe_df")

    # Tim
    timovi_df = pd.read_csv(os.path.join(PODACI, "timovi.csv"), sep=";").rename(columns={'ID_tima': 'id'})
    timovi_df = timovi_df.dropna(subset=['id'])
    timovi_df['id'] = timovi_df['id'].astype('int64')
    timovi_df['datum_nastanka'] = pd.to_datetime(timovi_df['datum_nastanka']).dt.date
    timovi_df = timovi_df[['id', 'datum_nastanka']]
    timovi_df = kuzu_fix(timovi_df)
    conn_kuzu.execute("COPY Tim FROM timovi_df")

    # Mjesto
    mjesta_df = pd.read_csv(os.path.join(PODACI, "mjesta.csv"), sep=";").rename(columns={'ID_mjesta': 'id'})
    mjesta_df = mjesta_df.dropna(subset=['id'])
    mjesta_df['id'] = mjesta_df['id'].astype('int64')
    mjesta_df['naziv_mjesta'] = mjesta_df['naziv_mjesta'].fillna('').astype(str)
    mjesta_df['postanski_br'] = mjesta_df['postanski_br'].fillna('').astype(str)
    mjesta_df = mjesta_df[['id', 'naziv_mjesta', 'postanski_br']]
    mjesta_df = kuzu_fix(mjesta_df)
    conn_kuzu.execute("COPY Mjesto FROM mjesta_df")

    # Rezervoar
    rez_df = pd.read_csv(os.path.join(PODACI, "rezervoari.csv"), sep=";").rename(columns={'ID_rezervoara': 'id', 'naziv_rezervoara': 'naziv'})
    rez_df = rez_df.dropna(subset=['id'])
    rez_df['id'] = rez_df['id'].astype('int64')
    rez_df['naziv'] = rez_df['naziv'].fillna('').astype(str)
    rez_df['pocetni_broj_vrsta'] = rez_df['pocetni_broj_vrsta'].fillna(0).astype('int64')
    rez_df['povrsina'] = rez_df['povrsina'].fillna(0.0).astype('float64')
    rez_df = rez_df[['id', 'naziv', 'pocetni_broj_vrsta', 'povrsina']]
    rez_df = kuzu_fix(rez_df)
    conn_kuzu.execute("COPY Rezervoar FROM rez_df")

    # Akcija
    akcije_raw = pd.read_csv(os.path.join(PODACI, "akcije.csv"), sep=";")
    tipovi_akcija_df = pd.read_csv(os.path.join(PODACI, "tipovi_akcija.csv"), sep=";")
    akcije_merged = akcije_raw.merge(tipovi_akcija_df, left_on='TIPOVI_AKCIJA_ID_tipa_akcije', right_on='ID_tipa_akcije', how='left')
    akcije_nodes = akcije_merged[['ID_akcija', 'datum', 'naziv_akcije']].rename(columns={'ID_akcija': 'id', 'naziv_akcije': 'tip_akcije'})
    akcije_nodes = akcije_nodes.dropna(subset=['id'])
    akcije_nodes['id'] = akcije_nodes['id'].astype('int64')
    akcije_nodes['datum'] = pd.to_datetime(akcije_nodes['datum']).dt.date
    akcije_nodes['tip_akcije'] = akcije_nodes['tip_akcije'].fillna('').astype(str)
    akcije_nodes = akcije_nodes[['id', 'datum', 'tip_akcije']]
    akcije_nodes = kuzu_fix(akcije_nodes)
    conn_kuzu.execute("COPY Akcija FROM akcije_nodes")

    # Edukacija
    edukacije_df = pd.read_csv(os.path.join(PODACI, "edukacije.csv"), sep=";").rename(columns={'ID_edukacije': 'id'})
    edukacije_df = edukacije_df.dropna(subset=['id'])
    edukacije_df['id'] = edukacije_df['id'].astype('int64')
    edukacije_df['naziv_edukacije'] = edukacije_df['naziv_edukacije'].fillna('').astype(str)
    edukacije_df['opis_edukacije'] = edukacije_df['opis_edukacije'].fillna('').astype(str)
    edukacije_df['datum_odrzavanja'] = pd.to_datetime(edukacije_df['datum_odrzavanja']).dt.date
    edukacije_df['broj_mjesta'] = edukacije_df['broj_mjesta'].fillna(0).astype('int64')
    edukacije_df['broj_posjetitelja'] = edukacije_df['broj_posjetitelja'].fillna(0).astype('int64')
    edukacije_df = edukacije_df[['id', 'naziv_edukacije', 'opis_edukacije', 'datum_odrzavanja', 'broj_mjesta', 'broj_posjetitelja']]
    edukacije_df = kuzu_fix(edukacije_df)
    conn_kuzu.execute("COPY Edukacija FROM edukacije_df")

    # Rezervacija
    rez_ed_df = pd.read_csv(os.path.join(PODACI, "rezervacije_edukacija.csv"), sep=";").rename(columns={'ID_rezervacije': 'id'})
    rez_ed_df = rez_ed_df.dropna(subset=['id'])
    rez_ed_df['id'] = rez_ed_df['id'].astype('int64')
    rez_ed_df['timestamp_rezervacije'] = pd.to_datetime(rez_ed_df['timestamp_rezervacije'])
    rez_ed_df = rez_ed_df[['id', 'timestamp_rezervacije']]
    rez_ed_df = kuzu_fix(rez_ed_df)
    conn_kuzu.execute("COPY Rezervacija FROM rez_ed_df")

    # 2. RELATIONS (BRIDOVI / VEZE)

    # IMA_PREDKA
    tax_edges = pd.read_csv(os.path.join(PODACI, "taksonomija_edges.csv"), sep=";").rename(columns={'source': 'from', 'target': 'to'})
    tax_edges = tax_edges.dropna(subset=['from', 'to'])
    tax_edges['from'] = tax_edges['from'].astype('int64')
    tax_edges['to'] = tax_edges['to'].astype('int64')
    tax_edges = tax_edges[['from', 'to']]
    tax_edges = kuzu_fix(tax_edges)
    conn_kuzu.execute("COPY IMA_PREDKA FROM tax_edges")

    # PRIPADA_TAKSONOMIJI
    pop_tax_rel = pop_df[['ID_populacije', 'TAKSONOMIJA_SELF_ID_taksonomije_self']].dropna(subset=['ID_populacije', 'TAKSONOMIJA_SELF_ID_taksonomije_self']).rename(columns={'ID_populacije': 'from', 'TAKSONOMIJA_SELF_ID_taksonomije_self': 'to'})
    pop_tax_rel['from'] = pop_tax_rel['from'].astype('int64')
    pop_tax_rel['to'] = pop_tax_rel['to'].astype('int64')
    pop_tax_rel = pop_tax_rel[['from', 'to']]
    pop_tax_rel = kuzu_fix(pop_tax_rel)
    conn_kuzu.execute("COPY PRIPADA_TAKSONOMIJI FROM pop_tax_rel")

    # ZIVI_U
    pop_stan_rel = pop_df[['ID_populacije', 'STANISTA_ID_stanista']].dropna(subset=['ID_populacije', 'STANISTA_ID_stanista']).rename(columns={'ID_populacije': 'from', 'STANISTA_ID_stanista': 'to'})
    pop_stan_rel['from'] = pop_stan_rel['from'].astype('int64')
    pop_stan_rel['to'] = pop_stan_rel['to'].astype('int64')
    pop_stan_rel = pop_stan_rel[['from', 'to']]
    pop_stan_rel = kuzu_fix(pop_stan_rel)
    conn_kuzu.execute("COPY ZIVI_U FROM pop_stan_rel")

    # INTERAGIRA
    medu_raw = pd.read_csv(os.path.join(PODACI, "meduodnosi.csv"), sep=";")
    int_defs = pd.read_csv(os.path.join(PODACI, "interakcije.csv"), sep=";")
    medu_m = medu_raw.merge(int_defs, left_on='INTERAKCIJE_ID_interakcije', right_on='ID_interakcije')
    medu_rel = medu_m[['POPULACIJE_ID_populacije1', 'POPULACIJE_ID_populacije2', 'PK_ID_meduodnosa', 'interakcija', 'uloga1', 'uloga2', 'mutualan']].rename(
        columns={'POPULACIJE_ID_populacije1': 'from', 'POPULACIJE_ID_populacije2': 'to', 'PK_ID_meduodnosa': 'interakcija_id', 'interakcija': 'tip'}
    )
    medu_rel = medu_rel.dropna(subset=['from', 'to'])
    medu_rel['from'] = medu_rel['from'].astype('int64')
    medu_rel['to'] = medu_rel['to'].astype('int64')
    medu_rel['interakcija_id'] = medu_rel['interakcija_id'].astype('int64')
    medu_rel['tip'] = medu_rel['tip'].fillna('').astype(str)
    medu_rel['uloga1'] = medu_rel['uloga1'].fillna('').astype(str)
    medu_rel['uloga2'] = medu_rel['uloga2'].fillna('').astype(str)
    medu_rel['mutualan'] = medu_rel['mutualan'].fillna(False).astype('bool')
    medu_rel = medu_rel[['from', 'to', 'interakcija_id', 'tip', 'uloga1', 'uloga2', 'mutualan']]
    medu_rel = kuzu_fix(medu_rel)
    conn_kuzu.execute("COPY INTERAGIRA FROM medu_rel")

    # OZNACENA
    ugr_pop = pd.read_csv(os.path.join(PODACI, "stupnjevi_ugrozenosti_populacije.csv"), sep=";").rename(columns={'POPULACIJE_ID_populacije': 'from', 'STUPNJEVI_UGROZENOSTI_ID_stupnja': 'to'})
    ugr_pop = ugr_pop.dropna(subset=['from', 'to'])
    ugr_pop['from'] = ugr_pop['from'].astype('int64')
    ugr_pop['to'] = ugr_pop['to'].astype('int64')
    ugr_pop['datum'] = pd.to_datetime(ugr_pop['datum']).dt.date
    ugr_pop = ugr_pop[['from', 'to', 'datum']]
    ugr_pop = kuzu_fix(ugr_pop)
    conn_kuzu.execute("COPY OZNACENA FROM ugr_pop")

    # PRIPADA_SUSTAVU
    st_sust_rel = pd.read_csv(os.path.join(PODACI, "stupnjevi_ugrozenosti.csv"), sep=";").rename(columns={'ID_stupnja': 'from', 'SUSTAVI_STUPNJEVA_UGROZENOSTI_ID_sustava': 'to'})
    st_sust_rel = st_sust_rel.dropna(subset=['from', 'to'])
    st_sust_rel['from'] = st_sust_rel['from'].astype('int64')
    st_sust_rel['to'] = st_sust_rel['to'].astype('int64')
    st_sust_rel = st_sust_rel[['from', 'to']]
    st_sust_rel = kuzu_fix(st_sust_rel)
    conn_kuzu.execute("COPY PRIPADA_SUSTAVU FROM st_sust_rel")

    # CLAN_TIMA
    uloge_df = pd.read_csv(os.path.join(PODACI, "uloge.csv"), sep=";")
    tim_os_raw = pd.read_csv(os.path.join(PODACI, "timovi_osobe.csv"), sep=";").merge(
        uloge_df, left_on='ULOGE_ID_uloga', right_on='ID_uloga')
    tim_os_rel = tim_os_raw[['OSOBE_ID_osobe', 'TIMOVI_ID_tima', 'naziv_uloge']].rename(columns={'OSOBE_ID_osobe': 'from', 'TIMOVI_ID_tima': 'to', 'naziv_uloge': 'uloga'})
    tim_os_rel = tim_os_rel.dropna(subset=['from', 'to'])
    tim_os_rel['from'] = tim_os_rel['from'].astype('int64')
    tim_os_rel['to'] = tim_os_rel['to'].astype('int64')
    tim_os_rel['uloga'] = tim_os_rel['uloga'].fillna('').astype(str)
    tim_os_rel = tim_os_rel[['from', 'to', 'uloga']]
    tim_os_rel = kuzu_fix(tim_os_rel)
    conn_kuzu.execute("COPY CLAN_TIMA FROM tim_os_rel")

    # STANUJE_U
    osobe_raw = pd.read_csv(os.path.join(PODACI, "osobe.csv"), sep=";")
    osoba_mjesto_rel = osobe_raw[['ID_osobe', 'MJESTA_ID_mjesta_stanovanja']].dropna().copy()
    osoba_mjesto_rel = osoba_mjesto_rel.rename(columns={'ID_osobe': 'from', 'MJESTA_ID_mjesta_stanovanja': 'to'})
    osoba_mjesto_rel['from'] = osoba_mjesto_rel['from'].astype('int64')
    osoba_mjesto_rel['to'] = osoba_mjesto_rel['to'].astype('int64')
    osoba_mjesto_rel = osoba_mjesto_rel[['from', 'to']]
    osoba_mjesto_rel = kuzu_fix(osoba_mjesto_rel)
    conn_kuzu.execute("COPY STANUJE_U FROM osoba_mjesto_rel")

    # NALAZI_SE_U
    rez_raw = pd.read_csv(os.path.join(PODACI, "rezervoari.csv"), sep=";")
    rez_mjesto_rel = rez_raw[['ID_rezervoara', 'MJESTA_ID_mjesta']].dropna().rename(columns={'ID_rezervoara': 'from', 'MJESTA_ID_mjesta': 'to'})
    rez_mjesto_rel['from'] = rez_mjesto_rel['from'].astype('int64')
    rez_mjesto_rel['to'] = rez_mjesto_rel['to'].astype('int64')
    rez_mjesto_rel = rez_mjesto_rel[['from', 'to']]
    rez_mjesto_rel = kuzu_fix(rez_mjesto_rel)
    conn_kuzu.execute("COPY NALAZI_SE_U FROM rez_mjesto_rel")

    # PROVODI
    akc_tim_rel = akcije_raw[['TIMOVI_ID_tima', 'ID_akcija']].dropna().copy()
    akc_tim_rel = akc_tim_rel.rename(columns={'TIMOVI_ID_tima': 'from', 'ID_akcija': 'to'})
    akc_tim_rel['from'] = akc_tim_rel['from'].astype('int64')
    akc_tim_rel['to'] = akc_tim_rel['to'].astype('int64')
    akc_tim_rel = akc_tim_rel[['from', 'to']]
    akc_tim_rel = kuzu_fix(akc_tim_rel)
    conn_kuzu.execute("COPY PROVODI FROM akc_tim_rel")

    # CILJA
    akc_pop_rel = akcije_raw[['ID_akcija', 'POPULACIJE_ID_populacije']].dropna().rename(columns={'ID_akcija': 'from', 'POPULACIJE_ID_populacije': 'to'})
    akc_pop_rel['from'] = akc_pop_rel['from'].astype('int64')
    akc_pop_rel['to'] = akc_pop_rel['to'].astype('int64')
    akc_pop_rel = akc_pop_rel[['from', 'to']]
    akc_pop_rel = kuzu_fix(akc_pop_rel)
    conn_kuzu.execute("COPY CILJA FROM akc_pop_rel")

    # KORISTI_REZERVOAR
    akc_rez_rel = akcije_raw[['ID_akcija', 'REZERVOARI_ID_rezervoara']].dropna().copy()
    akc_rez_rel = akc_rez_rel.rename(columns={'ID_akcija': 'from', 'REZERVOARI_ID_rezervoara': 'to'})
    akc_rez_rel['from'] = akc_rez_rel['from'].astype('int64')
    akc_rez_rel['to'] = akc_rez_rel['to'].astype('int64')
    akc_rez_rel = akc_rez_rel[['from', 'to']]
    akc_rez_rel = kuzu_fix(akc_rez_rel)
    conn_kuzu.execute("COPY KORISTI_REZERVOAR FROM akc_rez_rel")

    # ORGANIZIRA
    edukacije_raw = pd.read_csv(os.path.join(PODACI, "edukacije.csv"), sep=";")
    ed_tim_rel = edukacije_raw[['TIMOVI_ID_tima', 'ID_edukacije']].dropna().rename(columns={'TIMOVI_ID_tima': 'from', 'ID_edukacije': 'to'})
    ed_tim_rel['from'] = ed_tim_rel['from'].astype('int64')
    ed_tim_rel['to'] = ed_tim_rel['to'].astype('int64')
    ed_tim_rel = ed_tim_rel[['from', 'to']]
    ed_tim_rel = kuzu_fix(ed_tim_rel)
    conn_kuzu.execute("COPY ORGANIZIRA FROM ed_tim_rel")

    # ODRZAVA_SE_U
    ed_mj_rel = edukacije_raw[['ID_edukacije', 'MJESTA_ID_mjesta']].dropna().rename(columns={'ID_edukacije': 'from', 'MJESTA_ID_mjesta': 'to'})
    ed_mj_rel['from'] = ed_mj_rel['from'].astype('int64')
    ed_mj_rel['to'] = ed_mj_rel['to'].astype('int64')
    ed_mj_rel = ed_mj_rel[['from', 'to']]
    ed_mj_rel = kuzu_fix(ed_mj_rel)
    conn_kuzu.execute("COPY ODRZAVA_SE_U FROM ed_mj_rel")

    # IMA_REZERVACIJU
    rez_edukacije_raw = pd.read_csv(os.path.join(PODACI, "rezervacije_edukacija.csv"), sep=";")
    ed_rez_rel = rez_edukacije_raw[['EDUKACIJE_ID_edukacije', 'ID_rezervacije']].dropna().rename(columns={'EDUKACIJE_ID_edukacije': 'from', 'ID_rezervacije': 'to'})
    ed_rez_rel['from'] = ed_rez_rel['from'].astype('int64')
    ed_rez_rel['to'] = ed_rez_rel['to'].astype('int64')
    ed_rez_rel = ed_rez_rel[['from', 'to']]
    ed_rez_rel = kuzu_fix(ed_rez_rel)
    conn_kuzu.execute("COPY IMA_REZERVACIJU FROM ed_rez_rel")

    # REZERVIRAO
    os_rez_rel = rez_edukacije_raw[['OSOBE_ID_osobe', 'ID_rezervacije']].dropna().rename(columns={'OSOBE_ID_osobe': 'from', 'ID_rezervacije': 'to'})
    os_rez_rel['from'] = os_rez_rel['from'].astype('int64')
    os_rez_rel['to'] = os_rez_rel['to'].astype('int64')
    os_rez_rel = os_rez_rel[['from', 'to']]
    os_rez_rel = kuzu_fix(os_rez_rel)
    conn_kuzu.execute("COPY REZERVIRAO FROM os_rez_rel")

    kuzu_vrijeme = time.perf_counter() - _t0
    kuzu_velicina = os.path.getsize(KUZU_PATH)
    return kuzu_velicina, kuzu_vrijeme


@app.cell
def _(kuzu_velicina, kuzu_vrijeme):
    print(f"Kuzu:\n punjenje: {kuzu_vrijeme:.3f}s | Veličina: {kuzu_velicina/1024:.1f} KB")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. Usporedba
    """)
    return


@app.cell
def _(duckdb_velicina, duckdb_vrijeme, kuzu_velicina, kuzu_vrijeme):
    print(f"DuckDB:\n punjenje: {duckdb_vrijeme:.3f}s | Veličina: {duckdb_velicina/1024:.1f} KB")
    print(f"Kuzu:\n punjenje: {kuzu_vrijeme:.3f}s | Veličina: {kuzu_velicina/1024:.1f} KB")
    return


@app.cell
def _(
    duckdb_velicina,
    duckdb_vrijeme,
    go,
    kuzu_velicina,
    kuzu_vrijeme,
    make_subplots,
):
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Vrijeme punjenja (s)", "Veličina baze (KB)")
    )

    fig.add_trace(
        go.Bar(
            x=["DuckDB", "Kuzu"],
            y=[duckdb_vrijeme, kuzu_vrijeme],
            name="Vrijeme"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=["DuckDB", "Kuzu"],
            y=[duckdb_velicina / 1024, kuzu_velicina / 1024],
            name="Veličina"
        ),
        row=1,
        col=2
    )

    fig.update_layout(
        title="DuckDB vs Kuzu",
        showlegend=False,
        height=400
    )

    fig
    return


@app.cell
def _(conn_kuzu, duckdb_conn):
    # zatvaranje konekcija s bazama podataka
    duckdb_conn.close()
    conn_kuzu.close()

    print("Konekcije s DuckDB i Kuzu bazama su uspješno zatvorene.")
    return


if __name__ == "__main__":
    app.run()
