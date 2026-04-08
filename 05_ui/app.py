# 05_ui/app.py

"""
Pirmas Streamlit UI prototipas baigiamajam darbui.

Ką šis failas daro:
1. Suranda SQLite DB failus projekte
2. Leidžia pasirinkti norimą DB
3. Nuskaito visas DB lenteles
4. Leidžia pasirinkti lentelę
5. Leidžia ieškoti įrašo pagal SKLYPO_ID
6. Parodo pagrindinius automatinės analizės laukus

Šis variantas yra sąmoningai parašytas paprastai ir aiškiai,
kad būtų lengva plėsti vėliau.
"""

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st


# ============================================================
# 1. BENDRI NUSTATYMAI
# ============================================================

# Čia nusistatome pagrindinį projekto katalogą.
# Kadangi failas bus 05_ui/app.py,
# tai projekto šaknis bus vienu lygiu aukščiau.
PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]
DB_FAILO_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"
PAGRINDINE_LENTELE = "sklypu_analizes"
PAGRINDINIS_ID_STULPELIS = "sklypo_id"

# Kokius laukus pirmoje UI versijoje norime rodyti vartotojui.
# Jei kai kurių laukų tavo lentelėje dar nėra,
# programa tiesiog jų nerodys.
NORIMI_RODYTI_LAUKAI = [
    "sklypo_id",
    "adresas",
    "pagrindine_zona_pavadinimas",
    "automatines_analizes_rezultatas",
    "automatines_analizes_paaiskinimas",
    "ukininko_sodybos_statusas",
    "ukininko_sodybos_salygos",
    "rankines_validacijos_statusas",
]

# Galimi ID stulpelio pavadinimai.
# Jei tavo DB stulpelis vadinasi kitaip, vėliau lengvai papildysime.
GALIMI_ID_STULPELIAI = [
    "sklypo_id",
    "SKLYPO_ID",
    "id",
    "sklypas_id",
]


# ============================================================
# 2. PAGALBINĖS FUNKCIJOS
# ============================================================

def rasti_db_failus(projekto_katalogas: Path) -> list[Path]:
    """
    Suranda visus .db failus projekte.

    Ieškome:
    - projekto šaknyje
    - 03_db aplanke
    - ir apskritai visame projekte
    """
    rasti_failai = set()

    # Dažniausios vietos
    daznos_vietos = [
        projekto_katalogas,
        projekto_katalogas / "03_db",
    ]

    for vieta in daznos_vietos:
        if vieta.exists():
            for failas in vieta.glob("*.db"):
                rasti_failai.add(failas.resolve())

    # Jei DB guli kur nors giliau projekte
    for failas in projekto_katalogas.rglob("*.db"):
        rasti_failai.add(failas.resolve())

    # Grąžiname surūšiuotą sąrašą
    return sorted(rasti_failai)


def gauti_prisijungima(db_kelias: str) -> sqlite3.Connection:
    """
    Sukuria prisijungimą prie SQLite DB.
    """
    return sqlite3.connect(db_kelias, check_same_thread=False)


