import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Usporedba relacijske i grafovske baze podataka
    """)
    return


@app.cell
def _():
    import marimo as mo
    import duckdb
    import kuzu
    import time
    import pandas as pd
    import os
    import statistics

    return duckdb, kuzu, mo, pd, statistics, time


@app.cell
def _():
    N_RUNS = 11
    return (N_RUNS,)


@app.cell
def _(duckdb):
    DUCKDB_PATH = "baze/relacijska_baza.duckdb"
    duckdb_conn = duckdb.connect(DUCKDB_PATH)
    print("DuckDB spojen:", DUCKDB_PATH)
    return (duckdb_conn,)


@app.cell
def _(kuzu):
    KUZU_PATH = "baze/graf_baza.kuzu"
    db_kuzu   = kuzu.Database(KUZU_PATH)
    conn_kuzu = kuzu.Connection(db_kuzu)
    print("Kuzu spojen:", KUZU_PATH)
    return (conn_kuzu,)


@app.cell
def _(statistics, time):
    def mjeri_sql(conn, sql: str, params=None, n=11):
        vremena = []
        result = None
        for _ in range(n):
            t0 = time.perf_counter()
            result = conn.execute(sql, parameters=params).df() if params else conn.execute(sql).df()
            vremena.append(time.perf_counter() - t0)
        return result, statistics.median(vremena)

    return (mjeri_sql,)


@app.cell
def _(statistics, time):
    def mjeri_kuzu(conn, cypher: str, params=None, n=11):
        vremena = []
        result = None
        for _ in range(n):
            t0 = time.perf_counter()
            result = conn.execute(cypher, params).get_as_df() if params else conn.execute(cypher).get_as_df()
            vremena.append(time.perf_counter() - t0)
        return result, statistics.median(vremena)

    return (mjeri_kuzu,)


@app.cell
def _(mo):
    def prikazi_usporedbu(
        naziv: str,
        sql_df, sql_t,
        kuzu_df, kuzu_t,
        mo=mo
    ):
        sql_ms = sql_t * 1000
        kuzu_ms = kuzu_t * 1000

        return mo.vstack([
            mo.md(f"### {naziv}"),

            mo.hstack([
                mo.vstack([
                    mo.md("**DuckDB**"),
                    mo.md(f"vrijeme: `{sql_ms:.2f} ms`"),
                    mo.ui.table(sql_df) if sql_df is not None and not sql_df.empty else mo.md("_(nema rezultata)_"),
                ]),
                mo.vstack([
                    mo.md("**Kuzu**"),
                    mo.md(f"vrijeme: `{kuzu_ms:.2f} ms`"),
                    mo.ui.table(kuzu_df) if kuzu_df is not None and not kuzu_df.empty else mo.md("_(nema rezultata)_"),
                ]),
            ]),

        ])

    return (prikazi_usporedbu,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. OSNOVNI 1-HOP DOHVAT
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.1.Aktivnost tima
    """)
    return


@app.cell
def _(N_RUNS, duckdb_conn, mjeri_sql):
    TIM_ID_1A = 10

    _sql = """
    SELECT
        t.ID_tima,
        COUNT(DISTINCT tio.OSOBE_ID_osobe) AS broj_clanova,
        COUNT(DISTINCT e.ID_edukacije) AS broj_edukacija,
        COUNT(DISTINCT a.ID_akcija) AS broj_akcije
    FROM AKCIJE_TIMOVI t
    LEFT JOIN AKCIJE_TIMOVI_OSOBE tio
        ON tio.TIMOVI_ID_tima = t.ID_tima
    LEFT JOIN AKCIJE_EDUKACIJE e
        ON e.TIMOVI_ID_tima = t.ID_tima
    LEFT JOIN AKCIJE_AKCIJE a
        ON a.TIMOVI_ID_tima = t.ID_tima
    WHERE t.ID_tima = ?
    GROUP BY t.ID_tima
    """

    sql_1a_df, sql_1a_t = mjeri_sql(duckdb_conn, _sql, [TIM_ID_1A], n=N_RUNS)
    print(f"SQL gotov: {sql_1a_t*1000:.2f} ms")
    return TIM_ID_1A, sql_1a_df, sql_1a_t


