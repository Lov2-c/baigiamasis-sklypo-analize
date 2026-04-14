from io import BytesIO
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Table,
    TableStyle,
    Image,
)

from ui_helpers import sutvarkyti_lietuviskus_rasmenis
from ui_layer_texts import SLUOKSNIU_TEKSTAI


# =========================================================
# 1. Kodų paaiškinimai
# =========================================================

PASKIRTIES_TIPU_REIKSMES = {
    "610": "žemės ūkio paskirties žemė",
    "710": "miškų ūkio paskirties žemė",
    "995": "kitos paskirties žemė",
}

PASKIRTIES_TIPU_PAAISKINIMAI = {
    "610": (
        "Šiuo metu sklypas registruotas kaip žemės ūkio paskirties žemė. "
        "Tokios paskirties žemė pirmiausia skirta žemės ūkio veiklai, todėl įprasta gyvenamoji ar kita "
        "intensyvesnė statyba joje paprastai nelaikoma tiesiogiai savaime galima. Praktikoje tokioje žemėje "
        "gali būti aktualūs žemės ūkiui skirti statiniai, o kai kuriais atvejais – ir ūkininko sodybos "
        "scenarijus ar kiti specialūs sprendiniai, tačiau galutinės galimybės priklauso nuo konkretaus "
        "naudojimo būdo, sklypo ploto, bendrojo plano sprendinių ir papildomų ribojimų."
    ),
    "710": (
        "Šiuo metu sklypas registruotas kaip miškų ūkio paskirties žemė. "
        "Tokios paskirties žemė pirmiausia skirta miško išsaugojimui, tvarkymui ir naudojimui pagal miškų ūkio "
        "reikalavimus. Įprasta nauja gyvenamoji ar kita intensyvi statyba tokioje žemėje paprastai nėra laikoma "
        "pagrindine ir tiesiogiai numatoma kryptimi. Praktikoje gali būti aktualūs tik su miškų ūkiu, miško "
        "priežiūra ar kita specialia paskirtimi susiję sprendiniai, o galutinės galimybės priklauso nuo konkrečių "
        "teisinių reikalavimų ir papildomų ribojimų."
    ),
    "995": (
        "Šiuo metu sklypas registruotas kaip kitos paskirties žemė. "
        "Tai reiškia, kad galimų statinių pobūdis paprastai priklauso ne vien nuo bendro paskirties kodo, bet ir "
        "nuo konkretaus žemės naudojimo būdo, bendrojo plano funkcinės zonos bei kitų taikomų ribojimų. Tokiuose "
        "sklypuose gali būti aktuali gyvenamoji, paslaugų, komercinė, visuomeninė, inžinerinė ar kita statyba, "
        "tačiau galutiniai sprendiniai turi būti vertinami pagal konkretų teritorijos planavimo kontekstą."
    ),
}

PAGRINDINES_PASKIRTIES_REIKSMES = {
    "KT": "kita",
    "ZU": "žemės ūkio",
    "M": "miškų ūkio",
    "V": "vandens ūkio",
    "K": "konservacinė",
    "Z;KT": "žemės ūkio / kita",
}

