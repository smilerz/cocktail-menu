import json

import requests


class TandoorAPI:
    def __init__(self, url, token, logger, **kwargs):
        self.logger = logger
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

    def get_paged_results(self, url, params):
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
                self.logger.info(f"Failed to fetch recipes. Status code: {response.status_code}")
                raise Exception(f"Failed to fetch recipes. Status code: {response.status_code}")
        return results

    def get_single_result(self, url, obj_id):
        url = f'{url}{obj_id}'
        self.logger.debug(f'Connecting to tandoor api at url: {url}')
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            self.logger.info(f"Failed to fetch recipes. Status code: {response.status_code}")
            raise Exception(f"Failed to fetch recipes. Status code: {response.status_code}")
        return json.loads(response.content)

    def get_recipes(self, params={}, filters=[]):
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
            # params={'filter':id}
            recipes = self.get_paged_results(url, params)
        for f in filters:
            recipes += self.get_paged_results(url, {'page_size': self.page_size, 'filter': f})

        self.logger.debug(f'Returning {len(recipes)} total recipes.')
        return recipes

    def get_recipe_details(self, recipe_id):
        """
        Fetch details of a specific recipe by its ID.
        Args:
            recipe_id (str): The ID of the recipe to retrieve.
        Returns:
            dict: Details of the recipe in JSON-LD format.
        """
        url = f"{self.base_url}/recipes/{recipe_id}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch recipe details. Status code: {response.status_code}")

    def get_keyword_tree(self, kw_id, params={}):
        """
        Fetch a keyword and it's descendants from the API.
        Returns:
            list: A list of keyword objects in tandoor format.
        """

        url = f"{self.url}keyword/"
        params['tree'] = kw_id
        params['page_size'] = 100
        keywords = self.get_paged_results(url, params)

        self.logger.debug(f'Returning {len(keywords)} total keywords.')
        return keywords

    def get_food_tree(self, food_id, params={}):
        """
        Fetch a food and it's descendants from the API.
        Returns:
            list: A list of food objects in tandoor format.
        """

        url = f"{self.url}food/"
        params['tree'] = food_id
        params['page_size'] = 100
        foods = self.get_paged_results(url, params)

        self.logger.debug(f'Returning {len(foods)} total food.')
        return foods

    def get_food(self, food_id, params={}):
        """
        Fetch a food and it's descendants from the API.
        Returns:
            list: A list of food objects in tandoor format.
        """

        url = f"{self.url}food/"
        food = self.get_single_result(url, food_id)

        self.logger.debug(f'Returning food {food["id"]}: {food["name"]}.')
        return food
