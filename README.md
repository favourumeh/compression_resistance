# Automating the Design of Compression Members

![](https://github.com/favourumeh/compression_resistance/blob/main/Universal%20I-Beam%20and%20compressive%20load%20image.png)

## Project Overview
- Created a tool that provides desk-based assessment of the adequacy of universal columns and beams (UKC and UKB) subjected to compressive loads. 
- It uses the following information on the beam and loading conditions:  
   - design compressive load applied on the member (in kN)
   - span of the member(in m)
   - young's modulus (in N/mm2 or MN/m2)
   - steel grade
   - member end connections (i.e. whether the member is pinned at both ends, fixed at both ends, pinned at one end (fixed at other end), etc)
   - nature of the loading on the web and flange(bending or compression) 

- This tool can be used by those with/without experience in Structural Engineering to perform quick design checks on the compression resistance of structural members

# Reference
I-Beam image: https://www.alcoengineering.co.uk/steel-universal-i-beams.html

# How to use the tool
- Open the file: 'compression_resistance.py'  
- Alter the variables as explained in the script
- Run the script 
- In the terminal there should be a detailed breakdown of: 
      1) The structural member(s) analysed; 
      2) The reasons for failure or success of the member(s); 
      3) The calculations behind the design procedure for the successful member

- the below gif is a demo of the tool:

![](https://github.com/favourumeh/compression_resistance/blob/main/GIF_demo.gif)


**Note: This tool uses tabular data from the TATA steel structural member pdf database. It was scraped using the [scraper](https://github.com/favourumeh/PDF-SCRAPE-TATA-STEEL-SECTION-TABLES) developed in an earlier project. The tabular data used for this project are the csv files 'Merged UKC' and 'Merged UKB'. The recommended structural member is the most efficient member (i.e. smallest cross-section size) from the aforementioned csv files that can safely withstand the specified compressive load according to standard design for steel members protocols(Eurocode 3).**





