#!/usr/bin/env Rscript
# =============================================================================
# Scientific Color Palettes — R version
# Curated for ggplot2 + ggsci publication-quality figures.
#
# Sources:
#   Okabe-Ito (2008), Paul Tol (2021), NPG, NEJM, Lancet, JAMA, JCO, AAAS,
#   Crameri scientific colour maps, Viridis family
#
# Usage:
#   source("style/color_palettes.R")
#   pal <- get_pal("npg")                  # named character vector
#   use_pal("okabe_ito")                   # set ggplot2 default palette
#   use_pal("nejm", 4)                     # first 4 colors of NEJM
#   scale_color_pal("lancet")              # ggplot2 scale (manual)
#   scale_fill_pal("lancet")               # ggplot2 fill scale
#   list_pals()                             # print all available
#
# Integration with ggsci:
#   ggsci provides scale_color_npg(), scale_color_nejm(), etc.
#   This file supplements with palettes ggsci lacks:
#   okabe_ito, tol_bright/vibrant/muted, volcano, apa, survival, etc.
#   For ggsci palettes, prefer ggsci scales directly.
# =============================================================================

# --- Qualitative Palettes (named vectors) ---
.QUAL_PALS <- list(
  okabe_ito = c(
    orange        = "#E69F00",
    sky_blue      = "#56B4E9",
    bluish_green  = "#009E73",
    yellow        = "#F0E442",
    blue          = "#0072B2",
    vermillion    = "#D55E00",
    reddish_purple = "#CC79A7",
    black         = "#000000"
  ),
  tol_bright = c(
    blue    = "#4477AA",
    cyan    = "#66CCEE",
    green   = "#228833",
    yellow  = "#CCBB44",
    red     = "#EE6677",
    purple  = "#AA3377",
    grey    = "#BBBBBB"
  ),
  tol_vibrant = c(
    blue   = "#0077BB",
    cyan   = "#33BBEE",
    teal   = "#009988",
    green  = "#EE7733",
    red    = "#CC3311",
    purple = "#EE3377",
    grey   = "#BBBBBB"
  ),
  tol_muted = c(
    indigo   = "#332288",
    cyan     = "#88CCEE",
    teal     = "#44AA99",
    green    = "#117733",
    yellow   = "#999933",
    gold     = "#DDCC77",
    red      = "#CC6677",
    purple   = "#882255",
    pink     = "#AA4499"
  ),
  tol_highcontrast = c(
    blue   = "#004488",
    cyan   = "#009988",
    red    = "#BB3311",
    yellow = "#DDAA33"
  ),
  npg = c(
    red1     = "#E64B35",
    blue1    = "#4DBBD5",
    green1   = "#00A087",
    blue2    = "#3C5488",
    orange   = "#F39B7F",
    purple   = "#8491B8",
    cyan2    = "#91D1C2",
    red2     = "#DC0000",
    brown    = "#7E6148",
    tan      = "#B09C85"
  ),
  nejm = c(
    red       = "#BC3C29",
    blue      = "#0072B5",
    orange    = "#E18727",
    green     = "#20854E",
    purple    = "#7876B1",
    grey_blue = "#6F99AD",
    yellow    = "#FFDC91",
    pink      = "#EE4C97"
  ),
  lancet = c(
    blue   = "#00468B",
    red    = "#ED0000",
    green  = "#42B540",
    cyan   = "#0099B5",
    purple = "#925E9F",
    salmon = "#FDAF91",
    maroon = "#AD002A",
    grey   = "#ADB6B6"
  ),
  jama = c(
    dark_blue  = "#374E55",
    orange     = "#DF8D5B",
    navy       = "#003B5C",
    brown      = "#B6370E",
    light_blue = "#56B3E0",
    teal       = "#00A087"
  ),
  jco = c(
    blue   = "#0073A8",
    orange = "#E08B28",
    maroon = "#A0244D",
    cyan   = "#56B3E0",
    navy   = "#3C5488",
    green  = "#91D1C2",
    red    = "#DC0000",
    brown  = "#7E6148"
  ),
  aaas = c(
    blue   = "#3B4CC0",
    red    = "#B40426",
    orange = "#E7CC6D",
    green  = "#95C7BA",
    purple = "#8595D4",
    cyan   = "#4FA5D4",
    grey   = "#8C8C8C"
  )
)

# --- Genomics Palettes (named vectors) ---
.GENOMICS_PALS <- list(
  volcano_up_down_ns = c(
    up = "#D55E00",
    down = "#0072B2",
    ns = "#BBBBBB"
  ),
  apa_pattern = c(
    proximal = "#E64B35",
    distal = "#4DBBD5",
    no_change = "#8491B8"
  ),
  survival_km = c(
    high = "#D55E00",
    low = "#0072B2",
    censored = "#BBBBBB"
  ),
  gwas_manhattan = c(
    chr_odd = "#4477AA",
    chr_even = "#EE6677",
    significant = "#D55E00",
    suggestive = "#CCBB44"
  ),
  fluorophore_cvd = c(
    dapi_blue   = "#0072B2",
    fitc_green  = "#009E73",
    tritc_red   = "#D55E00",
    cy5_far_red = "#8491B8"
  ),
  dna_bases = c(
    A = "#4DBBD5",
    T = "#E64B35",
    G = "#00A087",
    C = "#8491B8"
  )
)

