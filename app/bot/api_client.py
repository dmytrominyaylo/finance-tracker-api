import httpx

from app.core.config import settings


class APIClient:
    def __init__(self):
        self.base_url = f"http://localhost:{settings.PORT}{settings.API_PREFIX}"

    async def login(self, email: str, password: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                params={"email": email, "password": password},
            )

            if response.status_code == 200:
                return response.json()

            return None

    async def get_me(self, token: str, user_id: int) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                return response.json()

            return None

    async def get_categories(self, token: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/categories/",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                return response.json()

            return None

    async def create_category(self, token: str, name: str) -> tuple[dict | None, int]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/categories/",
                headers={"Authorization": f"Bearer {token}"},
                json={"name": name},
            )

            if response.status_code == 201:
                return response.json(), response.status_code

            return None, response.status_code

    async def get_transactions(self, token: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/transactions/",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                return response.json()

            return None

    async def create_transaction(
        self,
        token: str,
        category_id: int,
        amount: float,
        transaction_type: str,
        description: str,
        transaction_date: str,
    ) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transactions/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "category_id": category_id,
                    "amount": amount,
                    "type": transaction_type,
                    "description": description,
                    "transaction_date": transaction_date,
                },
            )

            if response.status_code == 201:
                return response.json()

            return None

    async def get_budgets(self, token: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/budgets/",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                return response.json()

            return None

    async def create_budget(
        self,
        token: str,
        category_id: int,
        limit_amount: float,
        period: str,
        month: str,
    ) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/budgets/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "category_id": category_id,
                    "limit_amount": limit_amount,
                    "period": period,
                    "month": month,
                },
            )

            if response.status_code == 201:
                return response.json()

            return None

    async def delete_transaction(
        self,
        token: str,
        transaction_id: int
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/transactions/{transaction_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            return response.status_code == 204

    async def delete_budget(
        self,
        token: str,
        budget_id: int
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/budgets/{budget_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            return response.status_code == 204

    async def delete_category(
        self,
        token: str,
        category_id: int
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/categories/{category_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            return response.status_code == 204

    async def update_email(
        self,
        token: str,
        user_id: int,
        email: str
    ) -> tuple[dict | None, int]:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"email": email},
            )

            if response.status_code == 200:
                return response.json(), response.status_code

            return None, response.status_code

    async def update_password(
        self,
        token: str,
        user_id: int,
        password: str
    ) -> dict | None:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"password": password},
            )

            if response.status_code == 200:
                return response.json()

            return None

    async def register(
        self,
        email: str,
        password: str
    ) -> tuple[dict | None, int]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/users/",
                json={"email": email, "password": password},
            )

            if response.status_code == 201:
                return response.json(), response.status_code

            return None, response.status_code

    async def delete_account(
        self,
        token: str,
        user_id: int
    ) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            return response.status_code == 204


api_client = APIClient()
