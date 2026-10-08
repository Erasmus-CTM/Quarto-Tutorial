-- Page title per language.
-- The German value is in `title:` (and `subtitle:`, `description:`). For the other
-- languages there are `title-en:`, `title-sv:`, `title-no:`, `title-da:` etc. In the run
-- of a language the matching field replaces the German value; all -xx fields are removed
-- afterwards. This keeps a single .qmd file per page for all languages.
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
