#' Phylogenetic Tree (Rectangular Dendrogram)
#'
#' Rectangular phylogenetic tree built entirely with stats::hclust + ggplot2
#' segments.  No external phylogenetics packages (ape, ggtree) required.
#'
#' Workflow: generate_mock_data() produces a distance matrix among taxa, runs
#' hclust, and returns a list with the hclust object and taxa names.
#' plot_phylogenetic_tree() extracts the dendrogram geometry, computes x/y
#' coordinates for each branch, and draws them with geom_segment().
#'
#' @section Colour: branches are coloured by clade membership (tree cut into
#'   n_clades groups).  Merges that join two different clades are drawn in grey.

# --- sourcing & libraries ---------------------------------------------------
tryCatch(source("/app/r_libs/style/base_plot.R"),
         error = function(e) source("base_plot.R"))

suppressPackageStartupMessages({ library(ggplot2) })

# --- mock data --------------------------------------------------------------

#' Generate mock taxa-feature matrix and return an hclust dendrogram.
#'
#' @param n_taxa  Number of taxa (default 13).
#' @param n_feat  Number of features (default 50).
#' @param seed    Random seed for reproducibility.
#' @return A list with components: hc (hclust object), labels (character vector
#'   of taxa names in tree order), dist_mat (distance matrix).
generate_mock_data <- function(n_taxa = 13, n_feat = 50, seed = 42) {
  set.seed(seed)

  # Simulate four clades with distinct feature profiles
  n_clades  <- 4
  taxa_per  <- rep(ceiling(n_taxa / n_clades), n_clades)
  taxa_per[n_clades] <- n_taxa - sum(taxa_per[-n_clades])

  clade_labels <- rep(paste0("Clade_", LETTERS[1:n_clades]), taxa_per)
  taxa_names   <- paste0("Species_", seq_len(n_taxa))

  # Each clade is centred on a different region of feature space
  mat <- matrix(0, nrow = n_taxa, ncol = n_feat)
  for (cl in seq_len(n_clades)) {
    idx <- which(clade_labels == paste0("Clade_", LETTERS[cl]))
    centre <- rnorm(n_feat, mean = 0, sd = 3)
    for (j in idx) {
      mat[j, ] <- centre + rnorm(n_feat, mean = 0, sd = 0.6)
    }
  }
  rownames(mat) <- taxa_names

  dist_mat <- dist(mat, method = "euclidean")
  hc       <- hclust(dist_mat, method = "average")

  list(hc = hc, labels = taxa_names, dist_mat = dist_mat)
}

# --- geometry helpers -------------------------------------------------------

#' Retrieve all leaf indices beneath a given internal node.
#'
#' @param hc    An hclust object.
#' @param node  Internal node index (positive integer from merge[,1] / merge[,2]).
#' @return Integer vector of original observation indices.
#' @keywords internal
get_descendant_leaves <- function(hc, node) {
  if (node < 0) return(abs(node))
  left  <- hc$merge[node, 1]
  right <- hc$merge[node, 2]
  c(get_descendant_leaves(hc, left),
    get_descendant_leaves(hc, right))
}

#' Convert an hclust object into a data.frame of rectangular-dendrogram segments.
#'
#' Each row is one line segment with columns x, y, xend, yend, merge_id, and
#' segment_type (horizontal / vertical_left / vertical_right).
#'
#' @param hc An hclust object.
#' @return A data.frame suitable for geom_segment().
#' @keywords internal
hclust_to_segments <- function(hc) {
  n <- length(hc$order)

  # Leaf x-positions follow tree order
  leaf_x <- numeric(n)
  for (i in seq_len(n)) leaf_x[hc$order[i]] <- i

  parent_x <- numeric(n - 1)
  parent_y <- hc$height

  segs <- data.frame(
    x = numeric(), xend = numeric(),
    y = numeric(), yend = numeric(),
    merge_id = integer(), segment_type = character(),
    stringsAsFactors = FALSE
  )

  for (i in seq_len(n - 1)) {
    left  <- hc$merge[i, 1]
    right <- hc$merge[i, 2]

    if (left < 0) { lx <- leaf_x[abs(left)]; ly <- 0 }
    else          { lx <- parent_x[left];   ly <- parent_y[left] }

    if (right < 0) { rx <- leaf_x[abs(right)]; ry <- 0 }
    else           { rx <- parent_x[right];    ry <- parent_y[right] }

    parent_x[i] <- (lx + rx) / 2

    segs <- rbind(segs, data.frame(
      x = c(lx,  lx, rx),  xend = c(rx, lx, rx),
      y = c(parent_y[i], ly, ry), yend = c(parent_y[i], parent_y[i], parent_y[i]),
      merge_id    = rep(i, 3),
      segment_type = c("horizontal", "vertical_left", "vertical_right"),
      stringsAsFactors = FALSE
    ))
  }
  segs
}

