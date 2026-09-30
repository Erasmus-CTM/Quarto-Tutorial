-- Seitentitel je Sprache.
-- Der deutsche Wert steht in `title:` (und `subtitle:`, `description:`). Für die anderen
-- Sprachen gibt es `title-en:`, `title-sv:`, `title-no:`, `title-da:` usw. Im Lauf einer
-- Sprache ersetzt das passende Feld den deutschen Wert; alle -xx-Felder werden danach
-- entfernt. So bleibt pro Seite eine einzige .qmd-Datei für alle Sprachen.
local KUERZEL = { english = "en", svenska = "sv", norsk = "no", dansk = "da" }

local function sprache()
  local profile = os.getenv("QUARTO_PROFILE") or ""
  for p in profile:gmatch("[^,%s]+") do
    if KUERZEL[p] then return KUERZEL[p] end
  end
  return nil
end

local felder = { "title", "subtitle", "description" }

function Meta(meta)
  local kurz = sprache()
  for _, feld in ipairs(felder) do
    if kurz and meta[feld .. "-" .. kurz] ~= nil then
      meta[feld] = meta[feld .. "-" .. kurz]
    end
    for _, k in pairs(KUERZEL) do
      meta[feld .. "-" .. k] = nil
    end
  end
  return meta
end
