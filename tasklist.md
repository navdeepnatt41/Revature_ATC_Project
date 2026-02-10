## Tasks

### Alembic
- Set up migrations

### Generators
For now, we're just going to hardcode data in the generatorse
- Aircraft
- Airline
- Airport
- Flight Crew
- Flight
- In Flight Employee <-- Ronald
- Route

For each entity:
    make a file "name_generator_service.py"
        have a method in the file called generate_nameOfEntity() -> list[Entity]

        USER LAYER
        ```
        @app.post("/generate")
        def generate_seed_books(
            book_svc: BookService = Depends(get_book_service),
            checkout_svc: CheckoutHistoryService = Depends(get_checkout_history_service),
        ):
            books, checkout_histories = generate()
            book_svc.add_seed_records(books)
            checkout_svc.add_seed_records(checkout_histories)
            return "Books were added to DB......"
        ```
        ->
        SERVICE
        ```
        def add_seed_records(self, books: list[Book]) -> None:
                self.repo.add_seed_records(books)
        ```
        REPO ->
        ```
        def add_seed_records(self, books: list[Book]) -> None:
                for b in books:
                    self.session.add(b) <-- function to add to db

                self.session.commit()
```
### Pydantic
- Whatever pydantic is supposed to do

### Docker
- Make sure we can create an image for the application and get it to talking a Postgres container
    - Finalize Dockerfile
    - Finalize docker-compose.yml

### Endpoints
- Setup endpoints
