# EmDash

> Fork of [FeatherPad](https://github.com/tsujan/FeatherPad) by Pedram Pourang (Tsu Jan),
> packaged with the Newsk OS flavor by tir labs inc. GPL-3.0-or-later (see COPYING).
> Upstream credit: FeatherPad authors and translators.

## Overview

EmDash is a lightweight Qt plain-text/code editor for Linux (FeatherPad fork). It is independent of any desktop environment and has:

## EmDash additions (this fork)

- **Harper grammar check**: Edit → Check Grammar (Harper). Runs `emdash-harper`
  (bundled `harper-ls` v3.3.0, musl static) on the current file; output in the message dialog.
- **WordPress**: Edit → WordPress Publish Post / Browse Posts. Runs `emdash-wp`
  (stdlib-only Python, `WP_SITE` + `WP_USER` + `WP_APP_PASSWORD` env) via the WP REST API.
- **Newsk packaging**: `melange.yaml` + `apko.yaml` build the Newsk-flavored image
  (blocked on Wolfi providing `qt6-qtsvg`; editor itself needs no other new deps).

## Plugins & companions

- `tools/emdash-harper.sh` — Harper bridge (tested against harper-cli 3.3.0).
- `tools/emdash-wp.py` — WP REST client; `python3 tools/test_emdash_wp.py` (mock-server tested).

  * Drag-and-drop support, including tab detachment and attachment;
  * Workspace awareness under X11 and some Wayland compositors (using tabs on current desktop but opening a new window on another);
  * An optionally permanent search-bar with a different search entry for each tab;
  * Instant highlighting of found matches when searching;
  * A docked window for text replacement;
  * Support for showing line numbers and jumping to a specific line;
  * Optional selection highlighting;
  * Column selection;
  * Syntax highlighting for common programming languages;
  * Ability to open URLs with appropriate applications;
  * Session management;
  * Side-pane mode;
  * Auto-saving;
  * Spell checking with Hunspell;
  * Printing;
  * Text zooming;
  * Appropriate but non-interrupting prompts; and
  * Other features that can be found in its settings, on its menus or when it is actually used.

Please see [INSTALL](INSTALL) for instructions on compilation, installation and translation!

FeatherPad was written in GTK+ at first, then ported to Qt with more features. Its homepage is <https://github.com/tsujan/FeatherPad>.

## Credits

Haiku OS support is added by [khallebal at GitHub](https://github.com/khallebal).

macOS support is added by [Pavel Shliak](https://github.com/shlyakpavel).

OS/2 support is added by [josch1710 at GitHub](https://github.com/josch1710).

## Screenshots

The active Qt widget style determines the look and feel of every Qt application. The following screenshots are taken with a Kvantum theme and the dark color scheme of FeatherPad:

![Tabs](screenshots/Tabs.png?raw=true "Tabs")
![Side-Pane](screenshots/Side-Pane.png?raw=true "Side-Pane")