@app.cell
def _(N_RUNS, TIM_ID_1A, conn_kuzu, mjeri_kuzu):
    _cypher = """
    MATCH (t:Tim {id: $id})
    OPTIONAL MATCH (o:Osoba)-[:CLAN_TIMA]->(t)
    OPTIONAL MATCH (t)-[:PROVODI]->(a:Akcija)
    OPTIONAL MATCH (t)-[:ORGANIZIRA]->(e:Edukacija)
    RETURN
        t.id AS ID_tima,
        COUNT(DISTINCT o) AS broj_clanova,
        COUNT(DISTINCT a) AS broj_akcija,
        COUNT(DISTINCT e) AS broj_edukacija
    """

    kuzu_1a_df, kuzu_1a_t = mjeri_kuzu(conn_kuzu, _cypher, {"id": TIM_ID_1A}, n=N_RUNS)
    print(f"Kuzu gotov: {kuzu_1a_t*1000:.2f} ms")
    return kuzu_1a_df, kuzu_1a_t


@app.cell
def _(kuzu_1a_df, kuzu_1a_t, mo, prikazi_usporedbu, sql_1a_df, sql_1a_t):
    prikazi_usporedbu(
        "1.1. Aktivnost tima",
        sql_1a_df, sql_1a_t,
        kuzu_1a_df, kuzu_1a_t,
        mo=mo
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.1. Rezervoar pregled
    """)
    return


@app.cell
def _(N_RUNS, duckdb_conn, mjeri_sql):
    REZERVOAR_ID_1B = 217

    _sql = """
    SELECT
        r.naziv_rezervoara,
        m.naziv_mjesta AS mjesto,
        r.pocetni_broj_vrsta
        + (
            SELECT COUNT(DISTINCT a.POPULACIJE_ID_populacije)
            FROM AKCIJE_AKCIJE a
            WHERE a.REZERVOARI_ID_rezervoara = r.ID_rezervoara
        ) AS trenutni_broj_vrsta,
        (
            SELECT COUNT(*)
            FROM AKCIJE_AKCIJE a
            WHERE a.REZERVOARI_ID_rezervoara = r.ID_rezervoara
        ) AS broj_akcija
    FROM AKCIJE_REZERVOARI r
    JOIN AKCIJE_MJESTA m ON m.ID_mjesta = r.MJESTA_ID_mjesta
    WHERE r.ID_rezervoara = ?
    """

    sql_1b_df, sql_1b_t = mjeri_sql(duckdb_conn, _sql, [REZERVOAR_ID_1B], n=N_RUNS)
    print(f"SQL 1B gotov: {sql_1b_t*1000:.2f} ms")
    return REZERVOAR_ID_1B, sql_1b_df, sql_1b_t


@app.cell
def _(N_RUNS, REZERVOAR_ID_1B, conn_kuzu, mjeri_kuzu):
    _cypher = """
    MATCH (r:Rezervoar {id: $id})
    OPTIONAL MATCH (r)-[:NALAZI_SE_U]->(m:Mjesto)
    OPTIONAL MATCH (a:Akcija)-[:KORISTI_REZERVOAR]->(r)
    OPTIONAL MATCH (a)-[:CILJA]->(p:Populacija)
    WITH r, m,
         COUNT(DISTINCT p) AS br_vrsta_akcija,
         COUNT(DISTINCT a) AS br_akcija
    RETURN
        r.naziv AS naziv_rezervoara,
        m.naziv_mjesta AS mjesto,
        r.pocetni_broj_vrsta + br_vrsta_akcija  AS trenutni_broj_vrsta,
        br_akcija AS broj_akcija
    """

    kuzu_1b_df, kuzu_1b_t = mjeri_kuzu(conn_kuzu, _cypher, {"id": REZERVOAR_ID_1B}, n=N_RUNS)
    print(f"Kuzu gotov: {kuzu_1b_t*1000:.2f} ms")
    return kuzu_1b_df, kuzu_1b_t


@app.cell
def _(kuzu_1b_df, kuzu_1b_t, mo, prikazi_usporedbu, sql_1b_df, sql_1b_t):
    prikazi_usporedbu(
        "Rezervoar pregled",
        sql_1b_df, sql_1b_t,
        kuzu_1b_df, kuzu_1b_t,
        mo=mo
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. STABLASTA STRUKTRA
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.1. Taksonomija
    """)
    return


