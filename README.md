# alfred-CensusQuickRef
An [Alfred](https://www.alfredapp.com/) Workflow to query and make calculations on demographic data, with a function to calculate carriers if odds ratio, disease, and minor allele frequency are provided. 


<a href="https://github.com/giovannicoppola/alfred-CensusQuickRef/releases/latest/">
<img alt="Downloads"
src="https://img.shields.io/github/downloads/giovannicoppola/alfred-CensusQuickRef/total?color=purple&label=Downloads"><br/>
</a>

![](images/alfred-censusquickref.gif)

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Motivation](#motivation)
- [Setting up](#setting-up)
- [Basic Usage](#usage)
- [Known Issues](#known-issues)
- [Acknowledgments](#acknowledgments)
- [Changelog](#changelog)
- [Feedback](#feedback)

<!-- /MarkdownTOC -->


<h1 id="motivation">Motivation ✅</h1>

- Being able to quickly answer questions like: 
	- *how many people between xx and xx years of age live in [US/World/Europe/this-country]*
	- *if a disease has a prevalence of 3:100,000 how many cases are there in [US/US state/World/Europe/this-country]*
	- *if a risk factor has OR = 2, and a frequency y, how many carrier cases and controls can we expect for a disease with prevalence x?*




<h1 id="setting-up">Setting up ⚙️</h1>

### Needed
- [Alfred 5](https://www.alfredapp.com/) with Powerpack license


<h1 id="usage">Basic Usage 📖</h1>

- Launch with keyword (default: `!p`) or hotkey.
- Enter characters below to subset the total population based on %, age, sex, US state, ancestry. 
- ↩️ will copy the current row to clipboard 
- ^↩️ will copy the current row to clipboard and paste to frontmost application
- ⌘↩️ will copy entire output to clipboard and paste to frontmost application

## Subsets 🔣 (World regions, or individual country)

### Slice 🍰
- `%` percent of the population
- `1:` frequency per 100,000

### Age 🧙
- `nn` exact age
- `nn+` some age and above
- `nn-` some age and below
- `nn-nn` some age range


## Other criteria (🇺🇸 only)
### Sex ♂️♀️ 
- `M` male
- `F` female


### US state 🇺🇸
- `XX` US state abbreviation

### Ancestry 👤
- `EUR` European
- `AMR` American Indian
- `AAA` African-American
- `ASI` Asian

- `H` Hispanic (can be alone or added to any of the above)


## Calculating the number of expected carriers 🧮
- `ORxx` OR (Odds Ratio) followed by a number
- `MAFxx` MAF (Minor allele frequency), followed by a number
- `DISxx` Disease frequency, followed by a number
- Note: `OR`, `MAF`, and `DIS` are case-sensitive


<h1 id="known-issues">Limitations & known issues ⚠️</h1>

- None for now, but I have not done extensive testing, let me know if you see anything!
- The carrier estimate is just a rough estimate and makes a number of assumptions and approximations.



<h1 id="acknowledgments">Acknowledgments 😀</h1>

### Icons: 
- [Main icon](https://www.flaticon.com/free-icon/census_8709706) created by noomtah – Flaticon
- [European Union] (https://www.flaticon.com/free-icon/european_4628667)
- [Africa](https://thenounproject.com/icon/africa-146421/)
- [flags](https://flagpedia.net)

### Data Files:
- US records from [CDC](https://www.cdc.gov/nchs/nvss/bridged_race/data_documentation.htm#vintage2020)
- [world population](https://population.un.org/wpp/Download/Standard/Population/)
- [counties fips](https://github.com/kjhealy/fips-codes/blob/master/county_fips_master.csv) 




	
<h1 id="changelog">Changelog 🧰</h1>

- 05-19-2023: version 0.1


<h1 id="feedback">Feedback 🧐</h1>

Feedback welcome! If you notice a bug, or have ideas for new features, please feel free to get in touch either here, or on the [Alfred](https://www.alfredforum.com) forum. 
