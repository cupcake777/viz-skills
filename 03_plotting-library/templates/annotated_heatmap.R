#' Clustered Annotated Heatmap (pheatmap)
#'
#' Clustered heatmap with row and column annotation bars using the pheatmap
#' package. Row annotation shows pathway membership; column annotation shows
#' experimental condition and developmental stage. Useful for gene expression
#' matrices, proteomics, or any tabular omics data with sample/gene metadata.
#'
#' pheatmap returns a gtable (not ggplot), so saving uses direct pdf()/png()
#' device calls instead of ggsave.
#'
#' Input:
#'   mat       - numeric matrix (genes x samples) with rownames/colnames
#'   row_ann   - data.frame rownames=rownames(mat), columns are annotation factors
#'   col_ann   - data.frame rownames=colnames(mat), columns are annotation factors

suppressPackageStartupMessages({
  library(pheatmap)
  library(RColorBrewer)
})

# ---------- source base_plot.R for helpers ----------
source(file.path(dirname(normalizePath(sub(
  "^--file=", "",
  commandArgs(FALSE)[grepl("^--file=", commandArgs(FALSE))]
)[1])), "base_plot.R"))

# ============================================================
#  Mock data generator
# ============================================================
generate_mock_data <- function(n_genes = 15, n_samples = 8, seed = 42) {
  set.seed(seed)

  genes  <- paste0("Gene_", sprintf("%02d", seq_len(n_genes)))
  samples <- paste0("Sample_", LETTERS[seq_len(n_samples)])

  # Build expression matrix with three coherent gene clusters
  mat <- matrix(rnorm(n_genes * n_samples, mean = 0, sd = 1),
                nrow = n_genes, ncol = n_samples,
                dimnames = list(genes, samples))

  # Cluster 1 (genes 1-5): upregulated in samples A-D
  mat[1:5, 1:4] <- mat[1:5, 1:4] + 2.0
  # Cluster 2 (genes 6-10): upregulated in samples E-H
  mat[6:10, 5:8] <- mat[6:10, 5:8] + 2.0
  # Cluster 3 (genes 11-15): upregulated in condition B samples
  mat[11:15, c(2, 4, 6, 8)] <- mat[11:15, c(2, 4, 6, 8)] + 1.5

  # Row annotation: pathway membership
  pathways <- c(
    rep("Apoptosis",   5),
    rep("Cell_Cycle",  5),
    rep("Signaling",   5)
  )
  row_ann <- data.frame(
    Pathway = factor(pathways, levels = c("Apoptosis", "Cell_Cycle", "Signaling")),
    row.names = genes
  )

  # Column annotation: condition + stage
  conditions <- c("Control", "Control", "Treated", "Treated",
                   "Control", "Control", "Treated", "Treated")
  stages     <- c("Early",   "Late",    "Early",   "Late",
                   "Early",   "Late",    "Early",   "Late")
  col_ann <- data.frame(
    Condition = factor(conditions, levels = c("Control", "Treated")),
    Stage     = factor(stages,     levels = c("Early", "Late")),
    row.names = samples
  )

  list(mat = mat, row_ann = row_ann, col_ann = col_ann)
}

# ============================================================
#  Annotation colour maps
# ============================================================
make_annotation_colors <- function(row_ann, col_ann) {
  # Row annotation colours
  row_colors <- list()
  if ("Pathway" %in% names(row_ann)) {
    row_colors$Pathway <- c(
      Apoptosis = "#E64B35",
      Cell_Cycle = "#4DBBD5",
      Signaling  = "#00A087"
    )
  }

  # Column annotation colours
  col_colors <- list()
  if ("Condition" %in% names(col_ann)) {
    col_colors$Condition <- c(Control = "#3C5488", Treated = "#E64B35")
  }
  if ("Stage" %in% names(col_ann)) {
    col_colors$Stage <- c(Early = "#F39B7F", Late = "#8491B4")
  }

  c(row_colors, col_colors)
}

