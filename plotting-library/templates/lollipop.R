#' 棒棒糖图 (Lollipop Plot)
#' =========================
#' 基因突变/修饰位点标注图，蛋白结构域+突变频率。
#' versatile版本: 接受任意 position + count/type 数据。
#'
#' 适用数据类型: mutation_site
#' 必需列: position, count (或 value)
#' 可选列: type, label, domain_start, domain_end, domain_name
#'
#' 参考: ChiPlot, cBioPortal Lollipop

# ============ 参数配置 ============
STEM_WIDTH <- 1.0           # 茎宽度
HEAD_SIZE <- 2.5            # 球大小(相对)
DOMAIN_HEIGHT <- 0.12       # 蛋白条高度
DOMAIN_GAP <- 0.02          # 域间距
LABEL_MAX_N <- 8            # 最大标注位点数
NATURE_COLORS <- c("#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4")

# 突变类型配色(经典cBioPortal风格)
MUT_COLORS <- c(
  "Missense"  = "#00A087",
  "Truncating" = "#E64B35",
  "In-frame"  = "#4DBBD5",
  "Splice"    = "#F39B7F",
  "Other"     = "#8491B4",
  "Missense_Mutation" = "#00A087",
  "Nonsense_Mutation" = "#E64B35",
  "Frame_Shift_Del" = "#E64B35",
  "Frame_Shift_Ins" = "#E64B35",
  "Splice_Site" = "#F39B7F",
  "In_Frame_Del" = "#4DBBD5",
  "In_Frame_Ins" = "#4DBBD5"
)

# ============ 数据生成 ============
generate_mock_data <- function(seed = 42) {
  set.seed(seed)

  # 突变位点数据
  positions <- c(72, 175, 220, 248, 273, 282, 342, 245)
  counts <- c(3, 5, 12, 28, 45, 15, 2, 8)
  types <- c("Missense", "Missense", "Missense", "Missense",
            "Missense", "Missense", "Truncating", "Missense")
  labels <- c("P72L", "E175K", "R220*", "R248W",
              "R273H", "E285K", "Q342*", "G245S")

  lollipop <- data.frame(
    position = positions,
    count = counts,
    type = types,
    label = labels,
    stringsAsFactors = FALSE
  )

  # 蛋白结构域(可选)
  domains <- data.frame(
    domain_start = c(1, 95, 290),
    domain_end   = c(94, 289, 393),
    domain_name  = c("TAD1", "DNA-binding", "Tetramerization"),
    stringsAsFactors = FALSE
  )

  list(lollipop = lollipop, domains = domains, protein_length = 393)
}

