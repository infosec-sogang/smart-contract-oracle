#!/usr/bin/env Rscript
# Plot the average # of bugs found over time, using parsed-results/log_*.txt.
# Usage: Rscript scripts/plot_ELSC_time.R  (PDFs are saved in the current dir)
library(ggplot2)
library(cowplot)

args = commandArgs(trailingOnly=FALSE)
script_dir = dirname(normalizePath(sub("^--file=", "", grep("^--file=", args, value=TRUE))))
DATA_DIR = file.path(script_dir, "..", "parsed-results")

# Index of the bugs-over-time block in log_<name>.txt, where blocks are
# separated by "=====" lines (SC found times, SC over time, EL found times, EL over time).
BLOCK_IDX = c(SC=1, EL=3)

read_time = function(name, bug) {
  lines = readLines(file.path(DATA_DIR, sprintf("log_%s.txt", name)))
  block = cumsum(startsWith(lines, "====="))
  lines = lines[block == BLOCK_IDX[bug] & grepl("^[0-9]+m: ", lines)]
  data.frame(time=as.integer(sub("m:.*", "", lines)),
             bugs=as.numeric(sub(".*: ", "", lines)))
}

# Each panel: list(log name, legend label, color, linetype)
PANEL_RLF = list(
  list("smartian-original", quote("Smartian"),        "#4DAF4A", "solid"),
  list("smartian-rlf",      quote("Smartian"["RLF"]), "#1100FF", "62"),
  list("rlf",               quote("RLF"),             "#E41A1C", "31"),
  list("rlf-smartian",      quote("RLF"["SN"]),       "#984EA3", "solid"))
PANEL_SMARTEST = list(
  list("smartian-original", quote("Smartian"),        "#4DAF4A", "solid"),
  list("smartian-smartest", quote("Smartian"["ST"]),  "#377EB8", "62"),
  list("smartest",          quote("SmarTest"),        "#FF007B", "31"),
  list("smartest-smartian", quote("SmarTest"["SN"]),  "#FF7F00", "solid"))

read_panel = function(panel, bug) {
  names = sapply(panel, `[[`, 1)
  result = do.call(rbind, lapply(names, function(n) data.frame(read_time(n, bug), group=n)))
  result$group = factor(result$group, levels=names)
  return (result)
}

make_graph_time = function(result, panel, y_max, y_step) {
  labels = as.expression(lapply(panel, `[[`, 2))
  g <- ggplot(result, aes(x=time, y=bugs, group=group, color=group)) +
    geom_line(aes(linetype=group), linewidth=0.6) +
    scale_color_manual(values=sapply(panel, `[[`, 3), labels=labels) +
    scale_linetype_manual(values=sapply(panel, `[[`, 4), labels=labels) +
    theme_bw() +
    theme(  panel.grid.minor = element_blank(),
        axis.text = element_text(size=8),
        axis.title = element_text(size=8.5),
        legend.position = "inside",
        legend.position.inside = c(0.98, 0.04),
        legend.justification = c(1, 0),
        legend.title = element_blank(),
        legend.text = element_text(size=7.7),
        legend.background = element_rect(fill = "transparent"),
        legend.key = element_rect(fill = "transparent"),
        legend.key.size = unit(0.38, 'cm'),
        legend.key.width = unit(0.6, 'cm') ) +
    xlab("Time (min.)") +
    ylab("Total # of bugs found") +
    scale_x_continuous(breaks=c(seq(from=0,to=120,by=30))) +
    scale_y_continuous(limits=c(0, y_max), breaks=c(seq(from=0,to=y_max,by=y_step)),
                       expand=expansion(mult=c(0, 0)))
  return (g)
}

plot_bug = function(bug, y_step, out_file) {
  d_rlf = read_panel(PANEL_RLF, bug)
  d_smartest = read_panel(PANEL_SMARTEST, bug)
  # Use the same y-axis range for both panels.
  y_max = ceiling(max(d_rlf$bugs, d_smartest$bugs) / y_step) * y_step
  g <- plot_grid(make_graph_time(d_rlf, PANEL_RLF, y_max, y_step),
        make_graph_time(d_smartest, PANEL_SMARTEST, y_max, y_step),
        nrow=1, align="hv")
  ggsave(out_file, g, width=4.35, height=2.0, device=cairo_pdf)
  cat("Saved", out_file, "\n")
}

plot_bug("EL", 20, "./ether_leakage.pdf")
plot_bug("SC", 10, "./suicidal.pdf")
