#' Base Plot Utilities
#'
#' Global plotting style for viz-skills R templates. All figure templates should
#' source this file and use `theme_sci()` plus `save_figure()` / `save_demo()`.

suppressPackageStartupMessages({
  library(ggplot2)
})

`%||%` <- function(x, y) if (is.null(x) || length(x) == 0) y else x

VIZ_PALETTES <- list(
  nature = c("#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4", "#91D1C2", "#DC0000"),
  safe = c("#4477AA", "#EE6677", "#228833", "#CCBB44", "#66CCEE", "#AA3377"),
  two_group = c("#4575B4", "#D73027"),
  disease = c(Control = "#3C5488", MDD = "#E64B35", SCZ = "#4DBBD5", BD = "#00A087", ASD = "#F39B7F"),
  lifespan = c(Fetal = "#4DBBD5", Neonatal = "#00A087", Child = "#3C5488", Adolescent = "#F39B7F", Adult = "#E64B35", Aged = "#8491B4")
)

NATURE_COLORS <- VIZ_PALETTES$nature
SAFE_COLORS <- VIZ_PALETTES$safe
TWO_GROUP_COLORS <- VIZ_PALETTES$two_group

script_path <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- sub("^--file=", "", args[grepl("^--file=", args)])
  if (length(file_arg) > 0) normalizePath(file_arg[1]) else normalizePath(getwd())
}

template_root_dir <- function() dirname(dirname(script_path()))

template_out_dir <- function() file.path(template_root_dir(), "demo_fig")

preset_spec <- function(preset = "publication") {
  switch(
    preset,
    publication = list(base_size = 16, width = 85, height = 72, units = "mm", dpi = 300),
    presentation = list(base_size = 16, width = 9, height = 4.5, units = "in", dpi = 200),
    poster = list(base_size = 24, width = 12, height = 9, units = "in", dpi = 300),
    draft = list(base_size = 16, width = 7, height = 5, units = "in", dpi = 120),
    list(base_size = 16, width = 85, height = 72, units = "mm", dpi = 300)
  )
}

theme_sci <- function(base_size = 16, base_family = "Arial", grid = FALSE) {
  th <- theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      axis.line = element_line(linewidth = 0.35, colour = "grey25"),
      axis.ticks = element_line(linewidth = 0.3, colour = "grey25"),
      axis.text = element_text(colour = "grey25"),
      legend.title = element_blank(),
      legend.key.height = unit(8, "pt"),
      legend.key.width = unit(10, "pt"),
      plot.title = element_blank(),
      plot.subtitle = element_blank(),
      plot.margin = margin(5, 6, 5, 5, "pt")
    )

  if (grid) {
    th <- th + theme(
      panel.grid.major = element_line(colour = "grey90", linewidth = 0.25),
      panel.grid.minor = element_blank()
    )
  }
  th
}

# Backward-compatible alias for first-pass templates.
theme_clean <- theme_sci

save_figure <- function(plot, name, out_dir = ".", width = 85, height = 72,
                        units = "mm", dpi = 300, bg = "white",
                        pdf = TRUE, png = TRUE) {
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  paths <- c()
  if (pdf) {
    pdf_path <- file.path(out_dir, paste0(name, ".pdf"))
    ggsave(pdf_path, plot, width = width, height = height, units = units,
           dpi = dpi, device = cairo_pdf, bg = bg)
    paths <- c(paths, pdf = pdf_path)
  }
  if (png) {
    png_path <- file.path(out_dir, paste0(name, ".png"))
    ggsave(png_path, plot, width = width, height = height, units = units,
           dpi = dpi, bg = bg)
    paths <- c(paths, png = png_path)
  }
  invisible(paths)
}

save_demo <- function(plot, name, out_dir = template_out_dir(), width = 85,
                      height = 72, units = "mm", dpi = 300, bg = "white") {
  save_figure(plot, name = name, out_dir = out_dir, width = width,
              height = height, units = units, dpi = dpi, bg = bg)
}
