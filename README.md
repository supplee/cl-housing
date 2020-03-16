# cl-housing

This is a flexible, predictive modeler of the craigslist rental market of your choosing coded in python using.  It will soon be expanded to take data from other sources as well.  The modeler scrapes posts from the craigslist market of your choosing, and then creates and updates a regression to assess how "fair" the pricing is by comparing the difference between actual rent and expected rent.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project is designed for use in python and IP (Interactive Python) based on Python 3.6 or later.

In addition, it makes use of the following modules:

```
getLivedata.py -- scrapes data from craigslist and fills in missing information by crawling through each post as needed.
argparse
bs4.BeautifulSoup
h5py
pandas
random
re
requests.get
sys
```

In addition to the above modules, the Jupyter notebook requires some additional modules:
```
clean-data.ipynb -- notebook that cleans the data, visualizes it, and fits a multivariate linear model from the data.
scipy
statsmodels
sklearn
```


### Installing

1. Clone or download the repository onto your local system. 

2. Ensure you have python3 installed

```
python --version
```
If the above command shows python v2.x, try:
```
python3 --version
```
3. Open a command line prompt -- this script allows you to chose your own craigslist neighborhood for modeling!  This is easiest to do if you run the script that scrapes data from the command line, so you can specify your options.

```
./getLivedata.py -h
```

## Running getLivedata.py to get a complete table of data

TBA

## Versioning

This product is currently a technical demo, and is pre-release.

## Authors

* **William Supplee, MD** - *Initial release* 

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to Justin Sempyer at Medium whose work using craigslist with beautifulsoup inspired this project.