# --- Project-Level Palettes (domain-specific) ---
.PROJECT_PALS <- list(
  lifespan_apa = c(
    Fetal      = "#4DBBD5",
    Neonatal   = "#00A087",
    Child      = "#3C5488",
    Adolescent = "#F39B7F",
    Adult      = "#E64B35",
    Aged       = "#8491B4"
  ),
  neuro_disease = c(
    Control = "#3C5488",
    MDD     = "#E64B35",
    SCZ     = "#4DBBD5",
    BD      = "#00A087",
    ASD     = "#F39B7F"
  )
)

# --- Sequential & Diverging cmaps (for scale_fill_distiller etc.) ---
.CMAPS <- c(
  # Perceptually uniform sequential
  "viridis", "magma", "inferno", "plasma", "cividis",
  # Crameri CVD-safe
  "batlow", "devon", "lapaz", "hawaii", "glasbey",
  # Crameri CVD-safe diverging
  "roma", "vik", "broc", "cork",
  # Classic diverging
  "RdYlBu", "PuOr",
  # Tol diverging
  "sunset", "burd"
)

# =============================================================================
# API functions
# =============================================================================

#' Get a palette as a named character vector
#' @param name Palette name (e.g., "okabe_ito", "npg", "volcano_up_down_ns")
#' @return Named character vector of hex colors
get_pal <- function(name) {
  all_pals <- c(.QUAL_PALS, .GENOMICS_PALS, .PROJECT_PALS)
  if (!(name %in% names(all_pals))) {
    stop("Unknown palette: '", name, "'. Use list_pals() to see available options.")
  }
  all_pals[[name]]
}

#' Get unnamed color vector (for ggplot2 positions)
#' @param name Palette name
#' @param n Number of colors (NULL = all)
#' @return Unnamed character vector
get_pal_colors <- function(name, n = NULL) {
  pal <- get_pal(name)
  if (!is.null(n) && n <= length(pal)) {
    pal <- pal[1:n]
  }
  unname(pal)
}

#' Set ggplot2 default color/fill palette
#' Updates ggplot2::theme()'s angular color list for the current session
#' @param name Palette name
#' @param n Number of colors to use (NULL = all)
use_pal <- function(name, n = NULL) {
  colors <- get_pal_colors(name, n)
  # Override the default color cycle
  options(ggplot2.discrete.colour = colors)
  options(ggplot2.discrete.fill = colors)
  # Also set palette() for base R
  grDevices::palette(colors)
  invisible(colors)
}

#' Create a ggplot2 manual color scale
#' @param name Palette name
#' @return ggplot2 Scale object
scale_color_pal <- function(name) {
  colors <- get_pal(name)
  ggplot2::scale_color_manual(values = colors)
}

#' Create a ggplot2 manual fill scale
#' @param name Palette name
#' @return ggplot2 Scale object
scale_fill_pal <- function(name) {
  colors <- get_pal(name)
  ggplot2::scale_fill_manual(values = colors)
}

#' List all available palettes
list_pals <- function() {
  cat("=== Qualitative Palettes ===\n")
  for (nm in names(.QUAL_PALS)) {
    pal <- .QUAL_PALS[[nm]]
    cat(sprintf("  %-18s %2d colors  %s\n", nm, length(pal),
                ifelse(attr(pal, "cvd_safe") %in% TRUE, "CVD-safe", "")))
  }
  cat("\n=== Genomics Palettes ===\n")
  for (nm in names(.GENOMICS_PALS)) {
    pal <- .GENOMICS_PALS[[nm]]
    cat(sprintf("  %-18s %2d colors\n", nm, length(pal)))
  }
  cat("\n=== Project Palettes ===\n")
  for (nm in names(.PROJECT_PALS)) {
    pal <- .PROJECT_PALS[[nm]]
    cat(sprintf("  %-18s %2d colors  %s\n", nm, length(pal), paste(names(pal), collapse = ", ")))
  }
  cat("\n=== Sequential/Diverging cmaps ===\n")
  cat(paste(" ", .CMAPS), "\n")
  cat("\nTip: get_pal('npg'), use_pal('okabe_ito'), scale_color_pal('lancet')\n")
}

#' Convenience: apply project palette and return for direct use
#' @param project Project name ("lifespan_apa", "neuro_disease")
#' @return Named color vector
project_colors <- function(project = "lifespan_apa") {
  get_pal(project)
}

# =============================================================================
# CVD-safe annotations (for reference/printing)
# =============================================================================
.CVD_SAFE <- c("okabe_ito", "tol_bright", "tol_vibrant", "tol_muted",
               "tol_highcontrast", "nejm", "lancet", "jama")

#' Check if a palette is CVD-safe
is_cvd_safe <- function(name) {
  name %in% .CVD_SAFE
}