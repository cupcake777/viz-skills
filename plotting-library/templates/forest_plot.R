#' 森林图 (Forest Plot)
#' ======================
#' 展示多变量OR/HR及置信区间，Meta分析和临床预后标配。
#'
#' 适用数据类型: meta_analysis
#' 必需列: variable, estimate, ci_lower, ci_upper
#' 可选列: se, pvalue, group, weight, n_events
#'
#' 参考: SRplot, Bioincloud, forestplot package

# ============ 参数配置 ============
REFERENCE_LINE <- 1        # OR=1 / HR=1 参考线
POINT_SIZE <- 3             # 估计点大小
CI_LINEWIDTH <- 0.8        # CI线宽
ESTIMATE_SHAPE <- 18       # 18=diamond, 16=circle
HEADER_FONT <- 2           # bold
ROW_FONT <- 1              # normal
DIGITS <- 2                # 数值显示小数位

# Nature配色
NATURE_COLORS <- c("#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4")

# ============ 数据生成 ============
generate_mock_data <- function(n_vars = 8, seed = 42) {
  set.seed(seed)
  variables <- c(
    "Age (>65)", "Sex (M)", "Stage (III/IV)", "TP53 mutation",
    "BRAF mutation", "BMI (>30)", "Smoking", "APA lengthening"
  )
  # HR estimates with CIs
  estimates <- c(1.45, 1.12, 2.31, 1.87, 0.73, 0.91, 1.56, 1.68)
  ci_lower <- c(1.10, 0.89, 1.72, 1.42, 0.55, 0.68, 1.12, 1.28)
  ci_upper <- c(1.92, 1.41, 3.10, 2.46, 0.97, 1.22, 2.17, 2.20)
  pvalues <- c(0.008, 0.224, 1e-5, 3e-4, 0.031, 0.542, 0.009, 2e-4)

  data.frame(
    variable = variables,
    estimate = estimates,
    ci_lower = ci_lower,
    ci_upper = ci_upper,
    pvalue = pvalues,
    stringsAsFactors = FALSE
  )
}