PAGRINDINES_PASKIRTIES_PAAISKINIMAI = {
    "KT": (
        "Pagal bendrojo plano sprendinius teritorija orientuojama į kitos paskirties žemę. "
        "Tai nereiškia vieno universalaus statinių tipo: konkretūs galimi sprendiniai priklauso nuo funkcinės zonos. "
        "Jei teritorija patenka į gyvenamąją zoną, joje gali būti aktuali gyvenamoji statyba; jei į pramonės ir "
        "sandėliavimo zoną – gamybiniai, sandėliavimo ar logistikos pastatai; jei į specializuotų kompleksų zoną – "
        "specializuotos paskirties statiniai; jei į bendro naudojimo erdvių zoną – viešosios erdvės, želdynai ir su "
        "jais susiję sprendiniai. Taigi ši reikšmė rodo ne vien dabartinę būseną, o planavimo kryptį, pagal kurią "
        "teritorijoje galėtų būti vystoma kitos paskirties veikla."
    ),
    "ZU": (
        "Pagal bendrojo plano sprendinius teritorija orientuojama į žemės ūkio paskirtį. "
        "Tokiose teritorijose pagrindinė kryptis paprastai siejama su žemės ūkio veikla, todėl įprasta nauja "
        "gyvenamoji ar kita intensyvi statyba paprastai nėra laikoma pagrindine vystymo kryptimi. Praktikoje gali "
        "būti aktualūs žemės ūkio veiklai reikalingi statiniai, o tam tikrais atvejais – ir ūkininko sodybos ar "
        "kiti specialūs sprendiniai, tačiau tai priklauso nuo papildomų sąlygų."
    ),
    "M": (
        "Pagal bendrojo plano sprendinius teritorija orientuojama į miškų ūkio paskirtį. "
        "Tokiose teritorijose prioritetas teikiamas miško išsaugojimui, tvarkymui ir naudojimui pagal miškų ūkio "
        "principus, todėl įprasta nauja gyvenamoji ar kita intensyvi plėtra čia paprastai nėra numatoma. Praktikoje "
        "galimi tik tie sprendiniai, kurie suderinami su miškų ūkio, aplinkosaugos ir kitais taikomais reikalavimais."
    ),
    "V": (
        "Pagal bendrojo plano sprendinius teritorija orientuojama į vandens ūkio paskirtį. "
        "Tokiose teritorijose pagrindinė kryptis siejama su vandens telkiniais, jų apsauga ir priežiūra, todėl "
        "įprasta nauja gyvenamoji ar kita intensyvi statyba paprastai nėra laikoma pagrindine vystymo kryptimi."
    ),
    "K": (
        "Pagal bendrojo plano sprendinius teritorija orientuojama į konservacinę paskirtį. "
        "Tai reiškia, kad prioritetas teikiamas saugomų vertybių išsaugojimui, todėl naujos statybos ar intensyvaus "
        "vystymo galimybės tokiose teritorijose paprastai būna labai stipriai ribotos."
    ),
    "Z;KT": (
        "Pagal bendrojo plano sprendinius teritorijoje matoma mišri žemės ūkio ir kitos paskirties kryptis. "
        "Tai reiškia, kad vien teritorijos vertinimas pagal dabartinę paskirtį nėra pakankamas: galutinė vystymo "
        "kryptis priklauso nuo konkrečios funkcinės zonos, jos reglamentų ir kitų taikomų ribojimų. Praktikoje dalyje "
        "tokios teritorijos gali išlikti žemės ūkio pobūdžio naudojimas, o kitur gali būti aktualūs kitos paskirties "
        "sprendiniai, tačiau tai turi būti vertinama kartu su BP zonos turiniu."
    ),
}

PDF_ZEMELAPIO_SPALVOS = {
    "draustiniai": "#d73027",
    "rezervatai": "#7f0000",
    "parkai": "#ff7f00",
    "biosferos_poligonai": "#fdbf6f",
    "bast": "#33a02c",
    "past": "#b2df8a",
    "pajurio_juosta": "#1f78b4",
    "buferines_apsaugos_zonos": "#6a3d9a",
    "miskas": "#006400",
    "kvr_poligonai": "#8b4513",
    "kvr_apsaugos_zonos": "#ff1493",
    "pelkes": "#00bcd4",
    "saltinynai": "#00ffff",
    "pievos_ganyklos": "#ffd54f",
    "drenazo_plotai": "#795548",
    "rinktuvu_apsaugos_zonos": "#e64a19",
    "gelezinkelio_ribojimo_zonos": "#000000",
}


# =========================================================
# 2. Šriftai lietuviškoms raidėms
# =========================================================