# ============ 核心绘图 ============
lollipop_plot <- function(
    df,
    pos_col = "position",
    count_col = "count",
    type_col = "type",
    label_col = "label",
    domains = NULL,
    protein_length = NULL,
    title = NULL,
    xlabel = "Amino Acid Position",
    ylabel = "Mutation Count",
    colors = MUT_COLORS,
    show_labels = TRUE,
    label_top_n = LABEL_MAX_N,
    stem_width = STEM_WIDTH,
    head_size = HEAD_SIZE,
    figsize = NULL,
    save_path = NULL,
    dpi = 300,
    preset = "publication"
) {
  #' 绘制棒棒糖图
  #'
  #' Parameters:
  #'   df: data.frame, 至少包含 position 和 count 列
  #'   pos_col: 位置列名(氨基酸位点/基因组坐标)
  #'   count_col: 计数/频率列名
  #'   type_col: 类型列名(可选, 决定颜色分组)
  #'   label_col: 标签列名(可选, 标注关键位点)
  #'   domains: data.frame, 蛋白结构域(annotation bar), 列: start, end, name
  #'   protein_length: 蛋白总长度(默认=max(position)+10%)
  #'   colors: 类型→颜色映射(named vector)

  # Preset sizing
  if (preset == "publication") {
    text_cex <- 0.85
    lwd <- 0.6
    cex_pt <- 0.9
    mar <- c(3.5, 4, 2, 1)
    fig_height <- 3.5
  } else {
    text_cex <- 1.2
    lwd <- 1.2
    cex_pt <- 1.4
    mar <- c(4, 5, 3, 1)
    fig_height <- 5.5
  }

  fig_width <- if (!is.null(figsize)) figsize[1] else 7.2
  fig_height <- if (!is.null(figsize)) figsize[2] else fig_height

  if (is.null(protein_length)) {
    protein_length <- max(df[[pos_col]], na.rm = TRUE) * 1.1
  }

  # 计算y轴上限
  y_max <- max(df[[count_col]], na.rm = TRUE) * 1.15

  # 颜色映射
  if (type_col %in% names(df)) {
    types <- df[[type_col]]
    pt_colors <- sapply(types, function(t) {
      if (t %in% names(colors)) colors[t] else NATURE_COLORS[1]
    })
  } else {
    pt_colors <- rep(NATURE_COLORS[1], nrow(df))
  }

  # 绘图
  if (!is.null(save_path)) {
    png(save_path, width = fig_width, height = fig_height,
        units = "in", res = dpi, bg = "white")
  }

  par(mar = mar)

  # 空画布
  plot(NA, xlim = c(0, protein_length), ylim = c(-0.3, y_max),
       xlab = "", ylab = "", xaxt = "n", yaxt = "n", frame.plot = FALSE)

  # 蛋白条(bar at y=0)
  rect(0, -DOMAIN_HEIGHT * 1.5, protein_length, -DOMAIN_HEIGHT * 0.5,
       col = "#E0E0E0", border = "grey60", lwd = lwd)

  # 结构域(如果提供)
  if (!is.null(domains)) {
    dom_y_bottom <- -DOMAIN_HEIGHT * 1.5
    dom_y_top <- -DOMAIN_HEIGHT * 0.5
    for (i in seq_len(nrow(domains))) {
      ds <- domains[i, 1]
      de <- domains[i, 2]
      dn <- domains[i, 3]
      rect(ds, dom_y_bottom, de, dom_y_top,
           col = NATURE_COLORS[((i - 1) %% length(NATURE_COLORS)) + 1],
           border = "black", lwd = lwd)
      # 域名字
      text((ds + de) / 2, (dom_y_bottom + dom_y_top) / 2,
           labels = dn, cex = text_cex * 0.7, col = "white", font = 2)
    }
  }

  # 棒棒糖: 茎 + 球
  for (i in seq_len(nrow(df))) {
    pos <- df[[pos_col]][i]
    cnt <- df[[count_col]][i]
    col <- pt_colors[i]

    # 茎
    segments(pos, 0, pos, cnt, col = col, lwd = stem_width)
    # 球
    points(pos, cnt, pch = 16, col = col, cex = head_size * cex_pt / 2.5)
  }

  # 标注 top 突变
  if (show_labels && label_col %in% names(df)) {
    df_ord <- df[order(-df[[count_col]]), ]
    top_n <- min(label_top_n, nrow(df_ord))
    top_labels <- df_ord[[label_col]][1:top_n]
    top_pos <- df_ord[[pos_col]][1:top_n]
    top_counts <- df_ord[[count_col]][1:top_n]
    top_cols <- sapply(df_ord[[type_col]][1:top_n], function(t) {
      if (t %in% names(colors)) colors[t] else NATURE_COLORS[1]
    })

    # 交错标注避免重叠
    offset_y <- y_max * 0.03
    for (j in seq_len(top_n)) {
      text(top_pos[j], top_counts[j] + offset_y,
           labels = top_labels[j], cex = text_cex * 0.8,
           col = top_cols[j], font = 2, srt = 30, adj = c(0, 0))
    }
  }

  # 轴
  axis(1, at = pretty(c(0, protein_length)), cex.axis = text_cex)
  axis(2, at = pretty(c(0, y_max)), cex.axis = text_cex, las = 1)

  mtext(xlabel, side = 1, line = 2.2, cex = text_cex)
  mtext(ylabel, side = 2, line = 2.5, cex = text_cex)
  if (!is.null(title)) {
    mtext(title, side = 3, line = 0.5, cex = text_cex * 1.1, font = 2)
  }

  # 图例(唯一类型)
  if (type_col %in% names(df)) {
    unique_types <- unique(df[[type_col]])
    legend_cols <- sapply(unique_types, function(t) {
      if (t %in% names(colors)) colors[t] else NATURE_COLORS[1]
    })
    legend("topright", legend = unique_types, col = legend_cols,
           pch = 16, lty = 1, lwd = 1, cex = text_cex * 0.8,
           bty = "n", y.intersp = 1.2)
  }

  if (!is.null(save_path)) {
    dev.off()
    cat("Saved to", save_path, "\n")
  }

  invisible(df)
}

# ============ 主程序 ============
if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  mock <- generate_mock_data()
  lollipop_plot(
    mock$lollipop,
    domains = mock$domains,
    protein_length = mock$protein_length,
    save_path = "lollipop_demo.png",
    title = "TP53 Mutation Landscape"
  )
}