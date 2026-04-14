# init.R - Initialize skills for BI report

# Load necessary libraries
suppressMessages({
  if (!require(tidyverse)) install.packages('tidyverse')
  if (!require(DBI)) install.packages('DBI')
  if (!require(RMariaDB)) install.packages('RMariaDB')
  if (!require(RPresto)) install.packages('RPresto')
  if (!require(googledrive)) install.packages('googledrive')
  if (!require(googlesheets4)) install.packages('googlesheets4')
  if (!require(jsonlite)) install.packages('jsonlite')
  if (!require(glue)) install.packages('glue')
  if (!require(writexl)) install.packages('writexl')
  if (!require(httr)) install.packages('httr')
  
  library(tidyverse)
  library(DBI)
  library(RMariaDB)
  library(RPresto)
  library(googledrive)
  library(googlesheets4)
  library(jsonlite)
  library(glue)
  library(writexl)
  library(httr)
})

# Define default paths (auto-detect skill directory)
SKILL_PATH <- dirname(sys.frame(1)$ofile %||% normalizePath("./"))

# Source utility files
# Note: bi_base_utils.R contains DB credentials and is not included in this repo.
# Please create your own bi_base_utils.R with connection configs.
if (file.exists(file.path(SKILL_PATH, "bi_base_utils.R"))) {
  source(file.path(SKILL_PATH, "bi_base_utils.R"))
}
source(file.path(SKILL_PATH, "report_standard_skills.R"))

cat("BI Skills initialized successfully.\n")