@app.cell
def _(N_RUNS, duckdb_conn, mjeri_sql):
    POPULACIJA_ID_2 = 1

    _sql = """
    WITH RECURSIVE HijerarhijaCTE AS (
        SELECT
            p.ID_populacije,
            ts.ID_taksonomije_self,
            ts.ime_kategorije,
            ts.TIPOVI_TAKSONOMIJA_ID_tipa,
            ts.TAKSONOMIJA_SELF_predak,
            0 AS dubina
        FROM VRSTE_POPULACIJE p
        JOIN VRSTE_TAKSONOMIJA_SELF ts
            ON ts.ID_taksonomije_self = p.TAKSONOMIJA_SELF_ID_taksonomije_self
        WHERE p.ID_populacije = ?

        UNION ALL

        SELECT
            h.ID_populacije,
            ts_predak.ID_taksonomije_self,
            ts_predak.ime_kategorije,
            ts_predak.TIPOVI_TAKSONOMIJA_ID_tipa,
            ts_predak.TAKSONOMIJA_SELF_predak,
            h.dubina + 1
        FROM HijerarhijaCTE h
        JOIN VRSTE_TAKSONOMIJA_SELF ts_predak
            ON ts_predak.ID_taksonomije_self = h.TAKSONOMIJA_SELF_predak
    )
    SELECT
        h.ID_populacije,
        h.ime_kategorije AS ime_taksonomske_kategorije,
        tip.ime_tipa AS tip_taksonomije,
        h.dubina
    FROM HijerarhijaCTE h
    JOIN VRSTE_TIPOVI_TAKSONOMIJA tip
        ON tip.ID_tipa = h.TIPOVI_TAKSONOMIJA_ID_tipa
    ORDER BY h.dubina
    """

    sql_2_df, sql_2_t = mjeri_sql(duckdb_conn, _sql, [POPULACIJA_ID_2], n=N_RUNS)
    print(f"SQL gotov: {sql_2_t*1000:.2f} ms")
    return POPULACIJA_ID_2, sql_2_df, sql_2_t


@app.cell
def _(N_RUNS, POPULACIJA_ID_2, conn_kuzu, pd, statistics, time):
    _query0 = """
    MATCH (p:Populacija {id: $id})-[:PRIPADA_TAKSONOMIJI]->(tk:TaksonomskaKategorija)
    RETURN
        p.id AS ID_populacije,
        tk.ime AS ime_taksonomske_kategorije,
        tk.ime_tipa AS tip_taksonomije,
        0 AS dubina
    """

    _query1 = """
    MATCH (p:Populacija {id: $id})-[:PRIPADA_TAKSONOMIJI]->(tk:TaksonomskaKategorija)
    MATCH path = (tk)<-[:IMA_PREDKA*1..10]-(predak:TaksonomskaKategorija)
    RETURN
        p.id AS ID_populacije,
        predak.ime AS ime_taksonomske_kategorije,
        predak.ime_tipa AS tip_taksonomije,
        length(path) AS dubina
    ORDER BY dubina
    """

    _vremena = []
    for _ in range(N_RUNS):
        _t0 = time.perf_counter()
        conn_kuzu.execute(_query0, {"id": POPULACIJA_ID_2})
        conn_kuzu.execute(_query1, {"id": POPULACIJA_ID_2})
        _vremena.append(time.perf_counter() - _t0)

    kuzu_2_t = statistics.median(_vremena)

    _df0 = conn_kuzu.execute(_query0, {"id": POPULACIJA_ID_2}).get_as_df()
    _df1 = conn_kuzu.execute(_query1, {"id": POPULACIJA_ID_2}).get_as_df()

    kuzu_2_df = pd.concat([_df0, _df1], ignore_index=True)

    print(f"Kuzu gotov: {kuzu_2_t*1000:.2f} ms")
    return kuzu_2_df, kuzu_2_t


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    veliku razliku braniti s:
    "Ovaj workload u graf bazi je sporiji jer Cypher radi generalizirani graph traversal koji može generirati više putanja, dok relacijski model koristi deterministički parent-pointer join koji prati jedinstvenu strukturu stabla."
    """)
    return


@app.cell
def _(kuzu_2_df, kuzu_2_t, mo, prikazi_usporedbu, sql_2_df, sql_2_t):
    prikazi_usporedbu(
        "Taksonomija populacije",
        sql_2_df, sql_2_t,
        kuzu_2_df, kuzu_2_t,
        mo=mo
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. MANY-TO-MANY VEZE
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3.1. Osobe i uloge u timu
    """)
    return


