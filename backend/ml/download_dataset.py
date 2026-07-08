"""
SağlıkCebim - NIH ChestX-ray14 Dataset İndirici
~45GB toplam boyut. İndirme ve çıkartma işlemi internet hızına göre değişir.

Kullanım:
    python download_dataset.py --method kaggle
    python download_dataset.py --method direct
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "chestxray14"))

# NIH Box doğrudan indirme linkleri (resmi)
NIH_IMAGE_LINKS = [
    "https://nihcc.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c.gz",  # images_001
    "https://nihcc.box.com/shared/static/i28rlmbvmfjbl8p2n3ris0tt1f1y7ul3.gz",  # images_002
    "https://nihcc.box.com/shared/static/f1t00wrtdk94satdfb9olcolqx20telehl.gz", # images_003
    "https://nihcc.box.com/shared/static/0aowwzs5lclqy8to4sas0axag30hh0gm.gz",  # images_004
    "https://nihcc.box.com/shared/static/v5e3goj22zr6h8tzualxfsqlqaygfbsn.gz",  # images_005
    "https://nihcc.box.com/shared/static/asi7ikud9jwnkrnkj99jnpfkjdes7l6l.gz",  # images_006
    "https://nihcc.box.com/shared/static/jn1b4mw4n6lnh74ovmcjb8y48h8xj07n.gz",  # images_007
    "https://nihcc.box.com/shared/static/tvpxmn7qyrgl0w8wfh9kqfjskv6nmm1j.gz",  # images_008
    "https://nihcc.box.com/shared/static/upyy3ml7qdumlgk2rfcvlb9k6gvqq2pj.gz",  # images_009
    "https://nihcc.box.com/shared/static/l6nilvfa9cg3s28tqv1qc1olm3gnz54p.gz",  # images_010
    "https://nihcc.box.com/shared/static/nh2ber85ckcr0b384sn2u9ywmx1g8vbg.gz",  # images_011
    "https://nihcc.box.com/shared/static/phogv4ai26p0vzcuky4f2sjkj3mwvyic.gz",  # images_012
]

NIH_METADATA_LINKS = {
    "Data_Entry_2017_v2020.csv": "https://nihcc.box.com/shared/static/1if8fulnr6bo1j0lbxzwvf8lhqoq3khp.csv",
    "BBox_List_2017.csv": "https://nihcc.box.com/shared/static/xdsj0b3ql6rjua75mudkmal9r5bt0lyc.csv",
    "train_val_list.txt": "https://nihcc.box.com/shared/static/84p65fgqiwb2swhmqpi04ybn1kse8sg6.txt",
    "test_list.txt": "https://nihcc.box.com/shared/static/llk5d4dztqmdsh6jnhcqjsi96o5e7sk.txt",
}


def download_file(url, dest_path, desc=""):
    """Dosya indir ve ilerleme göster."""
    if os.path.exists(dest_path):
        print(f"  [ATLANDI] {desc or dest_path} zaten mevcut")
        return True

    print(f"  İndiriliyor: {desc or os.path.basename(dest_path)}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            block_size = 1024 * 1024  # 1MB

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            tmp_path = dest_path + ".tmp"

            with open(tmp_path, "wb") as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded / total * 100
                        mb_done = downloaded / (1024 * 1024)
                        mb_total = total / (1024 * 1024)
                        print(f"\r    {mb_done:.1f}/{mb_total:.1f} MB ({pct:.1f}%)", end="", flush=True)
                    else:
                        mb_done = downloaded / (1024 * 1024)
                        print(f"\r    {mb_done:.1f} MB indirild", end="", flush=True)

            os.replace(tmp_path, dest_path)
            print()
            return True

    except Exception as e:
        print(f"\n  [HATA] İndirme başarısız: {e}")
        tmp_path = dest_path + ".tmp"
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False


def extract_tar_gz(archive_path, extract_to):
    """tar.gz dosyasını çıkart."""
    print(f"  Çıkartılıyor: {os.path.basename(archive_path)}...")
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=extract_to)
        print(f"  [OK] Çıkartıldı")
        return True
    except Exception as e:
        print(f"  [HATA] Çıkartma başarısız: {e}")
        return False


def download_via_kaggle():
    """Kaggle API ile dataset indir (en güvenilir yöntem)."""
    print("\n" + "=" * 60)
    print("  KAGGLE API İLE İNDİRME")
    print("=" * 60)

    # Kaggle kurulu mu?
    try:
        import kaggle  # noqa: F401
        print("[OK] Kaggle paketi bulundu")
    except ImportError:
        print("[!] Kaggle paketi kuruluyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])

    # API key kontrolü
    kaggle_dir = os.path.join(os.path.expanduser("~"), ".kaggle")
    kaggle_json = os.path.join(kaggle_dir, "kaggle.json")

    if not os.path.exists(kaggle_json):
        print("\n[!] Kaggle API anahtarı bulunamadı!")
        print("    1. https://www.kaggle.com/settings adresine gidin")
        print("    2. 'API' bölümünde 'Create New Token' butonuna tıklayın")
        print(f"    3. İndirilen kaggle.json dosyasını şuraya koyun: {kaggle_dir}")
        print("    4. Bu scripti tekrar çalıştırın")
        print()

        os.makedirs(kaggle_dir, exist_ok=True)
        api_key = input("Kaggle username: ").strip()
        api_token = input("Kaggle key: ").strip()

        if api_key and api_token:
            import json
            with open(kaggle_json, "w") as f:
                json.dump({"username": api_key, "key": api_token}, f)
            # Windows'ta chmod gerekmez
            print(f"[OK] API anahtarı kaydedildi: {kaggle_json}")
        else:
            print("[HATA] API bilgileri eksik, çıkılıyor.")
            return False

    print("\n[*] NIH Chest X-ray14 indiriliyor (Kaggle)...")
    print("    Bu işlem ~45GB indirecektir, internet hızınıza göre uzun sürebilir.\n")

    try:
        subprocess.check_call([
            sys.executable, "-m", "kaggle", "datasets", "download",
            "-d", "nih-chest-xrays/data",
            "-p", DATA_DIR,
            "--unzip",
        ])
        print("\n[OK] Dataset başarıyla indirildi!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[HATA] Kaggle indirme başarısız: {e}")
        return False


def download_via_direct():
    """NIH Box doğrudan linklerinden indir."""
    print("\n" + "=" * 60)
    print("  NIH DOĞRUDAN İNDİRME")
    print("=" * 60)
    print(f"  Hedef klasör: {DATA_DIR}")
    print(f"  Toplam boyut: ~45 GB")
    print()

    os.makedirs(DATA_DIR, exist_ok=True)
    images_dir = os.path.join(DATA_DIR, "images")
    os.makedirs(images_dir, exist_ok=True)
    archives_dir = os.path.join(DATA_DIR, "_archives")
    os.makedirs(archives_dir, exist_ok=True)

    # 1) Metadata dosyaları
    print("[1/3] Metadata dosyaları indiriliyor...")
    for filename, url in NIH_METADATA_LINKS.items():
        dest = os.path.join(DATA_DIR, filename)
        if not download_file(url, dest, filename):
            print(f"  [UYARI] {filename} indirilemedi, devam ediliyor...")

    # 2) Görüntü arşivleri
    print(f"\n[2/3] Görüntü arşivleri indiriliyor (12 dosya)...")
    for i, url in enumerate(NIH_IMAGE_LINKS, 1):
        archive_name = f"images_{i:03d}.tar.gz"
        archive_path = os.path.join(archives_dir, archive_name)
        if not download_file(url, archive_path, f"{archive_name} ({i}/12)"):
            print(f"  [HATA] {archive_name} indirilemedi!")
            continue

    # 3) Arşivleri çıkart
    print(f"\n[3/3] Arşivler çıkartılıyor...")
    for i in range(1, 13):
        archive_name = f"images_{i:03d}.tar.gz"
        archive_path = os.path.join(archives_dir, archive_name)
        if os.path.exists(archive_path):
            extract_tar_gz(archive_path, DATA_DIR)

    # Görüntüleri düzle (images_xxx/images/ → images/)
    for subdir in os.listdir(DATA_DIR):
        nested = os.path.join(DATA_DIR, subdir, "images")
        if os.path.isdir(nested) and subdir.startswith("images_"):
            for img in os.listdir(nested):
                src = os.path.join(nested, img)
                dst = os.path.join(images_dir, img)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            shutil.rmtree(os.path.join(DATA_DIR, subdir))

    return True


def verify_dataset():
    """Dataset bütünlüğünü kontrol et."""
    print("\n" + "=" * 60)
    print("  DATASET DOĞRULAMA")
    print("=" * 60)

    csv_path = os.path.join(DATA_DIR, "Data_Entry_2017_v2020.csv")
    train_list = os.path.join(DATA_DIR, "train_val_list.txt")
    test_list = os.path.join(DATA_DIR, "test_list.txt")
    images_dir = os.path.join(DATA_DIR, "images")

    checks = {
        "Data_Entry_2017_v2020.csv": os.path.exists(csv_path),
        "train_val_list.txt": os.path.exists(train_list),
        "test_list.txt": os.path.exists(test_list),
        "images/ klasörü": os.path.isdir(images_dir),
    }

    all_ok = True
    for name, ok in checks.items():
        status = "[OK]" if ok else "[EKSIK]"
        print(f"  {status} {name}")
        if not ok:
            all_ok = False

    if os.path.isdir(images_dir):
        img_count = len([f for f in os.listdir(images_dir) if f.endswith(".png")])
        expected = 112120
        status = "[OK]" if img_count >= expected * 0.99 else "[UYARI]"
        print(f"  {status} Görüntü sayısı: {img_count:,} / {expected:,} beklenen")
        if img_count < expected * 0.99:
            all_ok = False

    if all_ok:
        print("\n  ✓ Dataset hazır! Eğitime başlayabilirsiniz:")
        print(f"    cd {os.path.dirname(__file__)}")
        print(f"    python train.py")
    else:
        print("\n  ✗ Bazı dosyalar eksik. İndirmeyi tekrar deneyin.")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description="NIH ChestX-ray14 Dataset İndirici")
    parser.add_argument(
        "--method",
        choices=["kaggle", "direct", "verify"],
        default="kaggle",
        help="İndirme yöntemi: kaggle (önerilen), direct (NIH Box), verify (sadece kontrol)",
    )
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  SağlıkCebim - NIH ChestX-ray14 Dataset İndirici       ║")
    print("║  112,120 göğüs X-ray görüntüsü · 14 patoloji sınıfı   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n  Hedef klasör: {DATA_DIR}")

    if args.method == "verify":
        verify_dataset()
    elif args.method == "kaggle":
        if download_via_kaggle():
            verify_dataset()
    elif args.method == "direct":
        if download_via_direct():
            verify_dataset()


if __name__ == "__main__":
    main()
