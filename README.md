# Installation

The project has been implemented and tested for Ubuntu/Debian. To install all dependcys and pageces use the following instruction:

## Ubuntu/Debian

``` bash
$ git clone 
$ cd 
$ chmod +x ./install.sh
$ ./install.sh
```

## Docker

Start by installing the docker pakeges.

```bash
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install docker

```

# Usage



# Q&A
## 1 Describe any reasoning behind your solution.
I used a statistical approach for the recommandation algorithm. In my experiences, statistical models producing very good result with a relativ low complexity. However, before applying the statistical approach, I have to organize my data, which will help me in a long term finding more interesting relations and expand my data set in the futur. Therefore, I create a Table for the following enitys: customer, invoice, stock item, and a n:m relation for stock items to invoices.

My approach for the regression model is to calculate the percentage at which two items are bought together. Therefore, I created a new table '', in which I count the number of time two **distinct** stock items appear within one invoice. Note, that in order to save memmory and avoid duplicated informatons, I only save the `(stock_item_a, stock_item_b)` pair and not the `(stock_item_b, stock_item_a)` pair, according to the inbuild `sort()` function of python strings.

Further, when someone want the recommended stock items of the model for one stock item `A`, the model divides the number of each stock item `B` bough with the `A` trough the number of time the item `A` was bought. The resulting list is order desc by the percentage.

Note, that if a customer id is missing, I used a `0` as placeholer. Further, I escaped all " and ' characters within the item discriptions. 

## What other splitting criteria would you choose if you could gather more features/data?
I would use a test-, validation- and training-dataset for my model. 

## Discuss the size of the output list and how it can be decided per product
Indeed, tha output list can get very long for an increasing data set length. However, a webside can only suggest a small numbers of items without compromosing the useabillity and the positive user experience. Therefore, I suggest to only take the top x recommended products, which can be displayed on the web page or for the specific use case.

## Discuss/implement any price computation per bundle e.g. the sum of products’ prices.
I have noted, that stock items can have different unit prices, which, for example, might depend on certain seassonal sales offers. Without understanding, which criteria influence the price, it is very difficult to compute a accurate price.

However, with a larger dataset, one could analyse whether there are any correlations between two stock items beeing bought, if their bundle has a cheaper price. Note, that there might a certain effects, which are indepent of the bundle itself e.g. I would expect every bundle will be bought more, if their price is decreased drastically, indepent whether customers typically buy theese two items together.

## How would you evaluate the business impact of the solution and share the outcome with the internal stakeholders?
Studys of ... and ... have shown, that an recommending items can increase the sales for a company. Comparing the relative small time and resourcen investment to a potentially large increase in sales. Therefore, I would argue that my solution is worth to try in a A/B user test to further evaluate the sale impact for our customers. 


