@app.cell
def _(N_RUNS, duckdb_conn, mjeri_sql):
    TIM_ID_3 = 1

    _sql = """
    SELECT
        t.ID_tima,
        o.ime || ' ' || o.prezime AS ime_prezime,
        u.naziv_uloge AS uloga
    FROM AKCIJE_TIMOVI t
    JOIN AKCIJE_TIMOVI_OSOBE  tio ON tio.TIMOVI_ID_tima = t.ID_tima
    JOIN AKCIJE_OSOBE o  ON o.ID_osobe = tio.OSOBE_ID_osobe
    JOIN AKCIJE_ULOGE u  ON u.ID_uloga = tio.ULOGE_ID_uloga
    WHERE t.ID_tima = ?
    ORDER BY u.naziv_uloge, o.prezime
    """

    sql_3_df, sql_3_t = mjeri_sql(duckdb_conn, _sql, [TIM_ID_3], n=N_RUNS)
    print(f"SQL gotov: {sql_3_t*1000:.2f} ms")
    return TIM_ID_3, sql_3_df, sql_3_t


@app.cell
def _(N_RUNS, TIM_ID_3, conn_kuzu, mjeri_kuzu):
    _cypher = """
    MATCH (o:Osoba)-[r:CLAN_TIMA]->(t:Tim {id: $id})
    RETURN
        t.id AS ID_tima,
        o.ime + ' ' + o.prezime AS ime_prezime,
        r.uloga AS uloga
    ORDER BY r.uloga, o.prezime
    """

    kuzu_3_df, kuzu_3_t = mjeri_kuzu(conn_kuzu, _cypher, {"id": TIM_ID_3}, n=N_RUNS)
    print(f"Kuzu gotov: {kuzu_3_t*1000:.2f} ms")
    return kuzu_3_df, kuzu_3_t


