# Void Linux smoke test

Five minutes, by hand, on a machine that has never run EKSB. Void is not in
the CI matrix, so this is the check that nothing depends on glibc, systemd,
Arch packaging or a developer's home directory.

Works unchanged on any musl or glibc Linux without systemd.

## Prerequisites

```sh
xbps-install -S python3 python3-pip git
python3 --version        # must be 3.11 or newer
```

## The test

Run every line. Each `#` note says what must be true.

```sh
# 1. isolate: pretend this user has never seen EKSB
export EKSB_TEST=$(mktemp -d)
export HOME="$EKSB_TEST/home"
export EKSB_CONFIG_DIR="$EKSB_TEST/config"
mkdir -p "$HOME"
cd "$EKSB_TEST"

# 2. clone and install into a venv
git clone https://github.com/ViniciusOliveiraOV/EmergentKnowledgeSB
cd EmergentKnowledgeSB
python3 -m venv "$EKSB_TEST/venv"
. "$EKSB_TEST/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install .
#    -> installs with only PyYAML pulled in

# 3. the command exists
eksb --version           # -> eksb 0.1.0a1
eksb --help              # -> short help, no traceback

# 4. first run, in Portuguese, choosing the demo
printf '2\n1\n' | eksb
#    -> language menu, then Portuguese throughout
#    -> "Pronto. Seu EKSB está preparado."

# 5. the demo is real
eksb search "partitioning"
#    -> 7 results, "Horizontal Partitioning" first

eksb provenance "Time-Range Partitioning"
#    -> "Veio de": the source conversation, chatgpt, 2026-08-24
#    -> three claims: two "você disse", one "um assistente sugeriu"
#    -> "é uma versão posterior de Tenant Sharding"

eksb attention
#    -> perguntas em aberto, afirmações não verificadas, posições mudadas

eksb validate
#    -> 7 notes · 0 errors · 0 warnings

# 6. a workspace of your own, in a path with a space and an accent
eksb init "$HOME/Meu Espaço EKSB"
eksb doctor "$HOME/Meu Espaço EKSB"
#    -> "O EKSB está pronto."
#    -> Obsidian: "não detectado" — and that is NOT an error

# 7. writing works
eksb add --type decision "Usar PostgreSQL" -w "$HOME/Meu Espaço EKSB"
printf 'Eu: e o Mongo?\nAssistente: talvez.\n' > "$EKSB_TEST/conversa.md"
eksb save "$EKSB_TEST/conversa.md" --kind chatgpt -w "$HOME/Meu Espaço EKSB"
eksb validate "$HOME/Meu Espaço EKSB"
#    -> 3 notes · 0 errors · 0 warnings

# 8. raw history is protected
sed -i 's/talvez/com certeza/' "$HOME/Meu Espaço EKSB/_sources/conversa.md"
eksb validate "$HOME/Meu Espaço EKSB"
#    -> ERROR ... content_hash mismatch — raw body was edited

# 9. errors are sentences, not tracebacks
cd "$EKSB_TEST" && eksb search algo -w /nonexistent
#    -> "Não existe um workspace EKSB em /nonexistent."
#    -> NO Python traceback

# 10. no background process, no network
eksb about
#    -> "Nada roda em segundo plano."
#    -> "O EKSB não faz nenhuma conexão de rede."
ps -A | grep -i eksb        # -> nothing but the grep itself

# 11. the language switch persists
eksb config --set-lang en
eksb attention -w "$HOME/Meu Espaço EKSB" | head -3
#    -> English

# 12. the suite, on this machine
python -m pip install -e ".[dev]"
python -m pytest -q
#    -> all pass
python -m eksb.validate --selftest
#    -> selftest ok
```

## Clean up

```sh
deactivate
rm -rf "$EKSB_TEST"
```

Nothing outside `$EKSB_TEST` was touched — that is itself part of what this
test checks.

## Report

If any step differs, open an issue with the step number, the command, the
full output, `python3 --version`, and `xbps-query -l | grep python`.

Failures worth reporting even if they look small: a traceback anywhere, a
mojibake character in the Portuguese output, a path with a space or accent
being rejected, or `eksb doctor` calling a missing optional integration a
problem.
