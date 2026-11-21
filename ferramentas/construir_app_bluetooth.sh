#!/usr/bin/env bash
# Monta o app auxiliar da capacidade bluetooth (controle-ir/capacidades/bluetooth/app) num APK assinado.
# Precisa do build-tools 35 e da plataforma 35 do Android SDK:
#   ANDROID_BUILD_TOOLS=<pasta com aapt2, d8, zipalign, apksigner>  ANDROID_JAR=<platforms/android-35/android.jar>
# A chave de assinatura fica FORA do repositório (CONTROLE_IR_CHAVE_APK, padrão ~/.controle-ir-apk.jks): se ela
# mudar, o Controle IR desinstala e reinstala o app sozinho (não há dados a perder).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
CAP="$RAIZ/controle-ir/capacidades/bluetooth"
BT="${ANDROID_BUILD_TOOLS:?defina ANDROID_BUILD_TOOLS}"
JAR="${ANDROID_JAR:?defina ANDROID_JAR}"
CHAVE="${CONTROLE_IR_CHAVE_APK:-$HOME/.controle-ir-apk.jks}"
VERSAO="${VERSAO_APP:-1}"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT

"$BT/aapt2" link --manifest "$CAP/app/AndroidManifest.xml" -I "$JAR" -o "$T/base.apk" \
  --min-sdk-version 26 --target-sdk-version 35 --version-code "$VERSAO" --version-name "1.$VERSAO"
mkdir -p "$T/cls"
javac -nowarn -source 8 -target 8 -encoding UTF-8 -bootclasspath "$JAR" -cp "$JAR" -d "$T/cls" \
  "$CAP/java/controleir/Bluetooth.java" $(find "$CAP/app/java" -name '*.java') 2>&1 | grep -vE "^(Picked up|warning:|[0-9]+ warning)" || true
"$BT/d8" --release --min-api 26 --lib "$JAR" --output "$T" $(find "$T/cls" -name '*.class')
(cd "$T" && cp base.apk sem_assinatura.apk && zip -q -X sem_assinatura.apk classes.dex)
"$BT/zipalign" -f -p 4 "$T/sem_assinatura.apk" "$T/alinhado.apk"
if [ ! -f "$CHAVE" ]; then
  keytool -genkeypair -keystore "$CHAVE" -storepass controleir -keypass controleir -alias controleir \
    -keyalg RSA -keysize 3072 -validity 36500 -dname "CN=Controle IR Bluetooth" >/dev/null 2>&1
fi
"$BT/apksigner" sign --ks "$CHAVE" --ks-pass pass:controleir --ks-key-alias controleir \
  --out "$CAP/app/controle-ir-bluetooth.apk" "$T/alinhado.apk"
rm -f "$CAP/app/controle-ir-bluetooth.apk.idsig"
"$BT/apksigner" verify "$CAP/app/controle-ir-bluetooth.apk"
sha256sum "$CAP/app/controle-ir-bluetooth.apk" | cut -c1-16
