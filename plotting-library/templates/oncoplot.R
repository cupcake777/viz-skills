#' 肿瘤瀑布图 (Oncoplot / Waterfall Plot)
#' =========================================
#' 展示基因突变景观矩阵：行为样本，列为基因，颜色为突变类型。
#' versatile版本：接受任意样本×基因×突变类型的长格式数据。
#'
#' 适用数据类型: mutation_matrix
#' 必需列: sample, gene, mutation_type
#' 可选列: frequency (如果不提供则自动统计)
#'
#' 参考: SRplot, maftools oncoplot, Bioincloud

# ============ 参数配置 ============
NATURE_COLORS <- c("#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4")

# 突变类型配色(经典MAF风格, versatile映射)
MUT_PALETTE <- c(
  "Missense_Mutation"  = "#00A087",
  "Missense"           = "#00A087",
  "Nonsense_Mutation"   = "#E64B35",
  "Nonsense"           = "#E64B35",
  "Frame_Shift_Del"    = "#E64B35",
  "Frame_Shift_Ins"    = "#E64B35",
  "Splice_Site"        = "#F39B7F",
  "In_Frame_Del"       = "#4DBBD5",
  "In_Frame_Ins"       = "#4DBBD5",
  "Multi_Hit"          = "#3C5488",
  "Amp"                = "#FF9900",
  "Del"                = "#8491B4",
  "Other"              = "#8491B4"
)

# 类型简化映射(用户数据可能用简写)
MUT_SIMPLIFY <- c(
  "Missense" = "Missense",
  "Nonsense" = "Nonsense",
  "FS_del" = "Frame_Shift",
  "FS_ins" = "Frame_Shift",
  "Splice" = "Splice",
  "Inframe" = "In_frame",
  "AMP" = "Amp",
  "DEL" = "Del"
)

# ============ 数据生成 ============
generate_mock_data <- function(n_samples = 40, n_genes = 10, seed = 42) {
  set.seed(seed)

  genes <- c("TP53", "KRAS", "BRAF", "PIK3CA", "APC",
             "SMAD4", "PTEN", "EGFR", "NF1", "CDKN2A")

  # 突变频率递减
  mutation_freq <- c(0.75, 0.55, 0.48, 0.35, 0.30,
                    0.25, 0.20, 0.18, 0.12, 0.08)

  # 突变类型
  mut_types <- c("Missense", "Nonsense", "Frame_Shift_Del",
                 "Splice_Site", "In_Frame_Del", "Multi_Hit")
  type_weights <- c(0.50, 0.15, 0.12, 0.08, 0.05, 0.10)

  samples <- paste0("TCGA-", sprintf("%02d", 1:n_samples))
  rows <- list()

  for (g in seq_along(genes)) {
    n_mut <- round(n_samples * mutation_freq[g])
    mut_samples <- sample(samples, n_mut)
    for (s in mut_samples) {
      # 同一个样本同一基因只保留最高优先级类型
      mt <- sample(mut_types, 1, prob = type_weights)
      rows <- c(rows, list(data.frame(
        sample = s,
        gene = genes[g],
        mutation_type = mt,
        stringsAsFactors = FALSE
      )))
    }
  }

  do.call(rbind, rows)
}

