"""Türk hastane PDF formatlarını test eden analiz scripti."""
import sys
sys.path.insert(0, ".")
from app.services.pdf_parser import parse_test_results

test_cases = {
    # === SENİN PDF'İN BÜYÜK İHTİMALLE BU FORMATA YAKIN ===
    "Format_A_Basit": "Hemoglobin  13.5  g/dL  12.0-16.0\nWBC  7.2  10^3/uL  4.0-10.0\nPLT  250  10^3/uL  150-400",

    # === BAŞKA BİRİNİN PDF'İ - FARKLI FORMATLAR ===

    # Format B: Sonuç ve referans arasında birim yok, birim sonda
    "Format_B_Birim_Sonda": "Hemoglobin 13.5 12.0 - 16.0 g/dL\nWBC 7.2 4.0 - 10.0 10^3/uL",

    # Format C: Uzun test adı + parantez kısaltma + geniş boşluk
    "Format_C_Genis_Bosluk": "Hemoglobin (HGB)                    13.5 g/dL            12.0  -  16.0\nLokosit (WBC)                       7200 /uL             4000  -  10000",

    # Format D: Referans aralığı parantez içinde
    "Format_D_Parantez_Ref": "Hemoglobin    13.5 g/dL    (12.0 - 16.0)\nWBC           7.2 10^3/uL  (4.0 - 10.0)\nGlukoz        95 mg/dL     (70 - 100)",

    # Format E: Bayrak sütunu (H/L/N)
    "Format_E_Bayrak": "Hemoglobin  13.5  g/dL  12.0-16.0  N\nGlukoz      145   mg/dL 70-100     H\nDemir       30    ug/dL 50-170     L",

    # Format F: Binlik ayırıcı nokta (250.000 gibi)
    "Format_F_Binlik": "Lokosit Sayisi   7.200  /uL  4.000-10.000\nTrombosit        250.000 /uL 150.000-400.000\nEritrosit        4.850.000 /uL 4.000.000-5.500.000",

    # Format G: Çok satırlı (test adı bir satır, sonuç başka satırda)
    "Format_G_Cok_Satirli": "Hemoglobin (HGB)\nSonuc: 13.5 g/dL  Referans: 12.0 - 16.0\nGlukoz (Aclik)\nSonuc: 95 mg/dL   Referans: 70 - 100",

    # Format H: Türkçe uzun test adları
    "Format_H_Uzun_Isim": "Aclik Kan Sekeri (Glukoz)  95  mg/dL  70-100\nTam Kan Sayimi - Lokosit   7.2  10^3/uL  4.0-10.0\nKaraciger Fonksiyon - ALT  25  U/L  7-56\nBobrek Fonksiyon - Kreatinin  0.9  mg/dL  0.5-1.2",

    # Format I: Virgüllü ondalık
    "Format_I_Virgul": "Hemoglobin  13,5  g/dL  12,0-16,0\nGlukoz  95,0  mg/dL  70,0-100,0\nTSH  2,45  uIU/mL  0,4-4,0",

    # Format J: Kolesterol alt türleri
    "Format_J_Kolesterol": "Total Kolesterol   220  mg/dL   0-200\nLDL Kolesterol     140  mg/dL   0-130\nHDL Kolesterol     45   mg/dL   40-100\nVLDL               25   mg/dL   0-30\nTrigliserit        180  mg/dL   0-150",

    # Format K: Başlık satırlı tablo
    "Format_K_Tablo": "Test Adi          Sonuc    Birim     Referans Araligi\nHemoglobin        13.5     g/dL      12.0 - 16.0\nWBC               7.2      10^3/uL   4.0 - 10.0",

    # Format L: Referans aralığı olmayan testler
    "Format_L_Refsiz": "Hemoglobin  13.5 g/dL\nWBC  7.2 10^3/uL\nGlukoz  95 mg/dL",

    # Format M: Farklı ayırıcılar (em dash, tilde)
    "Format_M_Ozel_Karakter": "Hemoglobin  13.5  g/dL  12.0 \u2013 16.0\nGlukoz  95  mg/dL  70\u201410.0",

    # Format N: Tab-separated
    "Format_N_Tab": "Hemoglobin\t13.5\tg/dL\t12.0-16.0\nGlukoz\t95\tmg/dL\t70-100",

    # Format O: Sonuçta yıldız/bayrak işareti
    "Format_O_Isaret": "Hemoglobin  13.5*  g/dL  12.0-16.0\nGlukoz  145*H  mg/dL  70-100\nWBC  7.2  10^3/uL  4.0-10.0",

    # Format P: Referans < veya > ile verilmiş
    "Format_P_Esitsizlik": "CRP  0.5  mg/L  < 5.0\nTSH  2.5  uIU/mL  0.4-4.0\nLDL Kolesterol  140  mg/dL  < 130",

    # Format Q: Gerçek hastane - Acıbadem/Memorial tarzı
    "Format_Q_Hastane1": "HEMOGRAM\nWBC (Lokosit)  7.20  10^3/uL  4.00 - 10.00\nRBC (Eritrosit)  4.85  10^6/uL  4.00 - 5.50\nHGB (Hemoglobin)  14.2  g/dL  12.0 - 16.0\nHCT (Hematokrit)  42.5  %  36.0 - 46.0\nMCV  87.6  fL  80.0 - 100.0\nMCH  29.3  pg  27.0 - 33.0\nMCHC  33.4  g/dL  32.0 - 36.0\nRDW  13.2  %  11.5 - 14.5\nPLT (Trombosit)  245  10^3/uL  150 - 400",

    # Format R: Devlet hastanesi - sıkışık format
    "Format_R_Devlet": "HEMOGLOBIN(HGB) 14.2 g/dL 12-16\nLOKOSIT(WBC) 7200 /uL 4000-10000\nTROMBOSIT(PLT) 250000 /uL 150000-400000\nGLUKOZ 95 mg/dL 70-100\nKREATININ 0.9 mg/dL 0.5-1.2",

    # Format S: Sonuç kolonunda birim olmayan, ayrı kolon
    "Format_S_Kolon_Ayri": "Hemoglobin          14.2        g/dL        12.0 - 16.0\nLokosit              7.20       10^3/uL      4.00 - 10.00\nTrombosit           245         10^3/uL     150 - 400",

    # Format T: İdrar tahlili gibi metinsel sonuçlar
    "Format_T_Metinsel": "Renk  Sari  -  Sari\npH  6.0  -  5.0-8.0\nDansite  1.025  -  1.005-1.030\nProtein  Negatif  -  Negatif\nGlukoz  Negatif  -  Negatif",

    # Format U: Çoklu referans satırları (yaş/cinsiyet bazlı)
    "Format_U_Yas_Bazli": "Hemoglobin  14.2  g/dL\nErkek: 13.5-17.5  Kadin: 12.0-15.5\nGlukoz  95  mg/dL\nYetiskin: 70-100  Cocuk: 60-100",
}

print("=" * 85)
print("PDF FORMAT ANALiZi - Hangi formatlar parse ediliyor, hangileri edilmiyor?")
print("=" * 85)

success_count = 0
fail_count = 0

for name, text in test_cases.items():
    results = parse_test_results(text)
    if results:
        status = "OK"
        success_count += 1
    else:
        status = "FAIL"
        fail_count += 1
    count = len(results)
    print(f"\n[{status}] {name}: {count} test bulundu")
    if results:
        for r in results:
            n = r["original_name"]
            v = r["value"]
            u = r["unit"]
            rm = r["ref_min"]
            rx = r["ref_max"]
            s = r["status"]
            print(f"   -> {n:35s} = {v:>8} {u:>10s}  [{rm}-{rx}] {s}")
    else:
        preview = text[:150].replace("\n", " | ")
        print(f"   !! Hicbir test yakalanamadi!")
        print(f"   Metin: {preview}")

print("\n" + "=" * 85)
print(f"SONUC: {success_count} format basarili, {fail_count} format basarisiz")
print(f"Basari orani: {success_count}/{success_count+fail_count} = {100*success_count//(success_count+fail_count)}%")
print("=" * 85)
