from behave import given, when, then
from playwright.sync_api import expect
from framework import data


@given("the shop is open")
def open_shop(context):
    context.page.goto(context.base_url)


@when('I sign in with Excel account "{key}"')
def sign_in(context, key):
    account = data.excel(key)
    context.login.submit(account["username"], account["password"])


@given("I am a signed-in student")
def signed_in(context):
    open_shop(context)
    sign_in(context, "valid")
    expect(context.page.get_by_role("heading", name="Supply catalog")).to_be_visible()


@then('the status reads "{message}"')
def status(context, message):
    expect(context.page.get_by_role("status")).to_have_text(message)


@when('I search using database case "{key}"')
def search(context, key):
    context.case = data.database(key)
    context.catalog.search(context.case["term"])


@then("the catalog matches the stored result")
def results(context):
    expected = context.case["expected"]
    if expected:
        expect(context.catalog.items).to_have_text([expected])
    else:
        expect(context.catalog.items).to_have_count(0)
        expect(context.catalog.empty_message).to_be_visible()


@when('I reserve the Redis order "{key}"')
def reserve(context, key):
    context.order = data.reservation(key)
    context.catalog.reserve(**context.order)


@then("the reservation identifies the product and student")
def confirmation(context):
    status(context, "Reserved {product} for {student}".format(**context.order))