# ============================================================
#  Plot function
# ============================================================
annotated_heatmap <- function(mat,
                              row_ann = NULL,
                              col_ann = NULL,
                              scale = "row",
                              clustering_method = "complete",
                              clustering_distance_rows = "euclidean",
                              clustering_distance_cols = "euclidean",
                              cluster_rows = TRUE,
                              cluster_cols = TRUE,
                              show_rownames = TRUE,
                              show_colnames = TRUE,
                              fontsize = 10,
                              fontsize_row = 8,
                              fontsize_col = 9,
                              color_palette = NULL,
                              breaks = NULL,
                              annotation_colors = NULL,
                              border_color = "grey80",
                              cellwidth = 20,
                              cellheight = 14,
                              main = "Annotated Clustered Heatmap",
                              silent = TRUE) {

  # Default diverging palette (RdBu, 99 steps)
  if (is.null(color_palette)) {
    color_palette <- colorRampPalette(rev(brewer.pal(11, "RdBu")))(99)
  }
  if (is.null(breaks)) {
    breaks <- seq(-2, 2, length.out = 100)
  }

  # Build annotation colour map if not supplied
  if (is.null(annotation_colors) && !is.null(row_ann) && !is.null(col_ann)) {
    annotation_colors <- make_annotation_colors(row_ann, col_ann)
  }

  # Draw pheatmap (returns a list with gtable in $gtable)
  ph <- pheatmap(
    mat,
    scale               = scale,
    clustering_method    = clustering_method,
    clustering_distance_rows = clustering_distance_rows,
    clustering_distance_cols = clustering_distance_cols,
    cluster_rows         = cluster_rows,
    cluster_cols         = cluster_cols,
    show_rownames        = show_rownames,
    show_colnames        = show_colnames,
    fontsize             = fontsize,
    fontsize_row         = fontsize_row,
    fontsize_col         = fontsize_col,
    color                = color_palette,
    breaks               = breaks,
    annotation_row       = row_ann,
    annotation_col       = col_ann,
    annotation_colors    = annotation_colors,
    border_color         = border_color,
    cellwidth            = cellwidth,
    cellheight           = cellheight,
    main                 = main,
    silent               = silent
  )

  ph
}

# ============================================================
#  Save helper (pheatmap -> pdf/png via grid::grid.draw)
# ============================================================
save_pheatmap <- function(ph, name, out_dir = ".",
                          width = 210, height = 260,
                          units = "mm", dpi = 300, bg = "white",
                          pdf = TRUE, png = TRUE) {
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  paths <- c()

  # pheatmap returns a list; the gtable is in $gtable
  g <- ph$gtable

  # Convert dimensions to inches
  to_inches <- function(val, u) {
    switch(u,
      "mm"  = val / 25.4,
      "cm"  = val / 2.54,
      "in"  = val,
      "px"  = val / dpi,
      val / 25.4   # default assume mm
    )
  }
  w_in <- to_inches(width,  units)
  h_in <- to_inches(height, units)

  if (pdf) {
    pdf_path <- file.path(out_dir, paste0(name, ".pdf"))
    cairo_pdf(pdf_path, width = w_in, height = h_in)
    grid::grid.newpage()
    grid::grid.draw(g)
    dev.off()
    paths <- c(paths, pdf = pdf_path)
  }

  if (png) {
    png_path <- file.path(out_dir, paste0(name, ".png"))
    png(png_path, width = w_in, height = h_in, units = "in", res = dpi, bg = bg)
    grid::grid.newpage()
    grid::grid.draw(g)
    dev.off()
    paths <- c(paths, png = png_path)
  }

  invisible(paths)
}

# ============================================================
#  Demo
# ============================================================
if (sys.nframe() == 0 || isTRUE(getOption("run_demo"))) {
  d <- generate_mock_data()
  ph <- annotated_heatmap(
    mat    = d$mat,
    row_ann = d$row_ann,
    col_ann = d$col_ann,
    scale  = "row",
    main   = "Gene Expression Heatmap"
  )

  out <- template_out_dir()
  save_pheatmap(ph, name = "annotated_heatmap_demo", out_dir = out,
                width = 210, height = 260, units = "mm", dpi = 300)
  message("Demo saved to ", file.path(out, "annotated_heatmap_demo.png"))
}
