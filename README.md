# tandoor-menu-generator

Using your recipe data in Tandoor this menu generator will generate a menuy of X recipes with defined constraints.
- Optionally create Meal Plans on Tandoor
- Optionally inject Recipe name and ingredients into a file template for printing or browsing on the web

Criteria can include:
- food
- keywords
- ratings
- date created
- last cooked
-  and more.

See config.ini or run create_menu.py --help for configuration guidance.



## Installation
``pip install -r requirements.txt``

### Menu file installation requirements
Creating a menu file from template requires install libcairo and some additional python libraries
``sudo apt install libcairo2-dev``
``pip install -r pdf_requirements.txt``