@app.cell
def _(kuzu_3_df, kuzu_3_t, mo, prikazi_usporedbu, sql_3_df, sql_3_t):
    prikazi_usporedbu(
        "Osobe i uloge u timu (M:N)",
        sql_3_df, sql_3_t,
        kuzu_3_df, kuzu_3_t,
        mo=mo
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. FILTERING + ATTRIBUTE QUERY
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.1. Slobodne akcije (nije dodijeljena timu)
    """)
    return


@app.cell
def _(N_RUNS, duckdb_conn, mjeri_sql):
    _sql_base = """
    SELECT
        m.naziv_mjesta AS mjesto,
        ts.ime_kategorije AS populacija,
        st.naziv AS staniste,
        ta.naziv_akcije AS tip_akcije,
        a.datum
    FROM AKCIJE_AKCIJE a
    JOIN VRSTE_POPULACIJE p ON p.ID_populacije = a.POPULACIJE_ID_populacije
    JOIN VRSTE_STANISTA st  ON st.ID_stanista = p.STANISTA_ID_stanista
    JOIN VRSTE_TAKSONOMIJA_SELF ts ON ts.ID_taksonomije_self = p.TAKSONOMIJA_SELF_ID_taksonomije_self
    JOIN AKCIJE_TIPOVI_AKCIJA ta  ON ta.ID_tipa_akcije = a.TIPOVI_AKCIJA_ID_tipa_akcije
    LEFT JOIN AKCIJE_REZERVOARI rez ON rez.ID_rezervoara = a.REZERVOARI_ID_rezervoara
    LEFT JOIN AKCIJE_MJESTA m ON m.ID_mjesta = rez.MJESTA_ID_mjesta
    WHERE a.TIMOVI_ID_tima IS NULL
    """

    sql_4_1_df, sql_4_1_t = mjeri_sql(duckdb_conn, _sql_base, n=N_RUNS)

    sql_4_2_df, sql_4_2_t = mjeri_sql(duckdb_conn,
        _sql_base + " AND ta.naziv_akcije = ?",
        ["Brojanje"], n=N_RUNS
    )

    sql_4_3_df, sql_4_3_t = mjeri_sql(duckdb_conn,
        _sql_base + " AND st.naziv = ?",
        ["Livada Brandon Key"], n=N_RUNS
    )

    print(f"SQL gotov: {sql_4_1_t*1000:.2f} / {sql_4_2_t*1000:.2f} / {sql_4_3_t*1000:.2f} ms")
    return sql_4_1_df, sql_4_1_t, sql_4_2_df, sql_4_2_t, sql_4_3_df, sql_4_3_t


@app.cell
def _(N_RUNS, conn_kuzu, mjeri_kuzu):
    _c1 = """
    MATCH (a:Akcija)-[:CILJA]->(p:Populacija)
    WHERE NOT EXISTS { MATCH (t:Tim)-[:PROVODI]->(a) }
    OPTIONAL MATCH (a)-[:KORISTI_REZERVOAR]->(r:Rezervoar)-[:NALAZI_SE_U]->(m:Mjesto)
    OPTIONAL MATCH (p)-[:ZIVI_U]->(st:Staniste)
    OPTIONAL MATCH (p)-[:PRIPADA_TAKSONOMIJI]->(tk:TaksonomskaKategorija)
    RETURN m.naziv_mjesta AS mjesto, tk.ime AS populacija, st.naziv AS staniste, a.tip_akcije AS tip_akcije, a.datum AS datum
    """
    kuzu_4_1_df, kuzu_4_1_t = mjeri_kuzu(conn_kuzu, _c1, n=N_RUNS)

    _c2 = """
    MATCH (a:Akcija)-[:CILJA]->(p:Populacija)
    WHERE NOT EXISTS { MATCH (t:Tim)-[:PROVODI]->(a) }
      AND a.tip_akcije = $tip
    OPTIONAL MATCH (a)-[:KORISTI_REZERVOAR]->(r:Rezervoar)-[:NALAZI_SE_U]->(m:Mjesto)
    OPTIONAL MATCH (p)-[:ZIVI_U]->(st:Staniste)
    OPTIONAL MATCH (p)-[:PRIPADA_TAKSONOMIJI]->(tk:TaksonomskaKategorija)
    RETURN m.naziv_mjesta AS mjesto, tk.ime AS populacija, st.naziv AS staniste, a.tip_akcije AS tip_akcije, a.datum AS datum
    """
    kuzu_4_2_df, kuzu_4_2_t = mjeri_kuzu(conn_kuzu, _c2, {"tip": "Brojanje"}, n=N_RUNS)

    _c3 = """
    MATCH (a:Akcija)-[:CILJA]->(p:Populacija)-[:ZIVI_U]->(st:Staniste)
    WHERE NOT EXISTS { MATCH (t:Tim)-[:PROVODI]->(a) }
      AND st.naziv = $staniste
    OPTIONAL MATCH (a)-[:KORISTI_REZERVOAR]->(r:Rezervoar)-[:NALAZI_SE_U]->(m:Mjesto)
    OPTIONAL MATCH (p)-[:PRIPADA_TAKSONOMIJI]->(tk:TaksonomskaKategorija)
    RETURN m.naziv_mjesta AS mjesto, tk.ime AS populacija, st.naziv AS staniste, a.tip_akcije AS tip_akcije, a.datum AS datum
    """
    kuzu_4_3_df, kuzu_4_3_t = mjeri_kuzu(conn_kuzu, _c3, {"staniste": "Livada Brandon Key"}, n=N_RUNS)

    print(f"Kuzu gotov: {kuzu_4_1_t*1000:.2f} / {kuzu_4_2_t*1000:.2f} / {kuzu_4_3_t*1000:.2f} ms")
    return (
        kuzu_4_1_df,
        kuzu_4_1_t,
        kuzu_4_2_df,
        kuzu_4_2_t,
        kuzu_4_3_df,
        kuzu_4_3_t,
    )


@app.cell
def _(
    kuzu_4_1_df,
    kuzu_4_1_t,
    kuzu_4_2_df,
    kuzu_4_2_t,
    kuzu_4_3_df,
    kuzu_4_3_t,
    mo,
    prikazi_usporedbu,
    sql_4_1_df,
    sql_4_1_t,
    sql_4_2_df,
    sql_4_2_t,
    sql_4_3_df,
    sql_4_3_t,
):
    mo.vstack([
        prikazi_usporedbu("Slobodne akcije (bez filtera)",
            sql_4_1_df, sql_4_1_t, kuzu_4_1_df, kuzu_4_1_t, mo=mo),
        prikazi_usporedbu("Slobodne akcije (tip = Brojanje)",
            sql_4_2_df, sql_4_2_t, kuzu_4_2_df, kuzu_4_2_t, mo=mo),
        prikazi_usporedbu("Slobodne akcije (stanište = Livada Brandon Key)",
            sql_4_3_df, sql_4_3_t, kuzu_4_3_df, kuzu_4_3_t, mo=mo),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. KONTEKSTUALNA AGREGACIJA
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.1. Rezervoar + predator odnosi
    """)
    return