# ============ 核心绘图 ============
oncoplot <- function(
    df,
    sample_col = "sample",
    gene_col = "gene",
    type_col = "mutation_type",
    top_n_genes = 10,
    title = NULL,
    show_barplot = TRUE,
    show_freq = TRUE,
    colors = MUT_PALETTE,
    figsize = NULL,
    save_path = NULL,
    dpi = 300,
    preset = "publication"
) {
  #' 绘制肿瘤瀑布图(Oncoplot)
  #'
  #' Parameters:
  #'   df: data.frame, 长格式 sample-gene-mutation_type
  #'   sample_col: 样本ID列名
  #'   gene_col: 基因名列名
  #'   type_col: 突变类型列名
  #'   top_n_genes: 显示前N个高频突变基因
  #'   show_barplot: 右侧是否显示突变频率条形图
  #'   show_freq: 左侧是否显示百分比

  # Preset sizing
  if (preset == "publication") {
    text_cex <- 0.65
    lwd <- 0.5
    mar_main <- c(0.5, 6, 2, 0.5)
    mar_bar <- c(0.5, 0, 2, 4)
    fig_height <- 2.0 + top_n_genes * 0.28
    fig_width <- 5.5 + 3.5  # main + barplot
  } else {
    text_cex <- 1.0
    lwd <- 1.0
    mar_main <- c(1, 8, 3, 1)
    mar_bar <- c(1, 0, 3, 5)
    fig_height <- 3.5 + top_n_genes * 0.45
    fig_width <- 9 + 5
  }

  if (!is.null(figsize)) {
    fig_width <- figsize[1]
    fig_height <- figsize[2]
  }

  # 统计基因频率, 取top N
  gene_counts <- sort(table(df[[gene_col]]), decreasing = TRUE)
  top_genes <- names(gene_counts)[1:min(top_n_genes, length(gene_counts))]
  n_genes <- length(top_genes)

  # 子集数据到top基因
  df_sub <- df[df[[gene_col]] %in% top_genes, ]
  df_sub[[gene_col]] <- factor(df_sub[[gene_col]], levels = rev(top_genes))

  # 样本排序: 突变越多越左
  sample_mut_count <- table(df_sub[[sample_col]])
  # 包含无突变的样本仍显示
  all_samples <- unique(df[[sample_col]])

  # 按突变模式排序样本
  sample_order <- names(sort(sample_mut_count, decreasing = TRUE))
  # 加入无突变样本
  zero_samples <- setdiff(all_samples, sample_order)
  sample_order <- c(sample_order, zero_samples)

  n_samples <- length(sample_order)

  # 突变类型→颜色
  all_types <- unique(df_sub[[type_col]])
  type_colors <- sapply(all_types, function(t) {
    if (t %in% names(colors)) colors[t] else NATURE_COLORS[1]
  })
  names(type_colors) <- all_types

  # 构建矩阵
  mut_matrix <- matrix(NA, nrow = n_genes, ncol = n_samples)
  rownames(mut_matrix) <- rev(top_genes)
  colnames(mut_matrix) <- sample_order

  for (i in seq_len(nrow(df_sub))) {
    s <- as.character(df_sub[[sample_col]][i])
    g <- as.character(df_sub[[gene_col]][i])
    t <- as.character(df_sub[[type_col]][i])
    if (s %in% sample_order && g %in% top_genes) {
      mut_matrix[g, s] <- t
    }
  }

  # 同一样本同一基因多种突变→Multi_Hit
  # (已在长格式中只保留一种, 真实数据需预处理)
  # 这里简化: 如果一个sample-gene有多行, 只取第一行

  # 绘图
  if (!is.null(save_path)) {
    png(save_path, width = fig_width, height = fig_height,
        units = "in", res = dpi, bg = "white")
  }

  # 布局: 主矩阵 + 频率条形图
  if (show_barplot) {
    layout(matrix(c(1, 2), nrow = 1), widths = c(5.5/9, 3.5/9))
  }

  # ---- 主矩阵 ----
  par(mar = mar_main)

  # 空画布
  plot(NA, xlim = c(0.5, n_samples + 0.5), ylim = c(0.5, n_genes + 0.5),
       xlab = "", ylab = "", xaxt = "n", yaxt = "n", frame.plot = FALSE)

  # 绘制突变色块
  cell_width <- 0.85
  for (i in 1:n_genes) {
    for (j in 1:n_samples) {
      mt <- mut_matrix[i, j]
      if (!is.na(mt)) {
        col <- if (mt %in% names(type_colors)) type_colors[mt] else "#8491B4"
        rect(j - cell_width / 2, i - 0.4, j + cell_width / 2, i + 0.4,
             col = col, border = NA)
      }
    }
  }

  # 格线
  abline(h = seq(0.5, n_genes + 0.5, 1), col = "white", lwd = 2)
  abline(v = seq(0.5, n_samples + 0.5, 2), col = "white", lwd = 0.3)

  # 基因名(右y轴)
  axis(2, at = 1:n_genes, labels = rev(top_genes),
       las = 2, cex.axis = text_cex, tick = FALSE, line = 0.3)

  # 左侧频率标注
  if (show_freq) {
    total_n <- length(all_samples)
    freq_text <- sprintf("%d (%.0f%%)", as.numeric(gene_counts[top_genes]),
                         as.numeric(gene_counts[top_genes]) / total_n * 100)
    axis(2, at = 1:n_genes, labels = freq_text,
         las = 2, cex.axis = text_cex * 0.8, tick = FALSE, line = -3.5,
         hadj = 1)
  }

  # 标题
  if (!is.null(title)) {
    mtext(title, side = 3, line = 0.5, cex = text_cex * 1.2, font = 2)
  }

  # ---- 频率条形图 ----
  if (show_barplot) {
    par(mar = mar_bar)
    freq <- as.numeric(gene_counts[top_genes]) / length(all_samples) * 100
    barplot(rev(freq), horiz = TRUE, col = rev(NATURE_COLORS[1:n_genes]),
            border = NA, xlim = c(0, max(freq) * 1.1),
            names.arg = rep("", n_genes), cex.names = text_cex,
            xlab = "Mutated (%)", cex.lab = text_cex)
    # 百分比标注
    text(rev(freq) + max(freq) * 0.05, seq_len(n_genes) - 0.2,
         labels = sprintf("%.0f%%", rev(freq)),
         cex = text_cex * 0.75, adj = 0)
  }

  # 图例
  par(fig = c(0, 1, 0, 1), mar = c(0, 0, 0, 0), new = TRUE)
  plot(NA, xlim = c(0, 1), ylim = c(0, 1), xaxt = "n", yaxt = "n",
       xlab = "", ylab = "", frame.plot = FALSE)

  leg_types <- names(type_colors)
  leg_col <- unname(type_colors)
  legend("bottomright", legend = leg_types, fill = leg_col, border = NA,
         bty = "n", cex = text_cex * 0.75, ncol = min(3, length(leg_types)),
         inset = c(0, 0))

  if (!is.null(save_path)) {
    dev.off()
    cat("Saved to", save_path, "\n")
  }

  invisible(mut_matrix)
}

# ============ 主程序 ============
if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  df <- generate_mock_data()
  oncoplot(df, top_n_genes = 10,
            save_path = "oncoplot_demo.png",
            title = "Somatic Mutation Landscape")
}