def _registruoti_sriftus():
    galimi_reguliarus = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),
    ]

    galimi_bold = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf"),
        Path("C:/Windows/Fonts/DejaVuSans-Bold.ttf"),
    ]

    reguliarus = next((p for p in galimi_reguliarus if p.exists()), None)
    bold = next((p for p in galimi_bold if p.exists()), None)

    if reguliarus is None or bold is None:
        raise FileNotFoundError(
            "Nepavyko rasti TrueType šriftų PDF generavimui. "
            "Patikrink, ar sistemoje yra Arial / Calibri / DejaVuSans."
        )

    try:
        pdfmetrics.getFont("PDFRegular")
    except Exception:
        pdfmetrics.registerFont(TTFont("PDFRegular", str(reguliarus)))

    try:
        pdfmetrics.getFont("PDFBold")
    except Exception:
        pdfmetrics.registerFont(TTFont("PDFBold", str(bold)))


# =========================================================
# 3. Formatavimo funkcijos
# =========================================================

def _tekstas(reiksme, tuscia="—") -> str:
    if reiksme is None:
        return tuscia

    tekstas = str(reiksme).strip()
    if tekstas == "" or tekstas.lower() in {"nan", "none"}:
        return tuscia

    return sutvarkyti_lietuviskus_rasmenis(tekstas)


def _ha_tiksliai(reiksme, tuscia="—") -> str:
    if reiksme is None:
        return tuscia
    try:
        return f"{float(reiksme):.4f}"
    except Exception:
        return _tekstas(reiksme, tuscia=tuscia)


def _m2_be_kablelio(reiksme, tuscia="—") -> str:
    if reiksme is None:
        return tuscia
    try:
        return f"{round(float(reiksme))}"
    except Exception:
        return _tekstas(reiksme, tuscia=tuscia)


def _proc_du_skaitmenys(reiksme, tuscia="—") -> str:
    if reiksme is None:
        return tuscia
    try:
        return f"{float(reiksme):.2f}"
    except Exception:
        return _tekstas(reiksme, tuscia=tuscia)


def _suformuoti_paskirties_tipa(kodas) -> str:
    kodas_txt = _tekstas(kodas)
    paaiskinimas = PASKIRTIES_TIPU_REIKSMES.get(kodas_txt)
    if paaiskinimas:
        return f"{kodas_txt} – {paaiskinimas}"
    return kodas_txt


def _suformuoti_pagrindine_paskirti(kodas) -> str:
    kodas_txt = _tekstas(kodas)
    paaiskinimas = PAGRINDINES_PASKIRTIES_REIKSMES.get(kodas_txt)
    if paaiskinimas:
        return f"{kodas_txt} – {paaiskinimas}"
    return kodas_txt

def _gauti_dabartines_paskirties_paaiskinima(kodas) -> str:
    kodas_txt = _tekstas(kodas, "")
    tekstas = PASKIRTIES_TIPU_PAAISKINIMAI.get(kodas_txt)
    if tekstas:
        return _tekstas(tekstas)

    return (
        "Dabartinės pagrindinės žemės naudojimo paskirties paaiškinimas šiam kodui dar nėra parengtas. "
        "Todėl galimos statybos ir naudojimo kryptys turi būti vertinamos pagal konkretų naudojimo būdą, "
        "bendrojo plano sprendinius ir kitus taikomus ribojimus."
    )


def _gauti_bp_paskirties_paaiskinima(kodas) -> str:
    kodas_txt = _tekstas(kodas, "")
    tekstas = PAGRINDINES_PASKIRTIES_PAAISKINIMAI.get(kodas_txt)
    if tekstas:
        return _tekstas(tekstas)

    return (
        "Bendrojo plano pagrindinės paskirties paaiškinimas šiai reikšmei dar nėra atskirai parengtas. "
        "Todėl teritorijos planavimo kryptis turi būti vertinama kartu su konkrečios funkcinės zonos turiniu "
        "ir kitais taikomais teritorijos reglamentais."
    )

