# Installation and usage

The project has been implemented and tested for Ubuntu(22.04)/Debian and python
3.9 and 3.10. To install all dependencies and packages, use the following
instructions:

## Using the python files locally 

All important files to run this project without docker are within the `src/`
folder.

```bash
$ git clone git@github.com:0815IDIOT/Conrad_Electronic_SE.git
$ cd conrad_electronic_se/src
$ chmod +x ./install.sh
$ ./install.sh
```
### Running as REST API with FastAPI/uvicorn

```bash
$ source venv/bin/activate
$ cd src/
$ uvicorn recommendation_api:app --reload
```

Your REST API is now available under `localhost:8000`. The possible endpoints
are:

- `GET /stock_items/{stock_id}/recommendations/bundle`
    - Receiving the `20` most bought items to the stock with id `stock_id`. 
- `GET /stock_items/{stock_id}/recommendations/price`
    - Receiving a price recommendation for the stock with the id `stock_id`. 

### Running as pure python

```bash
$ source venv/bin/activate
$ cd src/
```

Create your python file and import and create an object of the the
`Databace_connector` class from the
[databace_connector.py](src/databace_connector.py) file. The object has the
following functions:

`load_raw_data(data_path, split_training = 70)`: This function loads the local
raw csv-file downloadable from Kaggle
([link](https://www.kaggle.com/datasets/carrie1/ecommerce-data)) into the
database.
- `data_path` is a string to the .csv file within the `src/data/`
  folder.
- `split_training` represents the percentage used for the training data. 

`calc_regression(force = False)`: This function will calculate the number of times
each bundle has been bought. Note that this function can take some time. 
- If `force` is set to **false**, and the regression table `bought_together`
  already holds data, the functions ask permission to delete the data,
  before inserting new ones.

`get_recommanded_product(stock_id, limit = 20)`: This function calculates the
percentage at which a second product is bought together with the product of
`stock_id`. The top 'limit' products are returned.
- `stock_id` is the stock ID of the items you want to get recommendations for.
- `limit` defines the number of recommendations you will maximally get. 

`get_recommanded_price(stock_id)`: Recommends a unit price for a product,
depending on the historic mean sales price. It remains to be discussed whether
this is sufficient; see the Q&A below.
- `stock_id` is the stock ID of the items for which you want to get a recommended
  price.

Here is an example file with all the functions described above:

```python
from databace_connector import Database_connector 

db_path = "resources/data.db"
data_path = "data/data.csv"

dbc = Database_connector(db_path, dataset_type = "training")

dbc.load_raw_data(data_path)
dbc.calc_regression()
dbc.get_recommanded_product(stock_id = "22865")
dbc.get_recommanded_price(stock_id = "22865")
```

## Docker

Start by installing the docker packages
([link](https://docs.docker.com/engine/install/ubuntu/)). Following this, you
create the container with the following command:

```bash
$ sudo docker build -t conrad_image .
```

Now run the following command to have an docker which act as a REST API
listening on port `8000`:

```bash
$ sudo docker run -d --name conrad_api -p 8000:80 conrad_image
```

***

# Q&A
## 1 Describe any reasoning behind your solution.
I used a statistical approach for the recommendation algorithm. In my
experience, statistical models produce excellent results with a relatively low
complexity. However, before applying the statistical model, I have to
organize my data, which will help me in the long term find more interesting
relations and expand my data set in the future. Therefore, I created a table for
the following entities: customer, invoice, stock item, and a n:m relation for
stock items to invoices.

For performance reasons of the REST API, I decided to save some results later
needed for the regression in a new DB table (`bought_together`). This table
holds the amount of two **distinct** stock items that appear within one invoice.
Based on this, my approach for the regression model is to calculate the
probability at which two items are bought together: P(item_a|item_b) = P(item_a
and item_b) / P(item_b).

Further, when someone wants
the recommended stock items of the model for one stock item `A`, the model
divides the number of each stock item `B` bought with item `A` through the
number of times the item `A` was bought. The resulting list is ordered by the
percentage.

I used a `0` as the placeholder if a customer ID is missing. Further, I escaped
all " and ' characters within the item descriptions.

It appears that one stock item can have different unit prices. I speculate that
this might be due to coupons or special sale offers. Since I do not have any
specific information about the reason, I included the unit price within the
`shopping_lists` table and not the `stocks` table.

**Attenchent**: I see this project as a prototype. As such, I did not use any
ORM for the DB connection. If this project should be used in production, one
should use an ORM e.g. SQLAlchemy, to prevent SQL injections and make the code
scalable by using connection pooling. Further, in production, it would also be
better to use a special python package for logging instead of the print
function.

## What other splitting criteria would you choose if you could gather more features/data?
I would use a test, validation, and training dataset. 

## Discuss the size of the output list and how it can be decided per product
Indeed, the output list can get very long for an increasing amount of data
points (sales). However, a website can only suggest a few items
without compromising the usability and the positive user experience.
Therefore, I suggest only taking the top x recommended products, which can be
displayed on the web page or for the specific use case.

## Discuss/implement any price computation per bundle e.g. the sum of products’ prices.
I have noted that stock items can have different unit prices, which, for
example, might depend on certain seasonal sales offers or coupons. It is very
difficult to compute an accurate price without understanding which criteria
influence the price. Therefore, my program returns the bundle's historical
maximal and minimal cost computed from the individual ranges of each item.

However, with a larger dataset, one could analyze whether there are any
correlations between two stock items being bought more often together if their
bundle has a lower price. Note that there might be specific effects that are
independent of the bundle itself. For example, I would expect every bundle will
be bought more if their price is decreased drastically, independent of whether
customers typically buy these two items together.

## Is the provided data sufficient to predict the price? What other data would you like to gather to improve your solution?
For me, it is unclear what the customer wants the price related to for the
regression model. One could make a regression based on the amount any arbitrary
item was bought for a certain price. I would expect that the lower the cost of
an item, the more often it is bought. However, estimating the prices based on
this information in the future could lead to a self-fulfilling prophecy and
down-spiraling prices of our products.

Therefore, I would instead calculate the optimal price of a single product on
the frequency with which his item was bought for different prices. However, for
this, I need more information e.g. in what exact time frames the price of the
article was. Further, I expect the frequency to be the highest right after a
sale offer and decline exponentially over time. Thus, one needs to think about
the expected long-term buy frequency. Note that one should also know the
product-specific profit margin to avoid selling an item with a loss.

Therefore, my current price estimation is based on the average unit price of an
item. I know this is not optimal. However, I miss the data for a more
sophisticated model.

## How would you evaluate the business impact of the solution and share the outcome with the internal stakeholders?
I would start to argue with studies that have shown that recommending items
increases the sales for a company. Assuming that the company does not yet have
an item recommendation algorithm, I would further highlight the ratio of
investing a relatively small amount of time and resources with my solution
compared to the significant increase in sales. If the company already has an
item recommendation algorithm, I would showcase the benefits or potential
synergies of using my solution. Following these arguments, I would suggest that
my project is worth trying in an A/B user test to further evaluate the sales
impact for our customers. 


















