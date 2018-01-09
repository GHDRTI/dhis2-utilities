install.packages("rJava")
install.packages("RJDBC")
library(rJava)
library(RJDBC)


#set up URL to download Athena JDBC driver
URL <- 'https://s3.amazonaws.com/athena-downloads/drivers/AthenaJDBC41-1.1.0.jar'
fil <- basename(URL)


#download the file into current working directory
if (!file.exists(fil)) download.file(URL, fil)

drv <- JDBC(driverClass="com.amazonaws.athena.jdbc.AthenaDriver", fil, identifier.quote="'")

#connect to Athena using the driver, S3 working directory and credentials for Athena 
con <- jdbcConnection <- dbConnect(drv, 'jdbc:awsathena://athena.us-west-2.amazonaws.com:443/',
                                   s3_staging_dir="s3://aws-athena-query-results-695486472001-us-west-2/",
                                   user=Sys.getenv("ATHENA_USER"),
                                   password=Sys.getenv("ATHENA_PASSWORD"))


dfdhis2=dbGetQuery(con, "SELECT * FROM stoppalu.dhis2_export limit 10")
head(dfdhis2,2)

