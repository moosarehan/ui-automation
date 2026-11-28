class SignIn:
    def __init__(self, page):
        self.page = page

    def submit(self, username, password):
        self.page.get_by_label("Username").fill(username)
        self.page.get_by_label("Password").fill(password)
        self.page.get_by_role("button", name="Sign in").click()


class Catalog:
    def __init__(self, page):
        self.page = page
        self.items = page.get_by_role("listitem")
        self.empty_message = page.get_by_text("No supplies match your search.")

    def search(self, term):
        self.page.get_by_label("Search products").fill(term)

    def reserve(self, product, student):
        self.page.get_by_label("Product", exact=True).select_option(label=product)
        self.page.get_by_label("Pickup name").fill(student)
        self.page.get_by_role("button", name="Reserve").click()

