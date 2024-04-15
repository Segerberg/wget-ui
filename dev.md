****# Model 

## Targets
Target refers to a specific segment of the web that you aim to archive data from, such as a website or a collection of web pages. 
a schedule for when the archiving will occur.

## Crawler 
Details and settings about the crawler and the setup for this particular crawler. E.g. Wget with configuration, Heritrix, Browsertrix, Scrappy etc.. 

## Jobs
Single archiving job of a Target that is scheduled to occur (or which has already occurred) at a specific date and time.

## Seeds
Seed url - a starting URL for an archive job, usually the root address of a website. Most jobs start with a seed and include all pages “below” that seed.

## QA 
### Automated QA 
The automated quality assurance process runs after a job completes. Includes validation of the warc-file and provides stats for manual QA

### Manual QA
Ocular inspection of the archived webpage.



