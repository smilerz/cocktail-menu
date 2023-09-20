import requests


class TandoorAPI:
    def __init__(self, url, token):

        self.token = token
        if url and url[-1]=='/':
            self.url = url
        else:
            self.url = f"{url}/"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def get_recipe_list(self):
        """
        Fetch a list of recipes from the API.
        Returns:
            list: A list of recipe objects in JSON-LD format.
        """
        url = f"{self.url}/recipes"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch recipes. Status code: {response.status_code}")

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

    def search_recipes(self, query):
        """
        Search for recipes based on a query string.
        Args:
            query (str): The search query.
        Returns:
            list: A list of recipe objects matching the query in JSON-LD format.
        """
        url = f"{self.base_url}/recipes/search"
        params = {'q': query}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Recipe search failed. Status code: {response.status_code}")

    # You can add more methods for creating, updating, or deleting recipes as needed.