def _ml_paaiskinimas(ml_klase: str | None) -> str:
    ml_klase = _tekstas(ml_klase, "").strip()

    if ml_klase == "vystymas_tiesiogiai_galimas":
        return "Vystymas preliminariai laikomas tiesiogiai galimu."
    if ml_klase == "vystymas_galimas_su_salygomis":
        return "Vystymas galimas, tačiau reikia atsižvelgti į papildomas sąlygas ir ribojimus parenkant sprendinius bei statinio vietą."
    if ml_klase == "vystymas_labai_apribotas":
        return "Vystymas preliminariai laikomas labai apribotu."
    return "ML prognozė dar nesuformuota."


def uzpildyti_ploto_sablona(tekstas: str, plotas_m2, procentas) -> str:
    tekstas = tekstas.replace("[X m²]", f"{_m2_be_kablelio(plotas_m2)} m²")
    tekstas = tekstas.replace("[Y %]", f"{_proc_du_skaitmenys(procentas)} %")
    return tekstas


# =========================================================
# 4. Ribojimų tekstai
# =========================================================

def gauti_ataskaitini_sluoksnio_teksta(
    sluoksnis: dict,
    visi_sluoksniai: list[dict] | None = None,
) -> str:
    kodas = sluoksnis.get("kodas")
    plotas_m2 = sluoksnis.get("plotas_m2")
    procentas = sluoksnis.get("procentas")

    tekstu_blokas = SLUOKSNIU_TEKSTAI.get(kodas, {})

    if kodas == "drenazo_plotai" and visi_sluoksniai:
        yra_rinktuvu_zona = any(
            s.get("kodas") == "rinktuvu_apsaugos_zonos" for s in visi_sluoksniai
        )
        if not yra_rinktuvu_zona and "be_zonos_ataskaitai" in SLUOKSNIU_TEKSTAI.get("rinktuvu_apsaugos_zonos", {}):
            tekstas = SLUOKSNIU_TEKSTAI["rinktuvu_apsaugos_zonos"]["be_zonos_ataskaitai"]
            return _tekstas(uzpildyti_ploto_sablona(tekstas, plotas_m2, procentas))

    tekstas = (
        tekstu_blokas.get("ataskaitai")
        or sluoksnis.get("ataskaitos_tekstas")
        or sluoksnis.get("trumpas_aprasymas")
        or ""
    )

    if tekstas:
        tekstas = uzpildyti_ploto_sablona(tekstas, plotas_m2, procentas)

    return _tekstas(tekstas)


# =========================================================
# 5. GeoJSON -> GeoDataFrame
# =========================================================

def _geojson_i_gdf(geojson_obj: dict) -> gpd.GeoDataFrame | None:
    if not geojson_obj:
        return None

    features = geojson_obj.get("features", [])
    if not features:
        return None

    gdf = gpd.GeoDataFrame.from_features(features)
    if gdf.empty:
        return None

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    return gdf


# =========================================================
# 6. Žemėlapio paveikslas PDF ataskaitai
# =========================================================

