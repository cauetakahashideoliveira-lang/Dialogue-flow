#!/data/data/com.termux/files/usr/bin/bash
# Instalador do Controle IR para Termux (Android).
# Pode ser executado de novo para atualizar: mantém aparelhos, catálogo ampliado e segredo.
DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"

etapa() { printf '\n\033[1;36m▶ %s\033[0m\n' "$1"; }
ok() { printf '  \033[32m✔\033[0m %s\n' "$1"; }
falha() {
  printf '\n\033[1;31m✖ ERRO na etapa: %s\033[0m\n  %s\n' "$1" "$2"
  printf '  Copie esta mensagem e envie ao Claude para receber ajuda.\n'
  exit 1
}

if [ -z "$PREFIX" ] || [ ! -d "$PREFIX/bin" ] || ! command -v pkg >/dev/null 2>&1; then
  falha "verificação do Termux" "Este instalador precisa rodar dentro do app Termux (versão do F-Droid)."
fi

etapa "1/6 Instalando pacotes (python, cloudflared, termux-api)…"
if ! pkg install -y python cloudflared termux-api; then
  falha "instalação de pacotes" "Rode  pkg update -y && pkg upgrade -y  e cole a linha de instalação de novo."
fi
command -v python3 >/dev/null || falha "instalação de pacotes" "python3 não foi instalado."
ok "pacotes instalados"

etapa "2/6 Consultando o emissor infravermelho…"
SAIDA="$(timeout 25 termux-infrared-frequencies 2>&1)"
RC=$?
if [ $RC -eq 124 ]; then
  falha "consulta ao emissor" "O Termux:API não respondeu. Instale o app Termux:API da MESMA fonte do Termux (F-Droid), abra-o uma vez, permita a execução em segundo plano e repita."
fi
case "$SAIDA" in
  *'"min"'*)
    FREQS="$(printf '%s' "$SAIDA" | grep -o '"min": *[0-9]*' | grep -o '[0-9]*' | awk '{printf "%d kHz  ", $1/1000}')"
    ok "emissor encontrado: $FREQS" ;;
  *'[]'*)
    falha "consulta ao emissor" "O Android informou que este aparelho não tem emissor infravermelho." ;;
  *)
    falha "consulta ao emissor" "Resposta inesperada do Termux:API: $SAIDA" ;;
esac

etapa "3/6 Instalando o comando controle-ir…"
cat > "$PREFIX/bin/controle-ir" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
export PYTHONPATH="$DIR" PYTHONUNBUFFERED=1
exec python3 -m controle_ir "\$@"
EOF
chmod 700 "$PREFIX/bin/controle-ir"
PYTHONPATH="$DIR" python3 -c "import controle_ir, sqlite3, ssl" 2>"${TMPDIR:-$HOME}/cir-erro.txt" \
  || falha "instalação do comando" "$(cat "${TMPDIR:-$HOME}/cir-erro.txt")"
ok "comando disponível: controle-ir"

etapa "4/6 Preparando os perfis de controle…"
if ! controle-ir catalogo reconstruir; then
  falha "preparação dos perfis" "Não consegui montar o catálogo. Confira o espaço livre do celular."
fi
ok "catálogo base pronto (SmartIR + Flipper-IRDB CC0)"

etapa "5/6 Catálogo ampliado (opcional)"
if [ -d "$HOME/.controle-ir/fontes/Flipper-IRDB-main" ]; then
  ok "catálogo ampliado já instalado"
elif [ -t 0 ]; then
  echo "  A Flipper-IRDB completa adiciona ~9 mil controles (TVs, som, LED, ventiladores, câmeras…)."
  echo "  Recomendado para aparelhos antigos ou raros. Licença: CC0 só para arquivos de ago/2025 em diante;"
  echo "  os anteriores não declaram licença — o download é seu, para uso pessoal."
  read -r -p "  Baixar agora (~40 MB, alguns minutos)? [S/n] " R
  case "${R:-s}" in
    s|S|sim|Sim|y|Y) controle-ir catalogo ampliar --sim || echo "  (falhou; dá para tentar depois com: controle-ir catalogo ampliar)";;
    *) echo "  Pulado. Para ampliar depois: controle-ir catalogo ampliar";;
  esac
fi

etapa "6/6 Iniciando o servidor…"
mkdir -p "$HOME/.termux"
echo "  Mantenha o Termux aberto. Para reabrir depois, digite: controle-ir"
echo "  Dica (HyperOS): Configurações → Apps → Termux → Economia de bateria → Sem restrições."
exec controle-ir
