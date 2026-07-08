import sharp from "sharp";
import { existsSync, mkdirSync } from "node:fs";

/* eslint-disable no-undef */
const sizes = [192, 512];
const publicDir = "./public";
const logoSource = "./public/logo.svg";

if (!existsSync(publicDir)) {
  mkdirSync(publicDir, { recursive: true });
}

if (!existsSync(logoSource)) {
  console.error("HATA: Logo dosyasi bulunamadi:", logoSource);
  console.error("Lutfen logo.svg dosyasini public/ altina koyun.");
  process.exit(1);
}

for (const size of sizes) {
  await sharp(logoSource)
    .resize(size, size, { fit: "contain", background: { r: 245, g: 245, b: 245, alpha: 1 } })
    .png()
    .toFile(`${publicDir}/pwa-${size}x${size}.png`);

  console.log(`ok: pwa-${size}x${size}.png`);
}

await sharp(`${publicDir}/pwa-192x192.png`).toFile(`${publicDir}/apple-touch-icon.png`);
console.log("ok: apple-touch-icon.png");
