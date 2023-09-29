# tandoor-menu-generator

Using your recipe data in Tandoor this menu generator will generate a menuy of X recipes with defined constraints.

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


## Coming Soon
- Inject Recipe Name and Ingredients into SVG template