#' Assign a clade (cluster) label to every segment.
#'
#' Segments that bridge two different clades receive "root" (grey).
#'
#' @param segs  data.frame from hclust_to_segments().
#' @param hc    An hclust object.
#' @param n_clades  Number of clades (clusters).
#' @return The segs data.frame with an additional \code{clade} column.
#' @keywords internal
assign_clades <- function(segs, hc, n_clades = 4) {
  clusters <- cutree(hc, k = n_clades)

  merge_clade <- integer(max(segs$merge_id))
  for (m in seq_along(merge_clade)) {
    leaves <- get_descendant_leaves(hc, m)
    cls    <- unique(clusters[leaves])
    merge_clade[m] <- if (length(cls) == 1) cls else 0L
  }

  segs$clade <- merge_clade[segs$merge_id]
  segs$clade <- factor(segs$clade, levels = c(seq_len(n_clades), 0),
                       labels = c(paste0("clade_", seq_len(n_clades)), "root"))
  segs
}

# --- main plot function -----------------------------------------------------

#' Draw a rectangular phylogenetic / dendrogram tree.
#'
#' @param hc        An hclust object.
#' @param n_clades  Number of clades for colour grouping (default 4).
#' @param palette   Named character vector of colours.  Defaults to the first
#'   \code{n_clades} entries of NATURE_COLORS plus grey for root joins.
#' @param base_size Base font size (default 14).
#' @param line_size Branch line width (default 0.55).
#' @param label_size Font size for tip labels (default 3.4).
#' @param tip_margin Extra x-axis expansion so labels fit (default 2.2).
#' @return A ggplot object.
plot_phylogenetic_tree <- function(
    hc,
    n_clades   = 4,
    palette    = NULL,
    base_size  = 14,
    line_size  = 0.55,
    label_size = 3.4,
    tip_margin = 2.2,
    ...
) {
  n <- length(hc$order)

  if (is.null(palette)) {
    palette <- c(NATURE_COLORS[seq_len(n_clades)], "root" = "grey65")
  }

  segs <- hclust_to_segments(hc)
  segs <- assign_clades(segs, hc, n_clades = n_clades)

  # Tip labels: one per leaf in tree order
  tip_df <- data.frame(
    x     = seq_len(n),
    y     = 0,
    label = hc$labels[hc$order],
    stringsAsFactors = FALSE
  )

  ggplot() +
    geom_segment(
      data = segs,
      aes(x = x, y = y, xend = xend, yend = yend, colour = clade),
      size = line_size, lineend = "square"
    ) +
    geom_text(
      data = tip_df,
      aes(x = x, y = y, label = label),
      hjust = 0, nudge_y = 0.005 * max(hc$height),
      size = label_size, family = "Arial"
    ) +
    scale_colour_manual(values = palette, guide = "none") +
    scale_x_continuous(expand = expansion(mult = c(0.02, 0.06 * tip_margin))) +
    scale_y_continuous(expand = expansion(mult = c(0.02, 0.06))) +
    labs(x = NULL, y = "Branch distance") +
    coord_cartesian(clip = "off") +
    theme_sci(base_size = base_size) +
    theme(
      axis.text.x  = element_blank(),
      axis.ticks.x = element_blank(),
      axis.line.x   = element_blank(),
      plot.margin   = margin(5, 40, 5, 5, "pt")
    )
}

# --- demo -------------------------------------------------------------------
if (sys.nframe() == 0) {
  args      <- commandArgs(trailingOnly = FALSE)
  file_arg  <- sub("^--file=", "", args[grepl("^--file=", args)])
  out_dir   <- file.path(dirname(script_dir), "demo_fig")

  demo <- generate_mock_data(n_taxa = 13, seed = 42)

  p <- plot_phylogenetic_tree(demo$hc, n_clades = 4, base_size = 14)

  save_demo(p, name = "phylogenetic_tree_demo", out_dir = out_dir,
            width = 180, height = 130)
}
