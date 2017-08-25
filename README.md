# Retail products classifier

This project helps classify retail products into categories. Although in this example the categories are structured in a hierarchy, to keep it simple I considered all subcategories as top-level.
The main packages used in this projects are: [sklearn](http://scikit-learn.org), [nltk](http://www.nltk.org) and [dataset](https://dataset.readthedocs.io/en/latest/).

You can read the post explaining this project [here](https://joaorafaelm.github.io/blog/text-classification-with-python).

**You will need Python3+ to use this project.**

## Installation
### 1. Download
Now, you need the *text-classification-python* project files in your workspace:
```bash
$ git clone https://github.com/joaorafaelm/text-classification-python;
$ cd text-classification-python;
```
### 2. Virtualenv (Optional)
You should already know what is [virtualenv](http://www.virtualenv.org/) at this stage. So, simply create it for the project:
```bash
$ virtualenv venv;
$ source venv/bin/activate;
```
### 3. Requirements
You will find the *requirements.txt*. To install them, simply type:
```bash
$ pip install -r requirements.txt
```

#### Running the scraper
To run the scraper you will need a csv of ASINS (amazons product identifier). Just search the webz for it. And then run:
```bash
python amazon_scrape.py
```
All data will be saved into sqlite (file database.db), table *products*.

#### Dump the database
```bash
datafreeze .datafreeze.yaml
```
This will create a json file under the directory dumps/.

#### Data preparation
```bash
python data_prep.py
```
The script will create a new file called **products.json** at the root of the project, and print out the category tree structure. Change the value of the variables `default_depth`, `min_samples` and `domain` if you need more data.

### Classify and get prediction results.
```bash
python classify.py
```