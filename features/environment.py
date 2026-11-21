import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import allure
from playwright.sync_api import sync_playwright
from framework.pages import Catalog, SignIn


def before_all(context):
    context.base_url = os.getenv("BASE_URL")
    if not context.base_url:
        directory = Path(__file__).resolve().parents[1] / "app"
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=directory))
        Thread(target=server.serve_forever, daemon=True).start()
        context.add_cleanup(server.server_close)
        context.add_cleanup(server.shutdown)
        context.base_url = f"http://127.0.0.1:{server.server_port}"
    engine = os.getenv("BROWSER", "chromium")
    if engine not in {"chromium", "firefox", "webkit"}:
        raise ValueError(f"Unknown browser: {engine}")
    runtime = sync_playwright().start()
    context.add_cleanup(runtime.stop)
    context.browser = getattr(runtime, engine).launch(headless=os.getenv("HEADED") != "1")
    context.add_cleanup(context.browser.close)


def before_scenario(context, scenario):
    session = context.browser.new_context()
    context.add_cleanup(session.close)
    context.page = session.new_page()
    context.events = []
    context.page.on("console", lambda message: context.events.append(message.type + ": " + message.text))
    context.page.on("pageerror", lambda error: context.events.append(str(error)))
    context.login = SignIn(context.page)
    context.catalog = Catalog(context.page)


def after_step(context, step):
    context.events.append(f"{step.status.name}: {step.name}")
    if step.status.name == "failed":
        allure.attach(context.page.screenshot(), "Failure screenshot", allure.attachment_type.PNG)


def after_scenario(context, scenario):
    allure.attach("\n".join(context.events), "Execution log", allure.attachment_type.TEXT)

