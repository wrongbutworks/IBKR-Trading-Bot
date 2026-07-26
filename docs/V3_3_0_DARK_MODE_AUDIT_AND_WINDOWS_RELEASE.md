# v3.3.0 Fusion dark mode, audit layout, and Windows release packaging

**Release:** v3.3.0

**Release date:** 2026-07-26
**Type:** GUI presentation, Windows packaging, documentation, and release maintenance

## Summary

v3.3.0 adds an operating-system-aware light/dark appearance with an explicit
**View** menu override, corrects the About-logo layout, makes the Cycle Audit
Timeline tables use the available width, keeps Market capture inside one tab
viewport, and simplifies the portable Windows release root. The strategy state
machine, order construction, risk controls, broker reconciliation, SQLite
schema, session handling, execution accounting, and persisted settings are
unchanged.

## Automatic and selectable Fusion themes

At startup, BouncyBot reads Qt's current operating-system color scheme before it
installs the application palette. A light or dark Fusion palette and matching
application stylesheet are then applied automatically. On supported Qt/Windows
versions, a running application also follows subsequent system light/dark mode
changes through `QStyleHints.colorSchemeChanged`; no restart or persisted user
setting is required.

The menu bar now places **View** between **File** and **About**. **View > Light
mode** and **View > Dark mode** immediately switch the running application, and
their check marks track the active appearance. A manual choice lasts for the
current process; a later operating-system theme notification can select the new
system appearance again.

The dark appearance now uses neutral Qt Fusion-style greys rather than the
earlier navy/slate palette. It covers ordinary Qt controls, menus, tabs, dialogs,
tables, scrollbars, state cards, status pills, and command cards. The
custom-painted Cycle Timeline, Profit Guard, strategy graph, and strategy
flowchart select matching neutral surfaces, grid lines, labels, semantic state
colors, and hover cards at paint time. Semantic meanings are retained: green
remains successful, blue active, amber waiting/caution, and red blocked/risk.

The current system color scheme is presentation-only. It is not persisted in
SQLite and cannot change a strategy decision, order, quantity, price, or risk
calculation.

## About screen logo

The About dialog now places the scaled logo in a dedicated fixed-height panel.
The outer vertical layout reserves that complete panel before positioning the
title, version, and repository link. The logo is also bounded to a smaller
high-DPI-safe size, so the title text cannot overlap the artwork and the lower
edge remains visible when the support fields and notice are laid out below it.

## Cycle Audit Timeline tables

The stage-transition and guard/risk tables retain bounded content widths for
timestamps, stages, event types, and results. Each table now expands across its
assigned share of the Timeline tab, while its message column stretches into the
remaining space. The transition table receives three-fifths of the row and the
guard/risk table two-fifths.

At a normal maximized application width, both tables therefore use the complete
horizontal viewport and ordinary audit content should not require horizontal
scrollbars. Narrow windows and unusually long values still retain conditional
horizontal scrolling and full-value tooltips.

## Cycle Audit Market capture tab

The Market capture tab no longer wraps its complete contents in a vertically
scrolling main-page container. The metadata table, captured-row preview, and
capture-file list are laid out directly inside the tab. Each data box owns its
vertical scrollbar and a bounded height, so the tab itself fits the Cycle Audit
window and the outer right-edge scrollbar is removed.

## Windows release layout

The Windows build continues to use a PyInstaller one-directory bundle under
`GUI/`. Only the runtime application icon and About-screen logo are supplied to
PyInstaller. The complete source `Images/` directory, which also contains README
screenshots and documentation artwork, is no longer copied to the root of the
portable Windows release.

The release root now contains `BouncyBot.lnk`, which launches
`GUI\IBKRTradingBot.exe`. The shortcut stores the GUI path as a relative fallback
in addition to its initial absolute build path, so moving the complete extracted
release directory does not strand the shortcut. `QUICK_START.txt` documents both
the shortcut and the direct executable path. The build verifies that the runtime
icon and logo are present somewhere inside the packaged GUI folder and that no
top-level `Images/` directory was added.

The repository and source release retain the complete `Images/` directory so
README image links and documentation screenshots continue to work on GitHub.

## Documentation structure

The v3.2.2 release note has moved to `docs/legacy/`. This v3.3.0 note is the only
release-specific document in the root of `docs/`. Current guides and release
metadata now identify v3.3.0 while the archived v3.2.2 note remains unchanged as
a record of that release.

## Compatibility

v3.3.0 adds no SQLite table, column, index, data migration, or persisted setting.
Existing v3.2.2 portable databases, settings, active cycles, orders, executions,
audit events, backups, exports, and market-capture files remain compatible.

There is no trading-algorithm, broker-order, recovery, account-scope, currency,
commission, session, reconnect, or P/L behavior change in this release.

## Verification

Focused regressions cover:

- light and dark application palette roles;
- automatic startup detection and live system-theme signal handling;
- manual **View > Light mode / Dark mode** switching and action-state sync;
- neutral Fusion-dark stylesheet conversion and theme-aware custom-painted views;
- refresh of cached state cards when the theme changes;
- dedicated About-logo panel sizing and non-overlapping title placement;
- bounded Timeline columns, full-width table allocation, and stretched message columns;
- Market capture internal scrollbars without an outer tab scrollbar;
- continued PyInstaller inclusion of the two runtime image assets;
- omission of the source `Images/` directory from the Windows release root;
- release-root shortcut creation and checksum inclusion; and
- v3.3.0 metadata, documentation placement, and backward compatibility.

Final repository gate results are recorded in `IMPLEMENTATION_TEST_REPORT.txt`.
The Windows executable itself must be assembled on Windows with
`build_windows.bat` because PyInstaller produces platform-specific binaries.
