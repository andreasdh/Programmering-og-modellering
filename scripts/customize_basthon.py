"""Customize the self-hosted Basthon console used by the site."""

from hashlib import sha256
from pathlib import Path
import re
import sys


TRANSLATIONS = {
    "Ouvrir un script, charger un module ou un fichier": "Open a script or load a module or file",
    "Il semble que Basthon ait rencontré un problème à sa dernière utilisation. Que voulez-vous faire ?": "The editor encountered a problem the last time it was used. What would you like to do?",
    "Il n'y a aucune sauvegarde à restaurer !": "There is no saved version to restore!",
    "Revenir à une version précédente du script": "Return to a previous version of the script",
    "Changer le thème (sombre/lumineux)": "Switch theme (dark/light)",
    "Échanger l'éditeur et la console": "Swap the editor and console",
    "Afficher l'éditeur et la console": "Show the editor and console",
    "Afficher seulement l'éditeur": "Show only the editor",
    "Afficher seulement la console": "Show only the console",
    "Chargement des fichiers auxiliaires...": "Loading auxiliary files...",
    "Chargement des modules annexes...": "Loading additional modules...",
    "Aucune sauvegarde à restaurer": "No saved version to restore",
    "Copier dans le presse-papier": "Copy to clipboard",
    "Afficher la vue graphique": "Show graphical view",
    "Afficher la console": "Show console",
    "Charger dans l'éditeur": "Load into the editor",
    "Choisir une sauvegarde": "Choose a saved version",
    "Redémarrer le noyau": "Restart the Python kernel",
    "Télécharger le script": "Download the script",
    "Partager ce document": "Share this document",
    "Exécuter le script": "Run the script",
    "Installer le module": "Install the module",
    "Chargement de Basthon...": "Loading the Python editor...",
    "Un bac à sable pour ": "Online editor for ",
    "Partager ce code": "Share this code",
    "Propulsé par ": "Powered by ",
    "Récupération": "Recovery",
    "Exécuter": "Run",
    "Annuler": "Cancel",
    "Erreur": "Error",
}


def js_literal(text):
    return '"' + text.replace('"', '\\"') + '"'


def customize_javascript(path):
    content = path.read_text(encoding="utf-8")

    dark_default = 'theme:"dark",viewMode:"default",rightPanel:"terminal"'
    light_default = 'theme:"light",viewMode:"default",rightPanel:"terminal"'
    if dark_default in content and light_default not in content:
        content = content.replace(dark_default, light_default, 1)

    stored_state_init = 'case"init":return null!=i&&(e=se(i)),e.ready=!0,e;'
    forced_light_init = 'case"init":return null!=i&&(e=se(i)),e.theme="light",e.ready=!0,e;'
    if stored_state_init in content and forced_light_init not in content:
        content = content.replace(stored_state_init, forced_light_init, 1)

    for source, target in sorted(TRANSLATIONS.items(), key=lambda item: len(item[0]), reverse=True):
        content = content.replace(js_literal(source), js_literal(target))

    path.write_text(content, encoding="utf-8")


def replace_or_insert_script(content, script_id, script):
    pattern = re.compile(rf'<script id="{re.escape(script_id)}">.*?</script>', re.DOTALL)
    if pattern.search(content):
        return pattern.sub(script, content, count=1)
    return content.replace("</head>", script + "</head>")


def customize_html(path, javascript_path):
    content = path.read_text(encoding="utf-8")
    content = content.replace('<html lang="fr">', '<html lang="en">')
    content = content.replace("<title>Basthon Console</title>", "<title>Python editor</title>")

    cache_key = sha256(javascript_path.read_bytes()).hexdigest()[:12]
    script_pattern = re.compile(r'(<script\b[^>]*\bsrc="assets/main\.[^"?]+\.js)(?:\?[^"]*)?(")')
    content, replacements = script_pattern.subn(
        lambda match: f"{match.group(1)}?custom={cache_key}{match.group(2)}",
        content,
        count=1,
    )
    if replacements != 1:
        raise RuntimeError("Could not locate the Basthon application bundle in index.html")

    site_key = Path(__file__).resolve().parents[1].name.lower().replace(" ", "-")
    style_id = f"{site_key}-basthon-style"
    if style_id not in content:
        style = (
            f'<style id="{style_id}">'
            'div:has(> a > img[alt="Basthon"]) {display: none !important;}'
            '</style>'
        )
        content = content.replace("</head>", style + "</head>")

    storage_id = f"{site_key}-basthon-storage"
    storage_script = f'''<script id="{storage_id}">
(() => {{
  "use strict";
  const source = new URLSearchParams(window.location.search).get("from");
  if (!source) return;
  const prefix = `{site_key}:basthon:${{encodeURIComponent(source)}}:`;
  const prototype = Storage.prototype;
  const nativeGetItem = prototype.getItem;
  const nativeSetItem = prototype.setItem;
  const nativeRemoveItem = prototype.removeItem;
  const nativeClear = prototype.clear;
  const nativeKey = prototype.key;
  const local = window.localStorage;
  const session = window.sessionStorage;
  const scoped = (store) => store === local || store === session;
  const key = (value) => prefix + String(value);
  prototype.getItem = function (value) {{ return nativeGetItem.call(this, scoped(this) ? key(value) : value); }};
  prototype.setItem = function (value, data) {{ return nativeSetItem.call(this, scoped(this) ? key(value) : value, data); }};
  prototype.removeItem = function (value) {{ return nativeRemoveItem.call(this, scoped(this) ? key(value) : value); }};
  prototype.clear = function () {{
    if (!scoped(this)) return nativeClear.call(this);
    const keys = [];
    for (let index = 0; index < this.length; index += 1) {{
      const value = nativeKey.call(this, index);
      if (value && value.startsWith(prefix)) keys.push(value);
    }}
    keys.forEach((value) => nativeRemoveItem.call(this, value));
  }};
}})();
</script>'''
    content = replace_or_insert_script(content, storage_id, storage_script)

    focus_id = f"{site_key}-basthon-focus"
    focus_script = f'''<script id="{focus_id}">
(() => {{
  "use strict";
  if (!new URLSearchParams(window.location.search).get("from")) return;
  let guardStartupFocus = true;
  const nativeFocus = HTMLElement.prototype.focus;
  HTMLElement.prototype.focus = function (options) {{
    if (!guardStartupFocus) return nativeFocus.call(this, options);
    const guarded = options && typeof options === "object" ? {{ ...options, preventScroll: true }} : {{ preventScroll: true }};
    return nativeFocus.call(this, guarded);
  }};
  const release = () => {{
    guardStartupFocus = false;
    window.removeEventListener("pointerdown", release, true);
    window.removeEventListener("touchstart", release, true);
    window.removeEventListener("keydown", release, true);
  }};
  window.addEventListener("pointerdown", release, true);
  window.addEventListener("touchstart", release, true);
  window.addEventListener("keydown", release, true);
}})();
</script>'''
    content = replace_or_insert_script(content, focus_id, focus_script)
    path.write_text(content, encoding="utf-8")


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: customize_basthon.py INDEX_HTML MAIN_JS")
    html_path = Path(sys.argv[1])
    javascript_path = Path(sys.argv[2])
    customize_javascript(javascript_path)
    customize_html(html_path, javascript_path)


if __name__ == "__main__":
    main()