def gauti_lenteles(conn: sqlite3.Connection) -> list[str]:
    """
    Nuskaito visas vartotojo lenteles iš SQLite DB.
    """
    uzklausa = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """
    df = pd.read_sql_query(uzklausa, conn)
    return df["name"].tolist()


def gauti_stulpelius(conn: sqlite3.Connection, lenteles_pavadinimas: str) -> list[str]:
    """
    Nuskaito konkrečios lentelės stulpelių pavadinimus.
    """
    uzklausa = f"PRAGMA table_info({lenteles_pavadinimas})"
    df = pd.read_sql_query(uzklausa, conn)
    return df["name"].tolist()


def rasti_id_stulpeli(stulpeliai: list[str]) -> str | None:
    """
    Bando automatiškai rasti ID stulpelį.
    """
    for galimas in GALIMI_ID_STULPELIAI:
        if galimas in stulpeliai:
            return galimas
    return None


def ieskoti_pagal_sklypo_id(
    conn: sqlite3.Connection,
    lenteles_pavadinimas: str,
    id_stulpelis: str,
    sklypo_id_reiksme: str
) -> pd.DataFrame:
    """
    Suranda įrašą pagal pasirinktą ID stulpelį.
    """
    uzklausa = f"""
        SELECT *
        FROM {lenteles_pavadinimas}
        WHERE {id_stulpelis} = ?
    """
    df = pd.read_sql_query(uzklausa, conn, params=(sklypo_id_reiksme,))
    return df


def paruosti_suvestines_laukus(df: pd.DataFrame) -> dict:
    """
    Iš pirmos rastos eilutės paima tik norimus rodyti laukus.
    Jei lauko nėra lentelėje, jis tiesiog praleidžiamas.
    """
    if df.empty:
        return {}

    eilute = df.iloc[0]
    rezultatas = {}

    for laukas in NORIMI_RODYTI_LAUKAI:
        if laukas in df.columns:
            reikšmė = eilute[laukas]
            rezultatas[laukas] = reikšmė

    return rezultatas


def graziai_pavadinti_lauka(lauko_vardas: str) -> str:
    """
    Techninį DB lauko pavadinimą paverčia gražiu lietuvišku pavadinimu UI lange.
    """

    lauku_pavadinimu_zodynas = {
        "sklypo_id": "Sklypo ID",
        "adresas": "Adresas",
        "pagrindine_zona_pavadinimas": "Pagrindinė zona pavadinimas",
        "automatines_analizes_rezultatas": "Automatinės analizės rezultatas",
        "automatines_analizes_paaiskinimas": "Automatinės analizės paaiškinimas",
        "ukininko_sodybos_statusas": "Ūkininko sodybos statusas",
        "ukininko_sodybos_salygos": "Ūkininko sodybos sąlygos",
        "rankines_validacijos_statusas": "Rankinės validacijos statusas",
    }

    if lauko_vardas in lauku_pavadinimu_zodynas:
        return lauku_pavadinimu_zodynas[lauko_vardas]

    tekstas = lauko_vardas.replace("_", " ").strip()
    return tekstas[:1].upper() + tekstas[1:]


def sutvarkyti_lietuviskus_rasmenis(tekstas: str) -> str:
    """
    Bando sutvarkyti neteisingai atvaizduotus lietuviškus simbolius,
    kai tekstas DB atrodo pvz. 'KlaipÓdos' vietoj 'Klaipėdos'.
    """
    try:
        return tekstas.encode("latin1").decode("cp775")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return tekstas


def rodyti_reiksme(reiksme):
    """
    Vienodas reikšmių atvaizdavimas.
    """
    if pd.isna(reiksme):
        return "—"

    tekstas = str(reiksme).strip()

    if tekstas == "":
        return "—"

    return sutvarkyti_lietuviskus_rasmenis(tekstas)


# ============================================================
# 3. STREAMLIT PUSLAPIO NUSTATYMAI
# ============================================================

st.set_page_config(
    page_title="Sklypo analizės sistema",
    page_icon="🏡",
    layout="wide",
)

st.title("🏡 Automatinė sklypo statybos galimybių analizės sistema")
st.caption("Pirma UI prototipo versija su Streamlit ir SQLite DB")

st.markdown(
    """
    Ši versija skirta parodyti, kad sistema:
    - turi ne terminalinę sąsają,
    - dirba su duomenų baze,
    - leidžia surasti sklypą pagal `SKLYPO_ID`,
    - parodo automatinės analizės rezultatą.
    """
)


# ============================================================
# 4. FIKSUOTI DB NUSTATYMAI
# ============================================================

st.sidebar.header("DB nustatymai")

pasirinktas_db = DB_FAILO_KELIAS
pasirinkta_lentele = PAGRINDINE_LENTELE
id_stulpelis = PAGRINDINIS_ID_STULPELIS

if not pasirinktas_db.exists():
    st.error(f"DB failas nerastas: {pasirinktas_db}")
    st.stop()


# ============================================================
# 5. PRISIJUNGIMAS PRIE DB
# ============================================================

try:
    conn = gauti_prisijungima(str(pasirinktas_db))
except Exception as klaida:
    st.error(f"Nepavyko prisijungti prie DB: {klaida}")
    st.stop()

try:
    lenteles = gauti_lenteles(conn)
except Exception as klaida:
    st.error(f"Nepavyko nuskaityti lentelių: {klaida}")
    st.stop()

if pasirinkta_lentele not in lenteles:
    st.error(f"Lentelė '{pasirinkta_lentele}' DB faile nerasta.")
    st.stop()

try:
    lenteles_stulpeliai = gauti_stulpelius(conn, pasirinkta_lentele)
except Exception as klaida:
    st.error(f"Nepavyko nuskaityti lentelės stulpelių: {klaida}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.write("**Naudojamas DB failas:**")
st.sidebar.code(str(pasirinktas_db), language="text")

st.sidebar.write("**Naudojama lentelė:**")
st.sidebar.code(pasirinkta_lentele, language="text")

st.sidebar.write("**Paieškos laukas:**")
st.sidebar.code(id_stulpelis, language="text")


# ============================================================
# 6. PAGRINDINIS PAIEŠKOS BLOKAS
# ============================================================

st.subheader("1. Sklypo paieška")

kairys, desinys = st.columns([2, 1])

with kairys:
    ivestas_sklypo_id = st.text_input(
        "Įvesk SKLYPO_ID reikšmę",
        placeholder="Pvz. 12345",
    )

with desinys:
    ieskoti_paspausta = st.button("Ieškoti", use_container_width=True)

# Kad būtų patogiau: jei vartotojas ką nors įvedė, bet dar nepaspaudė,
# galima rodyti priminimą.
if ivestas_sklypo_id and not ieskoti_paspausta:
    st.info("Paspausk „Ieškoti“, kad būtų parodytas rezultatas.")


# ============================================================
# 7. PAIEŠKOS REZULTATAS
# ============================================================

if ieskoti_paspausta:
    if not ivestas_sklypo_id.strip():
        st.warning("Pirmiausia įvesk SKLYPO_ID reikšmę.")
        st.stop()

    try:
        rezultato_df = ieskoti_pagal_sklypo_id(
            conn=conn,
            lenteles_pavadinimas=pasirinkta_lentele,
            id_stulpelis=id_stulpelis,
            sklypo_id_reiksme=ivestas_sklypo_id.strip(),
        )
    except Exception as klaida:
        st.error(f"Paieškos metu įvyko klaida: {klaida}")
        st.stop()

    st.subheader("2. Automatinės analizės rezultatas")

    if rezultato_df.empty:
        st.warning("Pagal įvestą SKLYPO_ID įrašas nerastas.")
    else:
        if len(rezultato_df) > 1:
            st.warning(
                f"Rasti {len(rezultato_df)} įrašai pagal tą patį ID. "
                "Žemiau rodoma pirmoji rasta eilutė."
            )

        suvestine = paruosti_suvestines_laukus(rezultato_df)

        if suvestine:
            st.markdown("### Sklypo suvestinė")

            # Rodymui per du stulpelius
            rodomi_laukai = list(suvestine.items())
            puse = (len(rodomi_laukai) + 1) // 2

            kaire_lentele = rodomi_laukai[:puse]
            desine_lentele = rodomi_laukai[puse:]

            col1, col2 = st.columns(2)

            with col1:
                for laukas, reiksme in kaire_lentele:
                    st.markdown(f"**{graziai_pavadinti_lauka(laukas)}:** {rodyti_reiksme(reiksme)}")

            with col2:
                for laukas, reiksme in desine_lentele:
                    st.markdown(f"**{graziai_pavadinti_lauka(laukas)}:** {rodyti_reiksme(reiksme)}")
        else:
            st.info(
                "Įrašas rastas, bet nei vieno iš numatytų rodomų laukų šioje lentelėje nėra. "
                "Apačioje gali peržiūrėti visą eilutę."
            )

        st.markdown("---")

        # Papildomas blokas, kad aiškiai matytųsi, jog tai preliminari analizė
        if "automatines_analizes_rezultatas" in rezultato_df.columns:
            automatine_isvada = rezultato_df.iloc[0]["automatines_analizes_rezultatas"]
        else:
            automatine_isvada = "—"

        st.markdown("### Preliminari sistemos išvada")
        st.info(
            f"**Automatinės analizės rezultatas:** {rodyti_reiksme(automatine_isvada)}\n\n"
            "Šis rezultatas laikomas preliminariu ir turi būti patvirtintas specialisto validacijos etape."
        )

        # Ūkininko sodybos blokas
        if (
            "ukininko_sodybos_statusas" in rezultato_df.columns
            or "ukininko_sodybos_salygos" in rezultato_df.columns
        ):
            st.markdown("### Ūkininko sodybos scenarijus")

            uk_statusas = (
                rezultato_df.iloc[0]["ukininko_sodybos_statusas"]
                if "ukininko_sodybos_statusas" in rezultato_df.columns
                else None
            )

            uk_salygos = (
                rezultato_df.iloc[0]["ukininko_sodybos_salygos"]
                if "ukininko_sodybos_salygos" in rezultato_df.columns
                else None
            )

            st.write(f"**Statusas:** {rodyti_reiksme(uk_statusas)}")
            st.write(f"**Sąlygos:** {rodyti_reiksme(uk_salygos)}")

        # Visas žalias DB įrašas – labai naudinga derinimui
        with st.expander("Rodyti visą rastą DB įrašą"):
            st.dataframe(rezultato_df, use_container_width=True)

        # Stulpelių sąrašas – naudinga tikrinant, kas DB jau yra
        with st.expander("Rodyti lentelės stulpelius"):
            st.write(lenteles_stulpeliai)


# ============================================================
# 8. APAČIOS INFORMACIJA
# ============================================================

st.markdown("---")
st.caption(
    "Pirmas prototipas: paieška pagal SKLYPO_ID, duomenų nuskaitymas iš SQLite, "
    "preliminarios automatinės analizės rodymas."
)