# ============ 核心绘图 ============
forest_plot <- function(
    df,
    var_col = "variable",
    est_col = "estimate",
    lower_col = "ci_lower",
    upper_col = "ci_upper",
    pval_col = NULL,
    group_col = NULL,
    ref_line = REFERENCE_LINE,
    title = NULL,
    xlab = "Hazard Ratio (95% CI)",
    colors = NATURE_COLORS,
    point_size = POINT_SIZE,
    ci_linewidth = CI_LINEWIDTH,
    log_scale = TRUE,
    figsize = NULL,
    save_path = NULL,
    dpi = 300,
    preset = "publication"
) {
  #' 绘制森林图
  #'
  #' Parameters:
  #'   df: data.frame, 必须包含 variable, estimate, ci_lower, ci_upper 列
  #'   var_col: 变量名列名
  #'   est_col: 估计值列名 (OR/HR)
  #'   lower_col: CI下限列名
  #'   upper_col: CI上限列名
  #'   pval_col: p值列名(可选, 用于标记显著性)
  #'   group_col: 分组列名(可选, 用于颜色)
  #'   ref_line: 参考线位置(OR/HR=1)
  #'   xlab: x轴标签
  #'   log_scale: 是否对数刻度x轴
  #'   preset: "publication"(7pt) / "presentation"(16pt)

  # Preset sizing
  if (preset == "publication") {
    par(fontsize = 7, lwd = 0.5)
    text_cex <- 0.85
    point_cex <- 0.6
    mar <- c(4, 8, 2, 8)
    fig_width <- 7.2
    fig_height <- 1.0 + nrow(df) * 0.38
  } else {
    par(fontsize = 16, lwd = 1.2)
    text_cex <- 1.1
    point_cex <- 1.0
    mar <- c(5, 10, 3, 10)
    fig_width <- 12
    fig_height <- 2 + nrow(df) * 0.55
  }

  if (!is.null(figsize)) {
    fig_width <- figsize[1]
    fig_height <- figsize[2]
  }

  n <- nrow(df)
  y_pos <- n:1  # 逆序: 第一行在上

  # X轴范围
  all_vals <- c(df[[lower_col]], df[[upper_col]], ref_line)
  if (log_scale) {
    xlim <- range(pretty(range(log(all_vals))), na.rm = TRUE)
    xlim <- exp(xlim)
  } else {
    xlim <- range(pretty(range(all_vals, na.rm = TRUE)))
  }

  # 颜色
  if (!is.null(group_col) && group_col %in% names(df)) {
    groups <- as.factor(df[[group_col]])
    grp_colors <- colors[as.integer(groups)]
  } else {
    grp_colors <- rep(colors[1], n)
  }

  # 显著性标记
  sig_mark <- rep("", n)
  if (!is.null(pval_col) && pval_col %in% names(df)) {
    sig_mark <- ifelse(df[[pval_col]] < 0.001, "***",
                  ifelse(df[[pval_col]] < 0.01, "**",
                  ifelse(df[[pval_col]] < 0.05, "*", "")))
  }

  # 绘图
  if (!is.null(save_path)) {
    png(save_path, width = fig_width, height = fig_height,
        units = "in", res = dpi, bg = "white")
  }

  par(mar = mar, xpd = FALSE)

  # 空白画布
  if (log_scale) {
    plot(NA, xlim = log(xlim), ylim = c(0.5, n + 0.5),
         xlab = "", ylab = "", yaxt = "n", xaxt = "n",
         frame.plot = FALSE)
    axis(1, at = log(axTicks(1)), labels = round(exp(axTicks(1)), 2))
  } else {
    plot(NA, xlim = xlim, ylim = c(0.5, n + 0.5),
         xlab = "", ylab = "", yaxt = "n", xaxt = "n",
         frame.plot = FALSE)
  }

  # 参考线
  if (log_scale) {
    abline(v = log(ref_line), lty = 2, col = "grey60", lwd = ci_linewidth)
  } else {
    abline(v = ref_line, lty = 2, col = "grey60", lwd = ci_linewidth)
  }

  # 交替行背景
  for (i in 1:n) {
    if (i %% 2 == 0) {
      rect(par("usr")[1], y_pos[i] - 0.4, par("usr")[2], y_pos[i] + 0.4,
           col = "#F5F5F5", border = NA)
    }
  }

  # CI 和估计点
  for (i in 1:n) {
    est <- df[[est_col]][i]
    lo <- df[[lower_col]][i]
    hi <- df[[upper_col]][i]
    col <- grp_colors[i]

    if (log_scale) {
      # CI线
      segments(log(lo), y_pos[i], log(hi), y_pos[i],
               col = col, lwd = ci_linewidth * 1.5)
      # CI两端横线
      segments(log(lo), y_pos[i] - 0.08, log(lo), y_pos[i] + 0.08,
               col = col, lwd = ci_linewidth)
      segments(log(hi), y_pos[i] - 0.08, log(hi), y_pos[i] + 0.08,
               col = col, lwd = ci_linewidth)
      # 估计点
      points(log(est), y_pos[i], pch = 18, col = col, cex = point_cex * 1.2)
    } else {
      segments(lo, y_pos[i], hi, y_pos[i],
               col = col, lwd = ci_linewidth * 1.5)
      segments(lo, y_pos[i] - 0.08, lo, y_pos[i] + 0.08,
               col = col, lwd = ci_linewidth)
      segments(hi, y_pos[i] - 0.08, hi, y_pos[i] + 0.08,
               col = col, lwd = ci_linewidth)
      points(est, y_pos[i], pch = 18, col = col, cex = point_cex * 1.2)
    }
  }

  # 左侧变量名
  text(par("usr")[1] - strwidth("M") * 0.5, y_pos,
       labels = df[[var_col]], adj = 1, cex = text_cex, font = ROW_FONT)

  # 右侧HR (95% CI)
  hr_text <- sprintf("%.{1$d} (%.{1$d}-%.{1$d})", DIGITS, DIGITS, DIGITS)
  hr_labels <- sprintf(hr_text, df[[est_col]], df[[lower_col]], df[[upper_col]])
  text(par("usr")[2] + strwidth("M") * 0.5, y_pos,
       labels = hr_labels, adj = 0, cex = text_cex, font = ROW_FONT)

  # 显著性星号
  if (any(sig_mark != "")) {
    text(par("usr")[2] + strwidth("M") * 12, y_pos,
         labels = sig_mark, adj = 0, cex = text_cex * 0.8, col = "#E64B35")
  }

  # 轴标签
  mtext(xlab, side = 1, line = 2.5, cex = text_cex)
  if (!is.null(title)) {
    mtext(title, side = 3, line = 0.5, cex = text_cex * 1.1, font = 2)
  }

  par(xpd = TRUE)

  if (!is.null(save_path)) {
    dev.off()
    cat("Saved to", save_path, "\n")
  }

  invisible(df)
}

# ============ 主程序 ============
if (sys.nframe() == 0 || identical(environment(), globalenv())) {
  df <- generate_mock_data()
  forest_plot(df, save_path = "forest_plot_demo.png",
              title = "Prognostic Factors (Multivariate Cox)",
              xlab = "Hazard Ratio (95% CI)")
}