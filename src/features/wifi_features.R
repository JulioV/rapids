source("renv/activate.R")

library(dplyr)

filter_by_day_segment <- function(data, day_segment) {
  if(day_segment %in% c("morning", "afternoon", "evening", "night"))
    data <- data %>% filter(local_day_segment == day_segment)

  return(data %>% group_by(local_date))
}

compute_wifi_feature <- function(data, feature, day_segment){
  if(feature %in% c("countscans", "uniquedevices")){
    data <- data %>% filter_by_day_segment(day_segment)
    data <- switch(feature,
              "countscans" = data %>% summarise(!!paste("wifi", day_segment, feature, sep = "_") := n()),
              "uniquedevices" = data %>% summarise(!!paste("wifi", day_segment, feature, sep = "_") := n_distinct(bssid)))
    return(data)
   } else if(feature == "countscansmostuniquedevice"){
     # Get the most scanned device
    data <- data %>% group_by(bssid) %>% 
      mutate(N=n()) %>% 
      ungroup() %>%
      filter(N == max(N))
    return(data %>% 
             filter_by_day_segment(day_segment) %>%
             summarise(!!paste("wifi", day_segment, feature, sep = "_") := n()))
  }
}

data <- read.csv(snakemake@input[[1]], stringsAsFactors = FALSE)
day_segment <- snakemake@params[["day_segment"]]
requested_features <-  snakemake@params[["features"]]
features = data.frame(local_date = character(), stringsAsFactors = FALSE)

for(requested_feature in requested_features){
  feature <- compute_wifi_feature(data, requested_feature, day_segment)
  features <- merge(features, feature, by="local_date", all = TRUE)
}

write.csv(features, snakemake@output[[1]], row.names = FALSE)