def generuoti_automatines_analizes_zemelapio_png(
    sklypo_geojson: dict | None,
    automatiniai_sluoksniai: list[dict] | None,
) -> BytesIO | None:
    if not sklypo_geojson:
        return None

    sklypo_gdf = _geojson_i_gdf(sklypo_geojson)
    if sklypo_gdf is None or sklypo_gdf.empty:
        return None

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    ax.set_axis_off()

    if automatiniai_sluoksniai:
        for sluoksnis in automatiniai_sluoksniai:
            geojson = sluoksnis.get("geojson")
            sluoksnio_gdf = _geojson_i_gdf(geojson)

            if sluoksnio_gdf is None or sluoksnio_gdf.empty:
                continue

            spalva = PDF_ZEMELAPIO_SPALVOS.get(
                sluoksnis.get("kodas"),
                sluoksnis.get("spalva", "#4f81bd"),
            )

            sluoksnio_gdf.plot(
                ax=ax,
                color=spalva,
                edgecolor=spalva,
                alpha=0.50,
                linewidth=1.0,
                zorder=5,
            )

    sklypo_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="#111111",
        linewidth=3.0,
        zorder=20,
    )

    minx, miny, maxx, maxy = sklypo_gdf.total_bounds
    dx = (maxx - minx) * 0.18 if (maxx - minx) > 0 else 0.001
    dy = (maxy - miny) * 0.18 if (maxy - miny) > 0 else 0.001

    ax.set_xlim(minx - dx, maxx + dx)
    ax.set_ylim(miny - dy, maxy + dy)

    ax.set_title("Automatinės analizės vaizdas žemėlapyje", fontsize=12, fontweight="bold")

    plt.tight_layout()

    img_buffer = BytesIO()
    plt.savefig(
        img_buffer,
        format="png",
        dpi=170,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)
    img_buffer.seek(0)

    return img_buffer


def sukurti_reportlab_paveiksla_su_proporcija(
    image_buffer: BytesIO,
    max_plotis_mm: float,
    max_aukstis_mm: float,
):
    reader = ImageReader(image_buffer)
    orig_plotis_px, orig_aukstis_px = reader.getSize()

    if orig_plotis_px == 0 or orig_aukstis_px == 0:
        image_buffer.seek(0)
        return Image(image_buffer, width=max_plotis_mm * mm)

    max_plotis = max_plotis_mm * mm
    max_aukstis = max_aukstis_mm * mm

    mastelis_plotis = max_plotis / orig_plotis_px
    mastelis_aukstis = max_aukstis / orig_aukstis_px
    mastelis = min(mastelis_plotis, mastelis_aukstis)

    galutinis_plotis = orig_plotis_px * mastelis
    galutinis_aukstis = orig_aukstis_px * mastelis

    image_buffer.seek(0)
    return Image(image_buffer, width=galutinis_plotis, height=galutinis_aukstis)


def sukurti_legenda_duomenims(automatiniai_sluoksniai: list[dict] | None) -> list[list[str]]:
    legenda = [["Žymėjimas", "Sluoksnis"]]
    legenda.append(["■", "Analizuojamas sklypas"])

    if automatiniai_sluoksniai:
        for sluoksnis in automatiniai_sluoksniai:
            legenda.append(["■", _tekstas(sluoksnis.get("pavadinimas"))])

    return legenda


# =========================================================
# 7. Pagrindinė PDF funkcija
# =========================================================