@app.cell
def _(N_RUNS, duckdb_conn, mjeri_sql):
    REZERVOAR_ID_5 = 1
    POPULACIJA_ID_5 = 1

    _sql = """
    SELECT
        r.naziv_rezervoara,
        r.pocetni_broj_vrsta
        + (
            SELECT COUNT(DISTINCT a_inner.POPULACIJE_ID_populacije)
            FROM AKCIJE_AKCIJE a_inner
            WHERE a_inner.REZERVOARI_ID_rezervoara = r.ID_rezervoara
        ) AS ukupni_broj_vrsta,
        r.povrsina,
        (
            SELECT COUNT(DISTINCT m.POPULACIJE_ID_populacije1)
            FROM VRSTE_MEDUODNOSI m
            JOIN VRSTE_INTERAKCIJE i
                ON i.ID_interakcije = m.INTERAKCIJE_ID_interakcije
            WHERE m.POPULACIJE_ID_populacije2 = ?
              AND i.interakcija = 'Predacija'
              AND EXISTS (
                  SELECT 1
                  FROM AKCIJE_AKCIJE a2
                  WHERE a2.POPULACIJE_ID_populacije  = m.POPULACIJE_ID_populacije1
                    AND a2.REZERVOARI_ID_rezervoara  = r.ID_rezervoara
              )
        ) AS broj_predatora_u_rezervoaru,
        s.naziv AS staniste_populacije
    FROM AKCIJE_REZERVOARI r
    JOIN VRSTE_POPULACIJE p
        ON p.ID_populacije = ?
    JOIN VRSTE_STANISTA s
        ON s.ID_stanista = p.STANISTA_ID_stanista
    WHERE r.ID_rezervoara = ?
    """

    sql_5_df, sql_5_t = mjeri_sql(
        duckdb_conn, _sql,
        [POPULACIJA_ID_5, POPULACIJA_ID_5, REZERVOAR_ID_5], n=N_RUNS
    )
    print(f"SQL gotov: {sql_5_t*1000:.2f} ms")
    return POPULACIJA_ID_5, REZERVOAR_ID_5, sql_5_df, sql_5_t


@app.cell
def _(N_RUNS, POPULACIJA_ID_5, REZERVOAR_ID_5, conn_kuzu, mjeri_kuzu):
    _cypher = """
    MATCH (r:Rezervoar {id: $rez_id})
    MATCH (p:Populacija {id: $pop_id})-[:ZIVI_U]->(st:Staniste)

    OPTIONAL MATCH (a_vrsta:Akcija)-[:KORISTI_REZERVOAR]->(r)
    OPTIONAL MATCH (a_vrsta)-[:CILJA]->(p_vrsta:Populacija)
    WITH r, p, st,
         r.pocetni_broj_vrsta AS pocetni,
         COUNT(DISTINCT p_vrsta) AS br_vrsta_akcija

    OPTIONAL MATCH (pred:Populacija)-[inter:INTERAGIRA]->(p)
    WHERE inter.tip = 'Predacija'
    OPTIONAL MATCH (a_pred:Akcija)-[:CILJA]->(pred)
    OPTIONAL MATCH (a_pred)-[:KORISTI_REZERVOAR]->(r2:Rezervoar)
    WHERE r2.id = r.id
    WITH r, p, st, pocetni, br_vrsta_akcija,
         CASE WHEN r2 IS NOT NULL THEN pred ELSE NULL END AS pred_u_rez

    RETURN
        r.naziv AS naziv_rezervoara,
        pocetni + br_vrsta_akcija AS ukupni_broj_vrsta,
        r.povrsina AS povrsina,
        COUNT(DISTINCT pred_u_rez) AS broj_predatora_u_rezervoaru,
        st.naziv AS staniste_populacije
    """

    kuzu_5_df, kuzu_5_t = mjeri_kuzu(
        conn_kuzu, _cypher,
        {"rez_id": REZERVOAR_ID_5, "pop_id": POPULACIJA_ID_5}, n=N_RUNS
    )
    print(f"Kuzu gotov: {kuzu_5_t*1000:.2f} ms")
    return kuzu_5_df, kuzu_5_t


@app.cell
def _(kuzu_5_df, kuzu_5_t, mo, prikazi_usporedbu, sql_5_df, sql_5_t):
    prikazi_usporedbu(
        "Rezervoar + predator odnosi (kontekstualna agregacija)",
        sql_5_df, sql_5_t,
        kuzu_5_df, kuzu_5_t,
        mo=mo
    )
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
