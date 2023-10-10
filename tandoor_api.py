import json

import requests

from utils import TQDM, cached, display_progress


class TandoorAPI:
    progress = None

    def __init__(self, url, token, logger, **kwargs):
        self.logger = logger
        if self.logger.loglevel != 10:
            self.progress = TQDM(total=100)
        self.ttl = kwargs.get('cache', 240)
        self.token = token
        self.page_size = kwargs.get('page_size', 100)
        self.include_children = kwargs.get('include_children', True)
        if url and url[-1] == '/':
            self.url = f"{url}api/"
        else:
            self.url = f"{url}/api/"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def update_progress(self):
        if self.progress:
            self.progress.update_step()

    @display_progress
    @cached
    def get_paged_results(self, url, params, **kwargs):
        results = []
        while url:
            self.logger.debug(f'Connecting to tandoor api at url: {url}')
            self.logger.debug(f'Connecting with params: {str(params)}')
            if '?' in url:
                params = None
            response = requests.get(url, headers=self.headers, params=params)
            content = json.loads(response.content)
            new_results = content.get('results', [])
            self.logger.debug(f'Retrieved {len(new_results)} results.')
            results = results + new_results
            url = content.get('next', None)

            if response.status_code != 200:
                self.logger.info(f"Failed to fetch recipes. Status code: {response.status_code}: {response.text}")
                raise Exception(f"Failed to fetch recipes. Status code: {response.status_code}: {response.text}")
        return results

    @display_progress
    @cached
    def get_unpaged_results(self, url, obj_id, **kwargs):
        url = f'{url}{obj_id}'
        self.logger.debug(f'Connecting to tandoor api at url: {url}')
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            self.logger.info(f"Failed to fetch recipes. Status code: {response.status_code}: {response.text}")
            raise Exception(f"Failed to fetch recipes. Status code: {response.status_code}: {response.text}")
        return json.loads(response.content)

    def create_object(self, url, data, **kwargs):
        self.logger.debug(f'Create object with tandoor api at url: {url}')
        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 201:
            return response.json()
        else:
            self.logger.info(f'Error creating object: {response.text}')
            raise RuntimeError(f'Error creating object: {response.text}')

    def delete_object(self, url, obj_id, **kwargs):
        self.logger.debug(f'Deleteing object with tandoor api at url: {url}')
        response = requests.delete(f'{url}{obj_id}', headers=self.headers)

        if response.status_code != 204:
            self.logger.info(f'Error deleting object: {response.text}')
            raise RuntimeError(f'Error deleting object: {response.text}')

    def get_recipes(self, params={}, filters=[], **kwargs):
        """
        Fetch a list of recipes from the API.
        Returns:
            list: A list of recipe objects in tandoor recipe format.
        """
        url = f"{self.url}recipe/"
        recipes = []
        if params:
            params['include_children'] = self.include_children
            params['page_size'] = self.page_size
            recipes = self.get_paged_results(url, params, **kwargs)

        if not isinstance(filters, list):
            filters = [filters]
        for f in filters:
            recipes += self.get_paged_results(url, {'page_size': self.page_size, 'filter': f})

        self.logger.debug(f'Returning {len(recipes)} total recipes.')
        return recipes

    @display_progress
    @cached
    def get_recipe_details(self, recipe_id):
        """
        Fetch details of a specific recipe by its ID.
        Args:
            recipe_id (str): The ID of the recipe to retrieve.
        Returns:
            dict: Details of the recipe in JSON-LD format.
        """
        url = f"{self.url}recipe/{recipe_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch recipe details. Status code: {response.status_code}: {response.text}")

    def get_keyword_tree(self, kw_id, params={}, **kwargs):
        """
        Fetch a keyword and it's descendants from the API.
        Returns:
            list: A list of keyword objects in tandoor format.
        """

        url = f"{self.url}keyword/"
        params['tree'] = kw_id
        params['page_size'] = 100
        keywords = self.get_paged_results(url, params, **kwargs)

        self.logger.debug(f'Returning {len(keywords)} total keywords.')
        return keywords

    def get_food_tree(self, food_id, params={}, **kwargs):
        """
        Fetch a food and it's descendants from the API.
        Returns:
            list: A list of food objects in tandoor format.
        """

        url = f"{self.url}food/"
        params['tree'] = food_id
        params['page_size'] = 100
        foods = self.get_paged_results(url, params, **kwargs)

        self.logger.debug(f'Returning {len(foods)} total food.')
        return foods

    def get_food(self, food_id, params={}, **kwargs):
        """
        Fetch a food and it's descendants from the API.
        Returns:
            list: A list of food objects in tandoor format.
        """

        url = f"{self.url}food/"
        food = self.get_unpaged_results(url, food_id, **kwargs)

        self.logger.debug(f'Returning food {food["id"]}: {food["name"]}.')
        return food

    def get_book(self, book_id, params={}, **kwargs):
        """
        Fetch a book from the API.
        Returns:
            obj: A book object in tandoor format.
        """

        url = f"{self.url}recipe-book/"
        book = self.get_unpaged_results(url, book_id, **kwargs)

        self.logger.debug(f'Returning book {book["id"]}: {book["name"]}.')
        return book

    def get_book_recipes(self, book, params={}, **kwargs):
        """
        Fetch all recipes in a book from the API.
        Returns:
            list: List of book contents.
        """

        url = f"{self.url}recipe-book-entry/?book={book.id}"
        book_entries = self.get_unpaged_results(url, '', **kwargs)
        recipes = [be['recipe_content'] for be in book_entries]
        if book.filter:
            recipes += self.get_recipes(filters=book.filter)

        self.logger.debug(f'Returning book {book.id}: {book.name} with {len(recipes)} recipes.')
        return recipes

    def create_meal_plan(self, recipe=None, title=None, servings=1, date=None, note=None, type=None, **kwargs):
        url = f"{self.url}meal-plan/"
        plan = self.create_object(
            url,
            {
                'title': title,
                'recipe': {
                    'id': recipe.id,
                    'name': recipe.name,
                    'keywords': []
                },
                'servings': servings,
                'note': note,
                'from_date': date.strftime('%Y-%m-%d'),
                'to_date': date.strftime('%Y-%m-%d'),
                'meal_type': self.get_unpaged_results(f'{self.url}meal-type/', type)
            }
        )

        self.logger.debug(f'Succesfully created meal plan {plan["id"]}: {title} with type {type}')

        return plan

    def get_meal_plans(self, date, **kwargs):
        url = f"{self.url}meal-plan/?from_date={date.strftime('%Y-%m-%d')}"
        return self.get_unpaged_results(url, '', **kwargs)

    def delete_meal_plan(self, obj_id, **kwargs):
        url = f"{self.url}meal-plan/"
        self.delete_object(url, obj_id)
        self.logger.debug(f'Succesfully deleted meal plan {obj_id}.')

    @display_progress
    @cached
    def get_food_substitutes(self, id, substitute):
        url = f"{self.url}{substitute}/{id}/substitutes/"
        self.logger.debug(f'Connecting to tandoor api at url: {url}')
        response = requests.get(url, headers=self.headers, params={'onhand': 1})

        if response.status_code != 200:
            self.logger.info(f"Failed to fetch food substitutes. Status code: {response.status_code}: {response.text}")
            raise Exception(f"Failed to fetch food substitutes. Status code: {response.status_code}: {response.text}")
        return json.loads(response.content)