def generuoti_pdf_ataskaita(
    rasto_atviro_sklypo_info: dict | None,
    rasto_atviro_sklypo_atributai: dict | None,
    rezultato_dict: dict | None,
    automatiniai_sluoksniai: list[dict] | None,
    ml_prognoze: str | None,
    bp_zonos_tekstas: str | None,
    sklypo_geojson: dict | None = None,
    rankines_validacijos_santrauka: dict | None = None,
) -> bytes:
    _registruoti_sriftus()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    stilius_pavadinimas = ParagraphStyle(
        "Pavadinimas",
        parent=styles["Title"],
        fontName="PDFBold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    stilius_antraste = ParagraphStyle(
        "Antraste",
        parent=styles["Heading2"],
        fontName="PDFBold",
        fontSize=12,
        leading=15,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=6,
    )

    stilius_tekstas = ParagraphStyle(
        "Tekstas",
        parent=styles["BodyText"],
        fontName="PDFRegular",
        fontSize=10,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )

    stilius_bold = ParagraphStyle(
        "TekstasBold",
        parent=styles["BodyText"],
        fontName="PDFBold",
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    story = []

    # 1. Antraštė
    story.append(Paragraph("Automatinė sklypo analizės ataskaita", stilius_pavadinimas))
    story.append(
        Paragraph(
            f"Sugeneravimo data: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            stilius_tekstas,
        )
    )
    story.append(Spacer(1, 4 * mm))

    # 2. Sklypo identifikacija
    story.append(Paragraph("1. Sklypo identifikacija", stilius_antraste))

    atviri_unikalus_nr = None
    atviri_kadastro_nr = None
    if rasto_atviro_sklypo_info:
        atviri_unikalus_nr = rasto_atviro_sklypo_info.get("atviru_unikalus_nr")
        atviri_kadastro_nr = rasto_atviro_sklypo_info.get("atviru_kadastro_nr")

    adresas = None
    plotas_ha = None
    paskirties_tipas = None

    if rasto_atviro_sklypo_atributai:
        adresas = rasto_atviro_sklypo_atributai.get("adresas") or rasto_atviro_sklypo_atributai.get("ADRESAS")
        plotas_ha = rasto_atviro_sklypo_atributai.get("skl_plotas") or rasto_atviro_sklypo_atributai.get("PLOTAS_REG")
        paskirties_tipas = rasto_atviro_sklypo_atributai.get("pask_tipas") or rasto_atviro_sklypo_atributai.get("PASK_TIP")

    ident_data = [
        ["Unikalus numeris", _tekstas(atviri_unikalus_nr)],
        ["Kadastro numeris", _tekstas(atviri_kadastro_nr)],
        ["Adresas", _tekstas(adresas)],
        ["Plotas, ha", _ha_tiksliai(plotas_ha)],
        ["Paskirties tipas", _suformuoti_paskirties_tipa(paskirties_tipas)],
    ]

    ident_table = Table(ident_data, colWidths=[55 * mm, 105 * mm])
    ident_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2f2")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "PDFRegular"),
                ("FONTNAME", (0, 0), (0, -1), "PDFBold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(ident_table)
    story.append(Spacer(1, 3 * mm))

    story.append(
        Paragraph(
            _gauti_dabartines_paskirties_paaiskinima(paskirties_tipas),
            stilius_tekstas,
        )
    )
    story.append(Spacer(1, 2 * mm))

    # 3. BP informacija
    story.append(Paragraph("2. Bendrojo plano santrauka", stilius_antraste))

    bp_pav = rezultato_dict.get("pagrindine_zona_pavadinimas") if rezultato_dict else None
    bp_kodas = rezultato_dict.get("pagrindine_zona_kodas") if rezultato_dict else None
    bp_intens = rezultato_dict.get("pagrindine_u_intens") if rezultato_dict else None
    bp_aukstai = rezultato_dict.get("pagrindine_max_auk_sk") if rezultato_dict else None
    bp_paskirtis = rezultato_dict.get("pagrindine_pagr_pask") if rezultato_dict else None

    bp_data = [
        ["Pagrindinė zona", _tekstas(bp_pav)],
        ["Zonos kodas", _tekstas(bp_kodas)],
        ["Užstatymo intensyvumas", _tekstas(bp_intens)],
        ["Maks. aukštų skaičius", _tekstas(bp_aukstai)],
        ["BP pagrindinė paskirtis", _suformuoti_pagrindine_paskirti(bp_paskirtis)],
    ]

    bp_table = Table(bp_data, colWidths=[55 * mm, 105 * mm])
    bp_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2f2")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "PDFRegular"),
                ("FONTNAME", (0, 0), (0, -1), "PDFBold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(bp_table)
    story.append(Spacer(1, 2 * mm))

    if bp_zonos_tekstas:
        story.append(Paragraph(_tekstas(bp_zonos_tekstas), stilius_tekstas))
        story.append(Spacer(1, 1 * mm))

    story.append(
        Paragraph(
            _gauti_bp_paskirties_paaiskinima(bp_paskirtis),
            stilius_tekstas,
        )
    )
    story.append(Spacer(1, 3 * mm))

    # 4. Automatinė analizė
    story.append(Paragraph("3. Automatinės analizės rezultatas", stilius_antraste))

    automatinis_rez = rezultato_dict.get("automatines_analizes_rezultatas") if rezultato_dict else None
    story.append(
        Paragraph(
            f"<b>Automatinės analizės rezultatas:</b> {_tekstas(automatinis_rez)}",
            stilius_bold,
        )
    )
    story.append(
        Paragraph(
            "Šis rezultatas yra preliminarus ir paremtas automatiškai apskaičiuotais erdviniais požymiais bei taisykline analizės logika.",
            stilius_tekstas,
        )
    )
    story.append(Spacer(1, 3 * mm))

    # 5. ML prognozė
    story.append(Paragraph("4. ML prognozė", stilius_antraste))
    story.append(
        Paragraph(
            f"<b>ML prognozė:</b> {_tekstas(ml_prognoze)}",
            stilius_bold,
        )
    )
    story.append(
        Paragraph(
            _tekstas(_ml_paaiskinimas(ml_prognoze)),
            stilius_tekstas,
        )
    )
    story.append(Spacer(1, 4 * mm))

    # 6. Automatinių ribojimų santrauka
    story.append(Paragraph("5. Automatinių ribojimų santrauka", stilius_antraste))

    if automatiniai_sluoksniai:
        ribojimu_data = [[
            "Sluoksnis",
            "Plotas sklype, m²",
            "Dalis sklypo, %",
        ]]

        for sluoksnis in automatiniai_sluoksniai:
            ribojimu_data.append([
                _tekstas(sluoksnis.get("pavadinimas")),
                _m2_be_kablelio(sluoksnis.get("plotas_m2")),
                _proc_du_skaitmenys(sluoksnis.get("procentas")),
            ])

        ribojimu_table = Table(
            ribojimu_data,
            colWidths=[82 * mm, 32 * mm, 31 * mm],
            repeatRows=1,
        )
        ribojimu_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9eaf7")),
                    ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "PDFBold"),
                    ("FONTNAME", (0, 1), (-1, -1), "PDFRegular"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(ribojimu_table)
    else:
        story.append(Paragraph("Automatinių ribojimų šiame bloke nenustatyta.", stilius_tekstas))

    story.append(Spacer(1, 4 * mm))

    # 7. Žemėlapis
    story.append(Paragraph("6. Automatinės analizės vaizdas žemėlapyje", stilius_antraste))

    zemelapio_png = generuoti_automatines_analizes_zemelapio_png(
        sklypo_geojson=sklypo_geojson,
        automatiniai_sluoksniai=automatiniai_sluoksniai,
    )

    if zemelapio_png:
        zemelapio_img = sukurti_reportlab_paveiksla_su_proporcija(
            zemelapio_png,
            max_plotis_mm=128,
            max_aukstis_mm=76,
        )
        story.append(zemelapio_img)
        story.append(Spacer(1, 1 * mm))

        legenda_data = sukurti_legenda_duomenims(automatiniai_sluoksniai)
        legenda_table = Table(legenda_data, colWidths=[26 * mm, 119 * mm], repeatRows=1)

        legenda_stilius = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "PDFBold"),
            ("FONTNAME", (1, 1), (1, -1), "PDFRegular"),
            ("FONTNAME", (0, 1), (0, -1), "PDFBold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (0, -1), 16),
            ("FONTSIZE", (1, 1), (1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]

        for eil_nr in range(1, len(legenda_data)):
            if eil_nr == 1:
                legenda_stilius.append(("TEXTCOLOR", (0, eil_nr), (0, eil_nr), colors.black))
            else:
                sluoksnis = automatiniai_sluoksniai[eil_nr - 2]
                spalva_hex = PDF_ZEMELAPIO_SPALVOS.get(
                    sluoksnis.get("kodas"),
                    sluoksnis.get("spalva", "#4f81bd"),
                )
                legenda_stilius.append(("TEXTCOLOR", (0, eil_nr), (0, eil_nr), colors.HexColor(spalva_hex)))

        legenda_table.setStyle(TableStyle(legenda_stilius))
        story.append(legenda_table)

        story.append(
            Paragraph(
                "Žemėlapyje rodomas analizuojamas sklypas ir tie automatinės analizės sluoksniai, kurie realiai kertasi su sklypu.",
                stilius_tekstas,
            )
        )
    else:
        story.append(Paragraph("Žemėlapio paveikslo šiai ataskaitai sugeneruoti nepavyko.", stilius_tekstas))

    story.append(Spacer(1, 4 * mm))

    # 8. Ribojimų paaiškinimai
    story.append(Paragraph("7. Ribojimų paaiškinimai", stilius_antraste))

    if automatiniai_sluoksniai:
        for sluoksnis in automatiniai_sluoksniai:
            pavadinimas = _tekstas(sluoksnis.get("pavadinimas"))
            tekstas = gauti_ataskaitini_sluoksnio_teksta(
                sluoksnis,
                visi_sluoksniai=automatiniai_sluoksniai,
            )

            if tekstas and tekstas != "—":
                story.append(Paragraph(f"<b>{pavadinimas}</b>", stilius_bold))
                story.append(Paragraph(tekstas, stilius_tekstas))
                story.append(Spacer(1, 2 * mm))
    else:
        story.append(Paragraph("Papildomų ribojimų paaiškinimų nėra, nes sankirtų nenustatyta.", stilius_tekstas))

    # 9. Rankinė validacija
    story.append(Paragraph("8. Rankinės validacijos vieta", stilius_antraste))

    if rankines_validacijos_santrauka:
        rank_data = [
            ["SŽNS vertinimas", _tekstas(rankines_validacijos_santrauka.get("szns_rezultatas"))],
            ["Galutinis sprendimas", _tekstas(rankines_validacijos_santrauka.get("galutinis_sprendimas"))],
            ["Reikia papildomos patikros", _tekstas(rankines_validacijos_santrauka.get("papildoma_patikra"))],
            ["Pastaba", _tekstas(rankines_validacijos_santrauka.get("pastaba"))],
            ["Paaiškinimas", _tekstas(rankines_validacijos_santrauka.get("paaiskinimas"))],
        ]
    else:
        rank_data = [
            ["SŽNS vertinimas", "—"],
            ["Galutinis sprendimas", "—"],
            ["Reikia papildomos patikros", "—"],
            ["Pastaba", "Palikta vieta specialisto pastaboms."],
            ["Paaiškinimas", "Galutinis sprendimas gali reikalauti papildomos rankinės peržiūros."],
        ]

    rank_table = Table(rank_data, colWidths=[55 * mm, 105 * mm])
    rank_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2f2")),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "PDFRegular"),
                ("FONTNAME", (0, 0), (0, -1), "PDFBold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(rank_table)
    story.append(Spacer(1, 4 * mm))

    # 10. Pastaba
    story.append(Paragraph("9. Svarbi pastaba", stilius_antraste))
    story.append(
        Paragraph(
            "Ši ataskaita yra preliminari ir skirta kaip pagalbinė priemonė teritorijos vystymo palankumui įvertinti. Automatinės analizės rezultatas ir ML prognozė nepakeičia specialisto vertinimo. Skirtingose funkcinėse zonose gali būti galimi skirtingų tipų statiniai ar veikla, todėl išvada turi būti vertinama kartu su teritorijos paskirtimi, ribojimais ir projektinių sprendinių pobūdžiu. Galutinis sprendimas gali reikalauti papildomos teritorijų planavimo dokumentų, SŽNS, projektinių sąlygų ir kitų teisinių bei faktinių aplinkybių peržiūros.",
            stilius_tekstas,
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes