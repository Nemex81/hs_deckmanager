# ocr-support-patch
patch di compatibilità pe rocr support, mod dedicata a crusader king 3

---
## Obiettivo

1. **OCR mode** sia completamente accessibile per non vedenti
2. **Vanilla mode** mantenga tutta la grafica e animazioni originali
3. **Componenti condivisi** siano gestiti in modo DRY (Don't Repeat Yourself)
4. **Nessun compromesso** venga fatto su nessuna delle due modalità

---

## STRUTTURA TUTTA NUOVA (dual mode)

**FILO CONDUTTORE**: un solo `window` con datamodel condivisi, **due modalità di rendering** (OCR e Vanilla) con types separati e datamodel identici.

```gui
window name="culturewindow" {
  widgetid="culturewindow"
  layer="windows_layer"
  movable=no
  using="base_ocr_window"
  
  ### DATACONTEXT COMUNI (definiti UNA SOLA VOLTA)
  datacontext="CultureWindow.GetCulture()"
  datacontext="Culture.GetReformation()"
  
  ### STATES COMUNI (definiti UNA SOLA VOLTA)
  state name="culture_refresh" { ... }
  state { ... }  # refresh fade in
  state name="show" { ... }    # era tabs vanilla
  state name="hide" { ... }    # era tabs vanilla
  
  ### === OCR MODE (Non Vedenti) === ###
  window_ocr visible="[Not(GetVariableSystem.Exists('ocr'))]" {
    blockoverride "ocr_header" { ... }
    blockoverride "ocr_content" {
      # Tabs hbox
      # Tab 1: Overview content
      # Tab 2: Innovations content
      # Tab 3: All Cultures content
      # Tab 4: Counties content
      # Tab 5: Rulers content
      # Culture head section
    }
  }
  
  ### === VANILLA MODE (Normovedenti) === ###
  margin_widget visible="[GetVariableSystem.Exists('ocr')]" {
    using="Window_Margins_Sidebar"
    # Header con watch button
    # Acceptance widget
    # Who's culture text
    # Tabs (Overview, Innovations)
    # Tab 1: Overview content (pillars grafici, traditions layered, buttons, culture head portrait)
    # Tab 2: Innovations content (era tabs visual, innovations grid grafiche)
  }
}
```

---

## REGOLE GENERALI

1. **UN SOLO window principale** (`culturewindow`) con datacontext/states condivisi
2. **Due modalità separate**:
   - **OCR mode**: visibile quando `Not(GetVariableSystem.Exists('ocr'))`
   - **Vanilla mode**: visibile quando `GetVariableSystem.Exists('ocr')`
3. **Stessi datamodel e stesse localization keys** in entrambe le modalità
4. **Types separati** per componenti con rendering diverso (suffix `_ocr`)
5. **Types condivisi** per componenti logici identici (progress bars, tooltip widgets)
6. **Tooltip unificati** e referenziati via `using=tooltip_name`
7. **Condizioni DLC identiche** in OCR e Vanilla (`HasDlcFeature(...)`)
8. **Nessuna duplicazione di datacontext/states** nei widget figli

---

## DATACONTEXT (definiti UNA SOLA VOLTA nel window principale)

```gui
datacontext="CultureWindow.GetCulture()"
datacontext="Culture.GetReformation()"
```

---

## TYPES

### TYPES OCR (solo per non vedenti)

- **vbox_era_tab_ocr**: layout tab era lineare (no texture grafiche)
- **containerpillaritemocr**: struttura testo-only per pillars (niente highlighticon)
- **flowcontainer_innovation**: lista innovazioni con rawtext e hotkeys

### TYPES VANILLA (grafica originale)

- **vbox_era_tab**: tabs con texture illustrate, animazioni show/hide
- **containerpillaritem**: pillar item con highlighticon 592x130, MaskRoughEdges, effects
- **iconinnovation**: icone 90x60 con shimmer, glow, exposure markers

### TYPES CONDIVISI

- **progressbar_reform**: usato sia in OCR che in Vanilla (stessa logica)
- **widget_tradition_icon**: 5 layers grafici (background, frame, highlight, glyph, glow)

---

## TOOLTIP (unici, usati da entrambe le modalità)

```gui
tooltipwidget = { using = culture_pillar_tooltip }
tooltipwidget = { using = culture_tradition_tooltip }
tooltipwidget = { using = culture_innovation_tooltip }
tooltipwidget = { using = culture_era_tooltip }
```

---

## DATAMODEL (stesso backend per entrambi)

Usare SEMPRE gli stessi metodi:

- `CultureWindow.GetCulture()`
- `CultureWindow.GetCultureEras()`
- `Culture.GetPillars()`
- `Culture.GetTraditions()`
- `Culture.GetTradition(index)`
- `Culture.GetInnovations()`
- `Culture.GetEraProgress()`
- `Culture.GetHeadOfCulture()`
- `CultureWindow.GetCultureInnovationsByEra(era)`
- `CultureWindow.GetInnovationFascination()`
- `Culture.GetInnovationProgress(inno)`
- `Culture.GetInnovationEra(inno)`
- `Culture.GetProgressTowardNextEra()`
- `CultureWindow.GetCultureAcceptance()`

---

## DLC CONDITIONS (identiche in OCR e Vanilla)

```gui
visible="[HasDlcFeature('diverge_culture')]"          # Diverge button/sections
visible="[HasDlcFeature('hybridize_culture')]"        # Hybridize button
visible="[HasDlcFeature('reform_culture')]"           # Reform button
visible="[HasDlcFeature('dlc_fp1_feature_martial_custom')]"  # Martial custom
visible="[HasDlcFeature('dlc_fp1_feature_court_language')]"  # Court language
visible="[HasDlcFeature('royal_court')]"              # Court language adopt

enabled="[Culture.IsHeadOfCulture()]"                 # Head-only actions
enabled="[HasDlcFeature('diverge_culture')]"          # Diverge action
enabled="[HasDlcFeature('hybridize_culture')]"        # Hybridize action
enabled="[HasDlcFeature('reform_culture')]"           # Reform action
enabled="[HasDlcFeature('royal_court')]"              # Court language
enabled="[HasDlcFeature('dlc_fp1_feature_martial_custom')]" # Martial custom
```

---

## LOCALIZATION (stesse keys)

- **Overview**: `CULTUREWINDOW_CULTURE`, `CULTURE_ACCEPTANCE_LABEL`, `WHOSE_CULTURE_LABEL`
- **Actions**: `REFORM_CULTURE_LABEL`, `DIVERGE_CULTURE_LABEL`, `HYBRIDIZE_CULTURE_LABEL`, `COURT_LANGUAGE_LABEL`, `MARTIAL_CUSTOM_LABEL`
- **Pillars/Traditions**: `PILLARS_LABEL`, `TRADITIONS_LABEL`, `ADD_TRADITION_LABEL`, `REPLACE_TRADITION_LABEL`
- **Innovations**: `INNOVATIONS_LABEL`, `FASCINATION_LABEL`, `ERA_PROGRESS_LABEL`
- **Tabs OCR**: rawtext espliciti per screen reader (Overview, Innovations, All cultures, Counties, Rulers)

---

## HOTKEYS (solo OCR mode)

- **Tab Overview**: Speed1
- **Tab Innovations**: Speed2
- **Tab All Cultures**: Speed3
- **Tab Counties**: Speed4
- **Tab Rulers**: Speed5

Hotkeys da aggiungere ai widget OCR per garantire navigazione tastiera completa.

---

## WIDGET STRUTTURA (OCR mode)

```gui
window_ocr {
  block "ocr_header" {
    vbox {
      text rawtext="CULTUREWINDOW_CULTURE"
      text rawtext="Culture.GetNameNoTooltip()"
      text rawtext="Culture.GetHeritage()"
      text rawtext="Culture.GetLanguage()"
      # acceptance, fascination, era progress, head of culture
    }
  }
  
  block "ocr_content" {
    hbox name="tabs" {
      button rawtext="Overview" hotkey="Speed1"
      button rawtext="Innovations" hotkey="Speed2"
      button rawtext="All Cultures" hotkey="Speed3"
      button rawtext="Counties" hotkey="Speed4"
      button rawtext="Rulers" hotkey="Speed5"
    }
    
    stackpanel {
      # tab panels (show/hide via scripted toggle)
    }
  }
}
```

---

## WIDGET STRUTTURA (Vanilla mode)

```gui
margin_widget {
  using="Window_Margins_Sidebar"
  
  block "header" {
    # culture name, acceptance, watch button, head portrait, buttons
  }
  
  block "tabs" {
    # Overview / Innovations tabs grafiche
  }
  
  block "overview" {
    # pillars highlighticon, traditions layered, buttons (reform/diverge/hybridize/etc.)
  }
  
  block "innovations" {
    # era tabs animated, innovation icons with shimmer/glow
  }
}
```

---

## ANIMAZIONI (Vanilla da preservare)

- **Shimmer** su `iconinnovation` (UV rotation 360°, durata 7s, loop)
- **Glow pulsing** per fascination (alpha 0.5 ↔ 0.8, ciclo 1s/1.6s)
- **FadeIn/FadeOut** standard su refresh (`AnimationRefreshFadeOut/AnimationRefreshFadeIn`)
- **Size transitions** per era tabs (135 ↔ 0)
- **Portrait effects** (shoulders, outlines)

---

## ESEMPIO DI DEFINIZIONE TYPES (estratto)

```gui
types OCR {
  type vbox_era_tab_ocr = {
    layoutpolicy_horizontal="expanding"
    layoutpolicy_vertical="fixed"
    size={ 100 30 }
    children = { text rawtext="CultureEra.GetName()" }
  }
  
  type containerpillaritemocr = {
    layoutpolicy_horizontal="expanding"
    layoutpolicy_vertical="fixed"
    size={ 600 70 }
    children = {
      text rawtext="Pillar.GetName()"
      text rawtext="Pillar.GetDescription()"
    }
  }
}

types CultureWindow {
  type vbox_era_tab = {
    size={ 135 70 }
    using="era_tab_illustrated"
    state name="show" { using="AnimationSizeExpand" }
    state name="hide" { using="AnimationSizeCollapse" }
  }
  
  type iconinnovation = {
    size={ 90 60 }
    using="InnovationIconVanilla"
    state name="shimmer" { ... }
    state name="pause" { ... }
  }
}
```

---

## DIVERGE vs HYBRIDIZE (condizioni identiche per OCR/Vanilla)

```gui
# Diverge
visible="[And(HasDlcFeature('diverge_culture'), Culture.IsHeadOfCulture())]"
enabled="[Culture.IsHeadOfCulture()]"

# Hybridize
visible="[And(HasDlcFeature('hybridize_culture'), HasDlcFeature('royal_court'))]"  # <-- esempio
enabled="[CultureWindow.CanHybridizeCulture()]"  # stesso metodo backend
```

---

## GETSCRIPTEDGUI (stessi in entrambe le modalità)

- `culture_closest_county_ocr`
- `culture_map_extents`
- `culture_select_fascination_window`
- `culture_reform_window`
- `culture_diverge_window`
- `culture_hybridize_window`
- `culture_adopt_court_language_window`

---

## BLOCCO ACCEPTANCE (stesso datamodel)

```gui
block name="acceptance" {
  datacontext="CultureWindow.GetCultureAcceptance()"
  # OCR: text rawtext, progressbar plain
  # Vanilla: progressbar grafica
}
```

---

## NOTE SU PILASTRI / TRADITIONS

- **Stesso datamodel**: `Culture.GetPillars()`, `Culture.GetTraditions()`
- **OCR**: niente texture, solo testo + rawtext descrittivo
- **Vanilla**: usare `containerpillaritem` con highlighticon e tradizione con 5 layers
- **Add/Replace tradition**: condizioni head + reformation identiche

---

## NOTE SU INNOVATIONS

- **Stesse funzioni**: `CultureWindow.GetCultureInnovationsByEra(era)`, `Culture.GetInnovationEra(inno)`
- **OCR**: flow container testo, hotkeys per selezione, tooltip con rawtext
- **Vanilla**: icone con shimmer/glow, era tabs animate, tooltip grafici
- **Fascination**: usare stesso datamodel `CultureWindow.GetInnovationFascination()`
- **Exposure**: marker blu come vanilla

---

## NOTE SU ERA PROGRESS

- `Culture.GetEraProgress()` + `Culture.GetProgressTowardNextEra()`
- **OCR**: progressbar semplice, testo
- **Vanilla**: progressbar grafica
- Stesse localization keys

---

## NOTE SU COURT LANGUAGE

- Condizioni DLC identiche
- OCR: button testo
- Vanilla: button grafico
- Usa sempre `CultureWindow.CanAdoptCourtLanguage()`

---

## NOTE SU REFORMATION

- Datacontext `Culture.GetReformation()`
- OCR: testo + buttons (add tradition, replace)
- Vanilla: modal windows grafici (reform/hybridize/diverge)
- Stessi scripted_gui per modal

---

## NOTE SU HYBRIDIZE

- `visible="[HasDlcFeature('hybridize_culture')]"` sia OCR che Vanilla
- Button enabled `[GetPlayer.GetCulture().CanHybridize()]`  # condizione unica
- Nessuna differenza di datamodel

---

## NOTE SU DIVERGE

- `visible="[HasDlcFeature('diverge_culture')]"` sia OCR che Vanilla
- Button enabled `[Culture.IsHeadOfCulture()]`
- Nessuna differenza di datamodel

---

## NOTE SU REFORM

- `visible="[HasDlcFeature('reform_culture')]"` sia OCR che Vanilla
- Button enabled `[Culture.IsHeadOfCulture()]`
- Nessuna differenza di datamodel

---

## SPOSTAMENTO DATACONTEXT/STATES (ordine corretto)

```gui
window name="culturewindow" {
  datacontext="CultureWindow.GetCulture()"
  datacontext="Culture.GetReformation()"
  
  state name="culture_refresh" { using="AnimationRefreshFadeOut" }
  state { using="AnimationRefreshFadeIn" }
  
  # solo Vanilla (era tabs)
  state name="show" { size={ 135 0 } duration=0.3 }
  state name="hide" { size={ 0 0 } duration=0.3 }
  
  # children...
}
```

---

## PATCH SPECIFICA (TESTO)

```gui
# Diverge / Hybridize buttons (OCR + Vanilla)
visible="[HasDlcFeature('diverge_culture')]"
enabled="[Culture.IsHeadOfCulture()]"  # head-only

visible="[HasDlcFeature('hybridize_culture')]"
enabled="[GetPlayer.GetCulture().CanHybridize()]"  # condizione unica
```

---

## NOTE SU SCRIPTED GUI E DLC

Usare **sempre** gli stessi `GetScriptedGui` in OCR e Vanilla:

```gui
button {
  using="button_diverge_culture"
  visible="[HasDlcFeature('diverge_culture')]"
  enabled="[Culture.IsHeadOfCulture()]"
  on_click="[GuiOpen(GetScriptedGui('culture_diverge_window'), { Culture.Self })]"
}
```

---

## ORDINE DEI BLOCCO / WIDGET

1. Datacontext e states nel window principale
2. Window OCR (header + tabs + contenuti)
3. Window Vanilla (header + tabs + contenuti)
4. Types OCR
5. Types Vanilla
6. Types condivisi
7. Templates condivisi
8. Tooltip widget

---

## CODE SNIPPET (abilitazioni corrette)

```gui
# CULTURE HEAD BUTTONS (OCR + Vanilla, stessi datamodel)
visible="[HasDlcFeature('reform_culture')]"
enabled="[Culture.IsHeadOfCulture()]"

visible="[HasDlcFeature('diverge_culture')]"
enabled="[Culture.IsHeadOfCulture()]"

visible="[HasDlcFeature('hybridize_culture')]"
enabled="[GetPlayer.GetCulture().CanHybridize()]"  # ← STESSA CONDIZIONE
```

---

## 6. STATI E ANIMAZIONI

```gui
# State condiviso per refresh
state name="culture_refresh" {
  using="AnimationRefreshFadeOut"
}
state {
  using="AnimationRefreshFadeIn"
}

# State per era tabs (solo Vanilla)
state name="show" {
  size={ 135 0 }
  duration=0.3
}

state name="hide" {
  size={ 0 0 }
  duration=0.3
}

# State shimmer per innovations (solo Vanilla)
state name="shimmer" {
  next="pause"
  trigger_on_create=yes
  duration=1.2
  trigger_when="[CultureInnovation.IsFascination()]"
  bezier={ 0 0.9 1 0.4 }
  
  modify_texture name="shimmer" {
    translate_uv={ -1 1 }
  }
}

state name="pause" {
  duration=0
  delay=5
  
  modify_texture name="shimmer" {
    translate_uv={ 1 -1 }
  }
}
```

---

## 7. TEMPLATES CONDIVISI

```gui
template agot_show_hybridize_culture = {
  visible="[And(Not(ObjectsEqual(Culture.GetHeritage(), GetPlayer.GetCulture().GetHeritage())), And(Not(GetPlayer.GetCulture().IsChildOf(Culture.Self)), Not(Culture.IsChildOf(GetPlayer.GetCulture()))))]"
}

template animation_culture_refresh = {
  state name="culture_refresh" {
    using="AnimationRefreshFadeOut"
  }
  state {
    using="AnimationRefreshFadeIn"
  }
}
```

---

## 8. STRUTTURA FILE FINALE

```gui
###############################################
# WINDOW CULTURE - DUAL MODE (OCR + VANILLA)
###############################################
# Repository: Nemex81/ocr-support-patch
# File: ocr-support/compatibility-pach/gui/window_culture.gui
# Last Modified: 2025-12-21

### === WINDOW PRINCIPALE === ###
window name="culturewindow" {
  widgetid="culturewindow"
  layer="windows_layer"
  movable=no
  using="base_ocr_window"
  
  # DATACONTEXT COMUNI (definiti UNA SOLA VOLTA)
  datacontext="CultureWindow.GetCulture()"
  datacontext="Culture.GetReformation()"
  
  # STATES COMUNI (definiti UNA SOLA VOLTA)
  state name="show" { ... }
  state name="hide" { ... }
  
  ### === MODALITÀ OCR (Non Vedenti) === ###
  window_ocr visible="[Not(GetVariableSystem.Exists('ocr'))]" {
    blockoverride "ocr_header" { ... }
    blockoverride "ocr_content" {
      # Tabs hbox
      # Tab 1: Overview content
      # Tab 2: Innovations content
      # Tab 3: All Cultures content
      # Tab 4: Counties content
      # Tab 5: Rulers content
      # Culture head section
    }
  }
  
  ### === MODALITÀ VANILLA (Normovedenti) === ###
  margin_widget visible="[GetVariableSystem.Exists('ocr')]" {
    using="Window_Margins_Sidebar"
    # Header con watch button
    # Acceptance widget
    # Who's culture text
    # Tabs (Overview, Innovations)
    # Tab 1: Overview content (pillars grafici, traditions layered, buttons, culture head portrait)
    # Tab 2: Innovations content (era tabs visual, innovations grid grafiche)
  }
}

### === TYPES OCR-SPECIFICI === ###
types OCR {
  type vbox_era_tab_ocr = { ... }
  type containerpillaritemocr = { ... }
  type flowcontainer_innovation = { ... }
}

### === TYPES VANILLA-SPECIFICI === ###
types CultureWindow {
  type vbox_era_tab = { ... }  # Con texture illustrations + animations
  type containerpillaritem = { ... }  # Con highlighticon 592x130 + effects
  type iconinnovation = { ... }  # Con shimmer + glow animations
}

### === TYPES CONDIVISI === ###
types CultureShared {
  type progressbar_reform = { ... }
  type widget_tradition_icon = { ... }  # 5 layers grafiche
}

### === TEMPLATES CONDIVISI === ###
template agot_show_hybridize_culture = { ... }
template animation_culture_refresh = { ... }

### === TOOLTIP WIDGETS CONDIVISI === ###
# (Opzionale: possono essere in file separato)
tooltipwidget = { using = culture_pillar_tooltip }
tooltipwidget = { using = culture_tradition_tooltip }
tooltipwidget = { using = culture_innovation_tooltip }
tooltipwidget = { using = culture_era_tooltip }
```

---

## 9. CRITERI DI SUCCESSO

### ✅ OCR Mode (Non Vedenti)
- [ ] Tutte e 5 le tabs funzionanti con hotkeys Speed1-5
- [ ] Navigation completa tramite tastiera (Tab, Enter, hotkeys)
- [ ] Screen reader può leggere **tutto** il contenuto sequenzialmente
- [ ] Tutti i button hanno `rawtext` espliciti e descrittivi
- [ ] Sorting e filtering funzionanti con feedback vocale
- [ ] Nessuna texture/icon decorativa inutile
- [ ] Layout lineare (vbox/hbox) senza complessità visive
- [ ] Tooltip letti correttamente da screen reader

### ✅ Vanilla Mode (Normovedenti)
- [ ] **TUTTA** la grafica originale mantenuta:
  - [ ] Pillar highlighticon 592x130px con MaskRoughEdges
  - [ ] Innovation iconinnovation 90x60px con shimmer effect
  - [ ] Tradition widget_tradition_icon con 5 layers grafiche
  - [ ] Era tab texture illustrations con fade animations
  - [ ] Portrait shoulders per culture head
  - [ ] Glow effects per fascination (alpha 0.5 ↔ 0.8)
  - [ ] Exposure markers blu
  - [ ] Progress bar grafiche
  - [ ] Coat of arms
- [ ] **TUTTE** le animazioni funzionanti:
  - [ ] Shimmer effect (UV rotation 360°, 7s loop)
  - [ ] Glow pulsing (1s + 1.6s cycle)
  - [ ] Fade in/out (AnimationFadeInStandard/FadeOut)
  - [ ] Size transitions (era tabs 135↔0)
  - [ ] State animations (culture_refresh)
- [ ] **TUTTE** le interazioni funzionanti:
  - [ ] Hover effects
  - [ ] Click areas ottimizzate
  - [ ] Tooltip grafici ricchi
  - [ ] Modal windows (reform, diverge, hybridize)
  - [ ] Visual feedback immediato

### ✅ Entrambe le Modalità
- [ ] **Stessi datamodel** (CultureWindow.GetCultureEras(), Culture.GetTraditions(), etc.)
- [ ] **Stessi tooltip widget** (culture_pillar_tooltip, culture_innovation_tooltip, etc.)
- [ ] **Stesse funzionalità**:
  - [ ] Reform culture (se culture head + DLC)
  - [ ] Hybridize culture (se DLC + condizioni)
  - [ ] Diverge culture (se player culture + DLC)
  - [ ] Add tradition (se culture head)
  - [ ] Select fascination (se culture head)
  - [ ] Replace tradition (se reformation mode)
  - [ ] Adopt court language (se DLC royalcourt)
- [ ] **Nessun crash** o elemento mancante
- [ ] **Proper conditional visibility** per DLC features:
  - [ ] `HasDlcFeature('diverge_culture')`
  - [ ] `HasDlcFeature('hybridize_culture')`
  - [ ] `HasDlcFeature('reform_culture')`
  - [ ] `HasDlcFeature('dlc_fp1_feature_martial_custom')`
  - [ ] `HasDlcFeature('dlc_fp1_feature_court_language')`
  - [ ] `HasDlcFeature('royal_court')`
- [ ] **Stesse localization keys** (CULTUREWINDOW_CULTURE, REFORM_CULTURE_LABEL, etc.)
- [ ] **Stessi scripted_gui** (culture_closest_county_ocr, culture_map_extents, etc.)

---

## 10. ISTRUZIONI SPECIFICHE PER L'AGENTE GITHUB

### ✅ DA FARE

1. **Definire datacontext/states nel window principale** prima di qualsiasi widget figlio
2. **Creare types SEPARATI** per OCR e Vanilla quando rendering è diverso
3. **Creare types CONDIVISI** per componenti logici identici (progressbar_reform)
4. **Usare gli STESSI datamodel** in entrambe le modalità (no duplicazioni)
5. **Usare le STESSE localization keys** in entrambe le modalità
6. **Sincronizzare TUTTE le condizioni DLC** (visible/enabled identiche)
7. **Referenziare tooltip UNA SOLA VOLTA** tramite `using=tooltip_name`
8. **Usare blockoverride** per variazioni minime di componenti simili
9. **Mantenere GetScriptedGui IDENTICI** in entrambe le modalità
10. **Commentare CHIARAMENTE** ogni sezione (OCR vs Vanilla vs Condiviso)
11. **Preservare TUTTA la grafica Vanilla** (texture, alpha, tint, effects)
12. **Preservare TUTTE le animazioni Vanilla** (shimmer, glow, fade, transitions)
13. **Testare SEPARATAMENTE** OCR mode (senza `ocr` var) e Vanilla mode (con `ocr` var)

### ❌ DA NON FARE

1. ❌ **NON duplicare datacontext** nei widget figli
2. ❌ **NON ridefinire lo stesso type** due volte (OCR e Vanilla devono avere nomi diversi)
3. ❌ **NON usare datamodel diversi** per gli stessi dati backend
4. ❌ **NON creare tooltip separati** se il contenuto è identico
5. ❌ **NON hardcodare valori** che dovrebbero venire dal backend
6. ❌ **NON usare localization keys diverse** per lo stesso concetto
7. ❌ **NON duplicare states/animations** identici
8. ❌ **NON creare condizioni DLC diverse** tra OCR e Vanilla
9. ❌ **NON semplificare la grafica Vanilla** per "coerenza" con OCR
10. ❌ **NON rimuovere animazioni Vanilla** perché "non necessarie"
11. ❌ **NON usare lo stesso type** per rendering completamente diversi
12. ❌ **NON mescolare logica OCR e Vanilla** nello stesso widget (separare completamente)

---

## 11. CHECKLIST FINALE PRE-COMMIT

Prima di creare il commit, verificare:

- [ ] Window principale ha datacontext/states definiti UNA VOLTA
- [ ] OCR mode ha types separati (suffix `_ocr`)
- [ ] Vanilla mode ha types separati (no suffix o suffix vanilla-specific)
- [ ] Types condivisi sono in `types CultureShared`
- [ ] Tooltip sono definiti UNA VOLTA e referenziati da entrambi
- [ ] Datamodel sono identici in OCR e Vanilla
- [ ] Localization keys sono identiche in OCR e Vanilla
- [ ] DLC conditions sono identiche in OCR e Vanilla
- [ ] Scripted_gui calls sono identici in OCR e Vanilla
- [ ] OCR mode è completamente funzionale senza `ocr` var
- [ ] Vanilla mode è completamente funzionale con `ocr` var
- [ ] Tutte le texture Vanilla sono presenti
- [ ] Tutte le animazioni Vanilla funzionano
- [ ] Tutti i tooltip sono accessibili
- [ ] Nessun elemento duplicato inutilmente
- [ ] File è commentato chiaramente
- [ ] Codice è validato sintatticamente

---

Questo piano completo e dettagliato fornisce all'agente GitHub **tutte le informazioni necessarie** per implementare un sistema dual-mode perfetto, garantendo che:

1. **OCR mode** sia completamente accessibile per non vedenti
2. **Vanilla mode** mantenga tutta la grafica e animazioni originali
3. **Componenti condivisi** siano gestiti in modo DRY (Don't Repeat Yourself)
4. **Nessun compromesso** venga fatto su nessuna delle due modalità
